#!/usr/bin/env python3

import os
import re
import h5py
import time
import uuid
import glob
import numpy as np
import pandas as pd
import SharedArray as sa
import PIL.Image as Image
import multiprocessing as mp
import matplotlib.pyplot as plt

from tqdm import tqdm
from .read_tiff import read_tif_volume
from .calibration import Calibration
from .io import get_file_list
from .._version import __version__

class Scan:
    """
    Scan class that handles scanning operations, including data calibration,
    statistical analysis, and plotting of diffractogram.
    """
    def __init__(self,
                 initial_angle: float,
                 final_angle: float,
                 size_step: float,
                 number_of_steps: int,
                 xc: int,
                 yc: int,
                 output_folder: str,
                 scan_folder: str,
                 scan_filename: str,
                 ny: int,
                 detector_size_x: int,
                 input_mythen_lids: np.ndarray,
                 calibration_pixel: np.ndarray):
        """
        Initializes the Scan class with the given parameters.

        Args:
            initial_angle (float): Initial angle for the scan.
            final_angle (float): Final angle for the scan.
            size_step (float): Step size for each scan increment.
            number_of_steps (int): Number of steps in the scan.
            pixel_theta (np.ndarray): Pixel theta values.
            xc (int): X-coordinate of the center.
            yc (int): Y-coordinate of the center.
            output_folder (str): Path to the output folder.
            scan_folder (str): Path to the scan folder.
            scan_filename (str): Filename of the scan file.
            ny (int): Number of y pixels.
            detector_size_x (int): Size of the detector in x-dimension.
        """
        self.initial_angle   = initial_angle
        self.final_angle     = final_angle
        self.size_step       = size_step
        self.number_of_steps = number_of_steps
        self.output_folder   = output_folder
        self.scan_folder     = scan_folder
        self.scan_filename   = scan_filename
        self.det_x           = detector_size_x
        self.xmin            = xc - 1
        self.xmax            = xc + 0
        self.ymin            = yc - int(ny / 2) + 1
        self.ymax            = yc + int(ny / 2)
        self.input_mythen_lids = input_mythen_lids
        self.calibration_pixel = calibration_pixel

    def get_volume(self) -> np.ndarray:
        """Reads a series of TIFF files into a 3D NumPy array (volume).

        This method first constructs a list of TIFF file paths based on the scan
        parameters. It then reads the files into a NumPy array, storing the result
        in the `self.volume` attribute.

        Returns:
            np.ndarray: A 3D NumPy array of the measured diffraction 2D images.

        Raises:
            FileNotFoundError: If any of the expected TIFF files are not found.
            ValueError: If there are issues reading the TIFF data.
        """

        self.list_of_files = get_file_list(self.number_of_steps, self.number_of_steps, self.initial_angle,
                                          self.final_angle, self.scan_folder, self.scan_filename)

        params = [self.number_of_steps, self.ymax, self.ymin, self.det_x, self.list_of_files]

        self.volume = read_tif_volume(params)

        return self.volume


    def estatistics(self, mythen, croped_mythen, mythen_lids) -> tuple:
        """
        Performs statistical analysis on the scanned data.

        Args:
            mythen (np.ndarray): Array of mythen data.
            croped_mythen (np.ndarray): Cropped mythen data.
            mythen_lids (list): List of mythen lids.
            tth (np.ndarray): Two-theta values.

        Returns:
            tuple: Summed intensity, mean, and standard deviation of the intensities.
        """
        # Define the nominal two theta measured
        tth = self.initial_angle + (self.size_step / 2) + np.arange(self.number_of_steps, dtype=np.float32) * self.size_step
        # Round to 4 or 5 values
        tth = np.round(tth, 3)
        print(f'tth: {tth}')

        # Perform the theta to pixel mapping using the calibration_pixel vector as input calculated in the `Calibration` class
        pixel_address = get_pixel_address(self.calibration_pixel, tth, self.number_of_steps)
        # Round pixel_address values?
        pixel_address = np.round(pixel_address[:, mythen_lids[0]:mythen_lids[1]], 3)
        print(f'pixel address: {pixel_address}')

        flat_pixel_address = pixel_address.flatten()
        flat_croped_mythen = croped_mythen.flatten()

        det_start = np.round(min(flat_pixel_address), 3)
        det_end   = np.round(max(flat_pixel_address), 3)
        print(f'det_start: {det_start:.3f}\ndet_end: {det_end:.3f}')

        # Calculate the histogram
        begin_bin_value = np.round(det_start - self.size_step / 2, 3)
        end_bin_value = np.round(det_end + self.size_step, 3)

        print(f'value_0: {det_start - self.size_step / 2}')
        print(f'value_1: {det_end + self.size_step}')
        print(f'value_2: {self.size_step}')

        bins = np.arange(begin_bin_value, end_bin_value, self.size_step, dtype=float)
        #bins    = np.arange(det_start - self.size_step / 2, det_end + self.size_step, self.size_step, dtype=float)
        hist, _ = np.histogram(flat_pixel_address, bins=bins)

        print(f'bins: {bins}')
        print(f'histogram: {hist}')

        histogram_size = len(hist)
        number_of_output_parameters = 4

        direct_beam = np.zeros([histogram_size, number_of_output_parameters], dtype=np.float32)

        for index in range(len(hist)):
            min_       = bins[index]
            max_       = bins[index + 1]
            tth_       = min_
            tth_index  = np.where(np.logical_and(flat_pixel_address >= min_, flat_pixel_address <= max_))[0]
            int_       = np.sum(flat_croped_mythen[tth_index])
            mean_      = np.mean(flat_croped_mythen[tth_index])
            std_       = np.std(flat_croped_mythen[tth_index])

            direct_beam[index] = [tth_, int_, mean_, std_]

        # Add verification if path exists. If doesn't create the path and continue the processing and add log messages
        diffractogram_file_path = "".join([self.output_folder, self.scan_filename, 'proc.h5'])
        with h5py.File(diffractogram_file_path, "w") as h5f:
            h5f.create_group("proc")
            h5f.create_dataset('proc/tth', data=direct_beam[:,0], dtype=np.float32)
            h5f.create_dataset('proc/intensities', data=direct_beam[:,1], dtype=np.float32)
            h5f.create_dataset('proc/mean', data=direct_beam[:,2], dtype=np.float32)
            h5f.create_dataset('proc/standard_deviation', data=direct_beam[:,3], dtype=np.float32)

            h5f.create_group("metadata")
            h5f.create_dataset('metadata/initial_angle', data = self.initial_angle, dtype=np.float32)
            h5f.create_dataset('metadata/final_angle', data = self.final_angle, dtype=np.float32)
            h5f.create_dataset('metadata/size_step', data = self.size_step, dtype=np.float32)
            h5f.create_dataset('metadata/number_of_steps', data = self.number_of_steps, dtype=np.float32)
            h5f.create_dataset('metadata/output_folder', data = self.output_folder)
            h5f.create_dataset('metadata/scan_folder', data = self.scan_folder)
            h5f.create_dataset('metadata/scan_filename', data = self.scan_filename)
            h5f.create_dataset('metadata/det_x', data = self.det_x, dtype=np.float32)
            h5f.create_dataset('metadata/xmin', data = self.xmin, dtype=np.float32)
            h5f.create_dataset('metadata/xmax', data = self.xmax, dtype=np.float32)
            h5f.create_dataset('metadata/ymin', data = self.ymin, dtype=np.float32)
            h5f.create_dataset('metadata/ymax', data = self.ymax, dtype=np.float32)
            h5f.create_dataset('metadata/input_mythen_lids', data = self.input_mythen_lids, dtype=np.float32)
            h5f.create_dataset('metadata/calibration_pixel', data = self.calibration_pixel, dtype=np.float32)
            h5f.create_dataset('metadata/pixel_address', data = pixel_address, dtype=np.float32)
            h5f.create_dataset('metadata/datetime', data = time.strftime("%Y/%m/%d - %H:%M:%S"))
            h5f.create_dataset('metadata/software_version', data = __version__[:5])


        return direct_beam[:,0], direct_beam[:,1], direct_beam[:,2], direct_beam[:3]

    def scan_main_run(self) -> tuple:
        """
        Main method to run the scan and process the data.

        Returns:
            tuple: Contains angle map, mythen data, summed intensity, mean intensity, and standard deviation.
        """
        # Get the TIFF data and define as a volume
        self.volume = self.get_volume()

        # Calculate the detector matriz as if it was measured using the Mythen linear detector
        self.mythen_variable, self.cropped_mythen, self.mythen_lids = self.mythen(self.volume)

        # Perform the statistics calculation to return the processed data
        two_theta_scan, self.sum_of_intensities, self.mean, self.standard_deviation = self.estatistics(self.mythen_variable, self.cropped_mythen, self.mythen_lids)

        return np.asarray(self.mythen_variable), np.asarray(two_theta_scan), np.asarray(self.sum_of_intensities), np.asarray(self.mean), np.asarray(self.standard_deviation)


    def mythen(self, volume: np.ndarray) -> tuple:
        # Return the mythen matrix transposed?
        mythen        = np.sum(volume, axis = 1) #Projecting on the y/2theta plane
        open_mythen   = np.sum(mythen, axis = 0)
        croped_mythen = mythen[ :, self.input_mythen_lids[0]:self.input_mythen_lids[1] ]

        return mythen, croped_mythen, self.input_mythen_lids


def get_pixel_address(calibration_pixel_: np.ndarray, tth_: np.ndarray, steps_: int) -> np.ndarray:
    """
    Gets the pixel address based on calibration pixel values and two-theta values.

    Args:
        calibration_pixel (np.ndarray): Calibration pixel values.
        tth (np.ndarray): Two-theta values.
        steps (int): Number of steps in the scan.

    Returns:
        np.ndarray: Array of pixel addresses.
    """
    #pixel_address_ = calibration_pixel_[:, np.newaxis] + tth_[:steps_]  # Broadcasting magic!
    #return pixel_address_
    pixel_address = []
    for index in range(steps_):
        pixel_address.append(calibration_pixel_ + tth_[index])
    pixel_address_ = np.asarray(pixel_address)
    return pixel_address_

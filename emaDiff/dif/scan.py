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
from .io import get_file_list, logger, save_scan_data
from .parallel_scan import _get_xrd_batch
from .._version import __version__

NTHREADS = mp.cpu_count()

class Scan:
    """
    Scan class that handles scanning operations, including data calibration,
    statistical analysis, and plotting of diffractogram.
    """
    def __init__(self,
                 initial_angle: float,
                 final_angle: float,
                 number_of_steps: int,
                 xc: int,
                 yc: int,
                 output_folder: str,
                 scan_folder: str,
                 scan_filename: str,
                 ny_begin: int,
                 ny_end: int,
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
        self.size_step       = (final_angle - initial_angle) / number_of_steps
        self.number_of_steps = number_of_steps
        self.output_folder   = output_folder
        self.scan_folder     = scan_folder
        self.scan_filename   = scan_filename
        self.det_x           = detector_size_x
        self.xmin            = xc - 1
        self.xmax            = xc + 0
        #self.ymin            = yc - int(ny / 2) + 1
        #self.ymax            = yc + int(ny / 2)
        self.ymin            = ny_begin + 1
        self.ymax            = ny_end
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

        logger.info('Generating list of files.')
        self.list_of_files = get_file_list(self.number_of_steps, self.initial_angle, self.final_angle, self.scan_folder, self.scan_filename)

        params = [self.number_of_steps, self.ymax, self.ymin, self.det_x, self.list_of_files]

        logger.info('Reading TIFF files and generating volume...')
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
        logger.info(f'Two theta generated values: {tth[0]} and {tth[-1]}')

        # Perform the theta to pixel mapping using the calibration_pixel vector as input calculated in the `Calibration` class
        logger.info('Calculating the pixel address vector mapping...')
        pixel_address = get_pixel_address(self.calibration_pixel, tth, self.number_of_steps)
        # Round pixel_address values?
        pixel_address = np.round(pixel_address[:, mythen_lids[0]:mythen_lids[1]], 3)
        #logger.info(f'Calculated pixel addresses: [{pixel_address[:3]} ... {pixel_address[:-4]}]')

        flat_pixel_address = pixel_address.flatten()
        flat_croped_mythen = croped_mythen.flatten()

        det_start = np.round(min(flat_pixel_address), 3)
        det_end   = np.round(max(flat_pixel_address), 3)
        logger.info(f'det_start: {det_start:.3f} - det_end: {det_end:.3f}')

        # Calculate the histogram
        begin_bin_value = np.round(det_start - self.size_step / 2, 3)
        end_bin_value = np.round(det_end + self.size_step, 3)

        logger.info(f'Start bin value: {det_start - self.size_step / 2}')
        logger.info(f'End bin value: {det_end + self.size_step}')
        logger.info(f'Bin step size: {self.size_step}')

        bins = np.arange(begin_bin_value, end_bin_value, self.size_step, dtype=float)
        #bins = np.arange(det_start - self.size_step / 2, det_end + self.size_step, self.size_step, dtype=float)
        hist, _ = np.histogram(flat_pixel_address, bins=bins)

        logger.info(f'bins: {bins}')
        logger.info(f'histogram: {hist}')

        histogram_size = len(hist)
        number_of_output_parameters = 4

        # Start multiprocessing parallel histogram
        xrd_name = str(uuid.uuid4())
        logger.info(f'XRD name: {xrd_name}')

        try:
            sa.delete(xrd_name)
        except:
            pass

        logger.info('Creating XRD shared array...')
        xrd_matrix = sa.create(xrd_name, [histogram_size, number_of_output_parameters], dtype=np.float32)
        params = [xrd_matrix, NTHREADS, histogram_size, bins, flat_pixel_address, flat_croped_mythen]

        time0 = time.time()
        _get_xrd_batch(params)
        time1 = time.time()

        logger.info(f"Total time of execution of parallel XRD: {time1 - time0}s")
        logger.info(f"XRD matrix shape: {xrd_matrix.shape}")

        logger.info('Deleting shared array process...')
        sa.delete(xrd_name)

        xrd_dic = {
            'output_folder': self.output_folder,
            'scan_filename': self.scan_filename,
            'initial_angle': self.initial_angle,
            'final_angle': self.final_angle,
            'size_step': self.size_step,
            'number_of_steps': self.number_of_steps,
            'output_folder': self.output_folder,
            'scan_folder': self.scan_folder,
            'scan_filename': self.scan_filename,
            'det_x': self.det_x,
            'xmin': self.xmin,
            'xmax': self.xmax,
            'ymin': self.ymin,
            'ymax': self.ymax,
            'input_mythen_lids': self.input_mythen_lids,
            'calibration_pixel': self.calibration_pixel,
            'pixel_address': pixel_address
        }

        logger.info('Begin saving processed data.')
        save_scan_data(xrd_matrix, xrd_dic)
        logger.info('Finished saving processed data.')

        return xrd_matrix[:,0], xrd_matrix[:,1], xrd_matrix[:,2], xrd_matrix[:3]

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
        logger.info('Start to generate the diffractogram...')
        two_theta_scan, self.sum_of_intensities, self.mean, self.standard_deviation = self.estatistics(self.mythen_variable, self.cropped_mythen, self.mythen_lids)

        logger.info('Finished scan pipeline and data processing!')

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

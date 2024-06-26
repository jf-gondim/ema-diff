#!/usr/bin/env python3

import os
import re
import uuid
import glob

import numpy as np
import SharedArray as sa
import PIL.Image as Image
import multiprocessing as mp

from scipy.signal import find_peaks

from .read_tiff import read_tif_volume
from .io import get_file_list


class Calibration:

    def __init__(self,
                 start_angle: float,
                 end_angle: float,
                 step_size: float,
                 steps: int,
                 xc: int,
                 yc: int,
                 ny: int,
                 cfo: str,
                 cfi: str,
                 xdet: int,
                 ydet: int,
                 lids_border: int,
                 calibration_step_size: float):

        self.xmin = xc - 1
        self.xmax = xc + 0
        self.ymin = yc - (int(ny/2) + 1)
        self.ymax = yc + int(ny/2)
        self.xdet = xdet # detector size in x axis in pixels
        self.ydet = ydet # detector size in y axis in pixels

        self.steps       = steps
        self.start_angle = start_angle
        self.end_angle   = end_angle
        self.step_size   = step_size
        self.c_Folder    = cfo
        self.c_Filename  = cfi
        self.lids_border = lids_border
        self.calibration_step_size = (end_angle - start_angle) / steps

    def mythen(self, volume: np.ndarray) -> np.ndarray:
        """
        Processes volume data to generate a Mythen detector projection.

        This method takes a 3D volume array as input and performs the following steps:
        1. Projects the volume onto the y/2theta plane by summing along the first axis.
        2. Summing the projected array along the second axis to get a 1D array.
        3. Determines a threshold value based on the maximum value of the summed array.
        4. Identifies the region of interest (ROI) within the summed array.
        5. Applies windowing to the Mythen data based on the determined ROI.

        Args:
            volume (numpy.ndarray): A 3D array representing the volume data.

        Returns:
            numpy.ndarray: A processed 2D array representing the Mythen detector projection.

        Raises:
            ValueError: If the input volume array is empty or has incorrect dimensions.
        """
        # Projecting onto the y/2 theta plane
        mythen = np.sum(volume, axis = 1)
        mth_o = np.copy(mythen)

        # Sum along the second axis
        open_mythen = np.sum(mythen, axis = 0)

        # Define threshold for ROI
        threshold = ( int( max(open_mythen) / 2 ) )

        # Determine the ROI window
        mythen_window = np.asarray(np.nonzero(open_mythen > threshold))

        # Define any value of the lids_border as default?
        # The previous value was 5
        self.mythen_lids = [ min(mythen_window[0]) + self.lids_border, max(mythen_window[0]) - self.lids_border ]
        print(f'mythen_lids_calibration: {self.mythen_lids}')

        # Apply windowing to Mythen data
        mythen = mythen[:, self.mythen_lids[0]:self.mythen_lids[1]]
        mythen = np.transpose(mythen)

        return mythen

    def calibration_pixel(self, mythen_matrix) -> np.ndarray:
        """Calculates the calibration pixel values for each detector channel.

        Args:
            mythen_matrix: A numpy array representing the raw Mythen detector data.

        Returns:
            A numpy array containing the calibrated pixel positions for each detector channel.

        Raises:
            None
        """
        calibration_pixel = np.zeros(self.xdet, dtype=np.float32)

        for index in range(self.mythen_lids[0], self.mythen_lids[1]):
            peaks, _ = find_peaks(mythen_matrix[index], height=0.5)  # Adjust height threshold as needed
            if peaks.size > 0:
                calibration_pixel[index] = peaks[0] * self.calibration_step_size + self.start_angle

        return -calibration_pixel


    def calibration_main_run(self) -> tuple:
        """
        Runs the main calibration process.

        This method executes the primary steps for calibration, including:
        1. Running a calibration scan to generate a list of files.
        2. Reading a TIFF volume based on parameters.
        3. Initializing a detector (Mythen).
        4. Computing two_theta values for each file.
        5. Calculating pixel_theta values based on detector data.

        Returns:
            tuple: A tuple containing:
                - numpy.ndarray: Array of calculated intensities Mythen values.
                - numpy.ndarray: The calibration_pixel processed data.
                - numpy.ndarray: The loaded volume data.

        Raises:
            SomeException: An exception that might occur during file operations or computations.
        """
        # Create the list of all calibration files
        self.list_of_files = get_file_list(self.steps, self.step_size, self.start_angle, self.end_angle, self.c_Folder, self.c_Filename )

        # Define the parameters to read the multiple scan files measured at the beamline
        self.params = [self.steps, self.ymax, self.ymin, self.xdet, self.list_of_files]

        # Initialize volume and detector
        self.volume = read_tif_volume(self.params)

        # Calculate the detector matriz as if it was measured using the Mythen linear detector
        self.detector = self.mythen(self.volume)

        # Calculate the vector of calibration to use as input in the Scan class
        calibration_pixel_vector = self.calibration_pixel(self.detector)

        return self.detector, calibration_pixel_vector, self.volume

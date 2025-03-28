#!/usr/bin/env python3

import os
import re
import uuid
import glob

import numpy as np
import PIL.Image as Image
import multiprocessing as mp

from .io import get_file_list
from .read_tiff import read_tif_volume
from .log_module import configure_logger

logger = configure_logger(__name__)

class Calibration:

    def __init__(self,
                 start_angle: float,
                 end_angle: float,
                 steps: int,
                 xc: int,
                 yc: int,
                 ny_begin: int,
                 ny_end: int,
                 cfo: str,
                 cfi: str,
                 xdet: int,
                 ydet: int,
                 lids_border_left: int,
                 lids_border_right: int):

        self.xmin = xc - 1
        self.xmax = xc + 0
        self.ymin = ny_begin + 1
        self.ymax = ny_end
        self.xdet = xdet # detector size in x axis in pixels
        self.ydet = ydet # detector size in y axis in pixels

        self.steps       = steps
        self.start_angle = start_angle
        self.end_angle   = end_angle
        self.c_Folder    = cfo
        self.c_Filename  = cfi
        self.lids_border_left = lids_border_right
        self.lids_border_right = lids_border_right
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
        mt_copy = np.copy(mythen)

        # Sum along the second axis
        open_mythen = np.sum(mythen, axis = 0)

        # Define threshold for ROI
        threshold = ( int( max(open_mythen) / 2 ) )

        # Determine the ROI window
        mythen_window = np.asarray(np.nonzero(open_mythen > threshold))
        #import pdb;pdb.set_trace()

        # Define any value of the lids_border as default?
        # The previous value was 5
        crop_index =  min(mythen_window[0]) + self.lids_border_left, max(mythen_window[0]) - self.lids_border_right 
        self.mythen_lids = [ crop_index[0], crop_index[1] ]
        logger.info(f'Mythen lids values defined are: {self.mythen_lids}')
        #import pdb;pdb.set_trace()

        # Apply windowing to Mythen data
        mythen = mythen[:, self.mythen_lids[0]:self.mythen_lids[1]]
        #mythen = np.transpose(mythen)

        return mt_copy.T, crop_index

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
            pixel_verification_value = np.where(mythen_matrix[index] == max(mythen_matrix[index]))[0]
            calibration_pixel[index] = pixel_verification_value * self.calibration_step_size + self.start_angle

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
        #import pdb;pdb.set_trace()
        logger.info('Generating list of files.')
        self.list_of_files = get_file_list(self.steps, self.start_angle, self.end_angle, self.c_Folder, self.c_Filename )

        # Define the parameters to read the multiple scan files measured at the beamline
        self.params = [self.steps, self.ymax, self.ymin, self.xdet, self.list_of_files]

        # Initialize volume and detector
        logger.info('Reading TIFF files and generating volume...')
        self.volume = read_tif_volume(self.params)

        # Calculate the detector matriz as if it was measured using the Mythen linear detector
        logger.info('Calculating Mythen matrix.')
        self.detector, new_crop_window = self.mythen(self.volume)

        # Calculate the vector of calibration to use as input in the Scan class
        logger.info('Calculating calibration vector using the Mythen matrix...')
        import pdb;pdb.set_trace()
        calibration_pixel_vector = self.calibration_pixel(self.detector)

        logger.info('Finished the calibration pipeline for the Pilatus.')

        return self.detector, calibration_pixel_vector, self.volume, new_crop_window

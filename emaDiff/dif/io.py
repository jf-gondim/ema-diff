#!/usr/bin/env python3

import os
import re
import uuid
import glob
import h5py
import time
import numpy as np
import PIL.Image as Image
import SharedArray as sa
import multiprocessing as mp

from .read_tiff import read_tif_volume
from .._version import __version__

'''----------------------------------------------'''
import sys
import logging

# Define the log level for the console
console_log_level = logging.DEBUG

# Create a logger with the module name
logger = logging.getLogger('emaDiff')

# Create a handler for the console (stdout)
console_handler = logging.StreamHandler(sys.stdout)

# Define the format of the log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

# Set the log level for the logger and the handler
logger.setLevel(logging.DEBUG)
console_handler.setLevel(console_log_level)

# Constant for the debug level (not used in the current code, but kept as a reference)
DEBUG = logging.DEBUG

'''----------------------------------------------'''

def get_file_list(steps: int,
                  start_angle: float,
                  end_angle: float,
                  c_Folder: str,
                  c_Filename: str) -> list:
    """
    Runs a routine to gather a list of file paths.

    This method sets up and executes a calibration scan based on the specified parameters:
    - Computes the end angle based on the start angle, number of steps, and step size.
    - Checks compatibility of the computed end angle with the provided `end_angle` attribute.
    - Searches for TIFF files in a specified folder with a specific naming pattern.
    - Verifies the number of found TIFF files matches the expected number of steps.

    Returns:
        list: A list of file paths corresponding to the calibration scan images.

    Raises:
        SystemExit: If the number of found TIFF files does not match the expected number of steps.
    """
    logger.info('Running calibration scan!')

    start_id   = 0
    end_id     = steps - 1
    number_of_points = end_id - start_id + 1
    step_size = ( np.abs(start_angle) - end_angle ) / steps
    scan_range = number_of_points * step_size
    end_angle  = start_angle + scan_range
    folder     = c_Folder
    file_name  = c_Filename

    # Find TIFF files in folder
    filelist = sorted( glob.glob( "".join([folder, '/', file_name, '*.tiff'])),
        key=lambda x: float(re.findall("([0-9]+?)\.tiff", x)[0]) )

    # Verify and set end_angle
    if end_angle != end_angle:
        logger.info(f'End Angle value is incompatible with the setted one. Suggested value: {end_angle}')
    else:
        end_angle = end_angle

    # Check if number of files matches expected steps
    if len(filelist) != steps:
        logger.error('PICTURES MISSING!!')
        sys.exit()
    else:
        logger.info('Calibration Scan done successfully.')

    return filelist

def save_scan_data(xrd_matrix, dic):
    # Add verification if path exists. If doesn't create the path and continue the processing and add log messages
    diffractogram_file_path = "".join([dic['output_folder'], dic['scan_filename'], 'proc.h5'])
    with h5py.File(diffractogram_file_path, "w") as h5f:
        h5f.create_group("proc")
        h5f.create_dataset('proc/tth', data=xrd_matrix[:,0], dtype=np.float32)
        h5f.create_dataset('proc/intensities', data=xrd_matrix[:,1], dtype=np.float32)
        h5f.create_dataset('proc/mean', data=xrd_matrix[:,2], dtype=np.float32)
        h5f.create_dataset('proc/standard_deviation', data=xrd_matrix[:,3], dtype=np.float32)

        h5f.create_group("metadata")
        h5f.create_dataset('metadata/initial_angle', data = dic['initial_angle'], dtype=np.float32)
        h5f.create_dataset('metadata/final_angle', data = dic['final_angle'], dtype=np.float32)
        h5f.create_dataset('metadata/size_step', data = dic['size_step'], dtype=np.float32)
        h5f.create_dataset('metadata/number_of_steps', data = dic['number_of_steps'], dtype=np.float32)
        h5f.create_dataset('metadata/output_folder', data = dic['output_folder'])
        h5f.create_dataset('metadata/scan_folder', data = dic['scan_folder'])
        h5f.create_dataset('metadata/scan_filename', data = dic['scan_filename'])
        h5f.create_dataset('metadata/det_x', data = dic['det_x'], dtype=np.float32)
        h5f.create_dataset('metadata/xmin', data = dic['xmin'], dtype=np.float32)
        h5f.create_dataset('metadata/xmax', data = dic['xmax'], dtype=np.float32)
        h5f.create_dataset('metadata/ymin', data = dic['ymin'], dtype=np.float32)
        h5f.create_dataset('metadata/ymax', data = dic['ymax'], dtype=np.float32)
        h5f.create_dataset('metadata/input_mythen_lids', data = dic['input_mythen_lids'], dtype=np.float32)
        h5f.create_dataset('metadata/calibration_pixel', data = dic['calibration_pixel'], dtype=np.float32)
        h5f.create_dataset('metadata/pixel_address', data = dic['pixel_address'], dtype=np.float32)
        h5f.create_dataset('metadata/datetime', data = time.strftime("%m/%d/%Y - %H:%M:%S"))
        h5f.create_dataset('metadata/software_version', data = __version__[:5])

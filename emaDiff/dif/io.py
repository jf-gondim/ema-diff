#!/usr/bin/env python3

import os
import re
import uuid
import glob

import numpy as np
import PIL.Image as Image
import SharedArray as sa
import multiprocessing as mp

from .read_tiff import read_tif_volume

'''----------------------------------------------'''
import sys
import logging

# Define the log level for the console
console_log_level = logging.DEBUG

# Create a logger with the module name
logger = logging.getLogger(__name__)

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
                  step_size: float,
                  start_angle: float,
                  end_angle: float,
                  c_Folder: str,
                  c_Filename: str) -> list:
    """
    Runs a calibration scan to gather a list of file paths.

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
    print('-----------------')
    print('RUNNING CALIBRATION SCAN...')
    print('-----------------')

    start_id   = 0
    end_id     = steps - 1
    number_of_points = end_id - start_id + 1
    scan_range = number_of_points * step_size
    end_angle  = start_angle + scan_range
    folder     = c_Folder
    file_name  = c_Filename

    # Find TIFF files in folder
    filelist = sorted( glob.glob( "".join([folder, '/', file_name, '*.tiff'])),
        key=lambda x: float(re.findall("([0-9]+?)\.tiff", x)[0]) )

    # Verify and set end_angle
    if end_angle != end_angle:
        print(f'End Angle value is incompatible with the setted one. Suggested value: {end_angle}')
    else:
        end_angle = end_angle

    # Check if number of files matches expected steps
    if len(filelist) != steps:
        raise SystemExit('!!!!!!!!! PICTURES MISSING !!!!!!!!!')
    else:
        print('Calibration Scan done successfully.')

    return filelist

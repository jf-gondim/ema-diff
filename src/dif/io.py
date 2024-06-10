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

def get_file_list(number_of_steps: int,
                  size_step: float,
                  initial_angle: float,
                  final_angle: float,
                  scan_folder: str,
                  scan_filename: str) -> list:
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

    start_id = 0
    end_id   = number_of_steps - 1
    number_of_points = end_id - start_id + 1
    scan_range    = number_of_points * size_step
    end_angle     = initial_angle + scan_range
    scan_folder   = scan_folder
    scan_filename = scan_filename

    if final_angle != end_angle:
        raise ValueError(f'End Angle value is incompatible with the setted one. Suggested value: {end_angle}')
    else:
        final_angle = end_angle

    print('-----------------')
    print('RUNNING FLY SCAN...')
    print('-----------------')

    filelist = sorted(glob.glob(scan_folder + '/' + scan_filename + '*.tiff'), \
        key=lambda x: float(re.findall("([0-9]+?)\.tiff", x)[0]))

    if len(filelist) != number_of_steps:
        raise ValueError('Number of scan files is different thant the number of angle steps defined!')
    else:
        print('Fly Scan done successfully!')

    return filelist

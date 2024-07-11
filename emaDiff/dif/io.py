#!/usr/bin/env python3

import os
import re
import sys
import uuid
import glob
import h5py
import time
import numpy as np
import PIL.Image as Image
import multiprocessing as mp

from .read_tiff import read_tif_volume
from .._version import __version__
from .log_module import configure_logger

logger = configure_logger(__name__)


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
    """
    Save the scan data to an HDF5 file.

    Parameters:
    - xrd_matrix (numpy.ndarray): The XRD matrix containing the scan data.
    - dic (dict): A dictionary containing the metadata for the scan.

    Returns:
        None
    """
    # Add verification if path exists. If doesn't create the path and continue the processing and add log messages
    diffractogram_file_path = "".join([dic['output_folder'], dic['scan_filename'], 'proc.h5'])
    with h5py.File(diffractogram_file_path, "w") as h5f:
        proc_group = h5f.create_group("proc")
        metadata_group = h5f.create_group("metadata")

        proc_group.create_dataset('tth', data=xrd_matrix[:,0], dtype=np.float32)
        proc_group.create_dataset('intensities', data=xrd_matrix[:,1], dtype=np.float32)
        proc_group.create_dataset('mean', data=xrd_matrix[:,2], dtype=np.float32)
        proc_group.create_dataset('standard_deviation', data=xrd_matrix[:,3], dtype=np.float32)

        metadata_group.create_dataset('initial_angle', data=dic['initial_angle'], dtype=np.float32)
        metadata_group.create_dataset('final_angle', data=dic['final_angle'], dtype=np.float32)
        metadata_group.create_dataset('size_step', data=dic['size_step'], dtype=np.float32)
        metadata_group.create_dataset('number_of_steps', data=dic['number_of_steps'], dtype=np.float32)
        metadata_group.create_dataset('output_folder', data=dic['output_folder'])
        metadata_group.create_dataset('scan_folder', data=dic['scan_folder'])
        metadata_group.create_dataset('scan_filename', data=dic['scan_filename'])
        metadata_group.create_dataset('det_x', data=dic['det_x'], dtype=np.float32)
        metadata_group.create_dataset('xmin', data=dic['xmin'], dtype=np.float32)
        metadata_group.create_dataset('xmax', data=dic['xmax'], dtype=np.float32)
        metadata_group.create_dataset('ymin', data=dic['ymin'], dtype=np.float32)
        metadata_group.create_dataset('ymax', data=dic['ymax'], dtype=np.float32)
        metadata_group.create_dataset('input_mythen_lids', data=dic['input_mythen_lids'], dtype=np.float32)
        metadata_group.create_dataset('calibration_pixel', data=dic['calibration_pixel'], dtype=np.float32)
        metadata_group.create_dataset('pixel_address', data=dic['pixel_address'], dtype=np.float32)
        metadata_group.create_dataset('datetime', data=time.strftime("%m/%d/%Y - %H:%M:%S"))
        metadata_group.create_dataset('software_version', data=__version__[:5])

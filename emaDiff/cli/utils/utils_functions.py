import h5py
import numpy as np

from ...dif.calibration import Calibration
from ...dif.scan import Scan

def calibration_cli(start_angle: float,
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
                    lids_border_right: int,
                    output_file_path: str):
    """
    Perform calibration scan and save the results to an HDF5 file.

    Args:
        start_angle (float): The starting angle of the scan.
        end_angle (float): The ending angle of the scan.
        steps (int): The number of steps in the scan.
        xc (int): The x-coordinate of the center of the image.
        yc (int): The y-coordinate of the center of the image.
        ny_begin (int): The starting index of the vertical scan range.
        ny_end (int): The ending index of the vertical scan range.
        cfo (str): The path to the calibration folder.
        cfi (str): The path to the calibration file.
        xdet (int): The x-coordinate of the detector.
        ydet (int): The y-coordinate of the detector.
        lids_border_left (int): The left border of the lids.
        lids_border_right (int): The right border of the lids.
        output_file_path (str): The path to save the calibration results.

    Returns:
        None
    """

    calib = Calibration(start_angle, end_angle, steps, xc, yc, ny_begin, ny_end, cfo, cfi, xdet, ydet, lids_border_left, lids_border_right)
    calibration_mythen_full_matrix, calibration_vector, calibration_volume, mythen_lids= calib.calibration_main_run()

    calibration_hdf5_abs_file_path = "".join([output_file_path, cfi, "proc_calibration.h5"])

    with h5py.File(calibration_hdf5_abs_file_path, "w") as h5f:
        h5f.create_group("data")
        h5f.create_dataset("data/mythen", data=calibration_mythen_full_matrix, dtype=np.float32)
        h5f.create_dataset("data/calibration_vector", data=calibration_vector, dtype=np.float32)
        h5f.create_dataset("data/volume", data=calibration_volume, dtype=np.float32)
        h5f.create_dataset("data/mythen_lids", data=mythen_lids, dtype=np.int16)


def scan_cli(initial_angle: float,
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
    Perform a scan and save the results to an HDF5 file.

    Args:
        initial_angle (float): The initial angle of the scan.
        final_angle (float): The final angle of the scan.
        number_of_steps (int): The number of steps in the scan.
        xc (int): The x-coordinate of the center of the image.
        yc (int): The y-coordinate of the center of the image.
        output_folder (str): The folder to save the scan results.
        scan_folder (str): The folder to save the scan files.
        scan_filename (str): The filename of the scan file.
        ny_begin (int): The starting index of the vertical scan range.
        ny_end (int): The ending index of the vertical scan range.
        detector_size_x (int): The size of the detector in the x-direction.
        input_mythen_lids (np.ndarray): The input Mythen lids.
        calibration_pixel (np.ndarray): The calibration pixel.

    Returns:
        None
    """

    scan = Scan(initial_angle,
                final_angle,
                number_of_steps,
                xc,
                yc,
                output_folder,
                scan_folder,
                scan_filename,
                ny_begin,
                ny_end,
                detector_size_x,
                input_mythen_lids,
                calibration_pixel)

    xrd_mythen_matrix, xrd_tth, xrd_intensity, xrd_mean, xrd_std = scan.scan_main_run()

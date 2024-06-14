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

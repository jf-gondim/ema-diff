import h5py
import numpy as np

from ...dif.calibration import Calibration
from ...dif.scan import Scan

def calibration_cli(start_angle: float,
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
                    output_file_path: str):


    calib = Calibration(start_angle, end_angle, step_size, steps, xc, yc, ny, cfo, cfi, xdet, ydet, lids_border)
    calibration_mythen_full_matrix, calibration_vector, calibration_volume = calib.calibration_main_run()

    calibration_hdf5_abs_file_path = "".join([output_file_path, cfi, "proc.h5"])

    with h5py.File(calibration_hdf5_abs_file_path, "w") as h5f:
        h5f.create_group("data")
        h5f.create_dataset("data/mythen", data=calibration_mythen_full_matrix, dtype=np.float32)
        h5f.create_dataset("data/calibration_vector", data=calibration_vector, dtype=np.float32)
        h5f.create_dataset("data/volume", data=calibration_volume, dtype=np.float32)


def scan_cli(initial_angle: float,
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
             input_mythen_lids: list,
             calibration_pixel: np.ndarray):

    scan = Scan(initial_angle,
                final_angle,
                size_step,
                number_of_steps,
                xc,
                yc,
                output_folder,
                scan_folder,
                scan_filename,
                ny,
                detector_size_x,
                input_mythen_lids,
                calibration_pixel)
    xrd_mythen_matrix, xrd_tth, xrd_intensity, xrd_mean, xrd_std = scan.scan_main_run()

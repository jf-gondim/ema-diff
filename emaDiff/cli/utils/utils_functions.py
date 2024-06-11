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
                    ydet: int):

    #calib = Calibration(start_angle, end_angle, step_size, steps, xc, yc, ny, cfo, cfi, xdet, ydet)
    #calib.calibration_main_run()

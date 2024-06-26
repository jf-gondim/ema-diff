import os
import sys
import numpy as np

from rich import print
from typing_extensions import Annotated
from typing import List, Optional, Tuple
from typer import Typer, Context, Argument, Exit, Option
from .._version import __version__
from .utils.utils_functions import calibration_cli

'''----------------------------------------------'''
import logging
console_log_level = 10
logger            = logging.getLogger(__name__)
console_handler   = logging.StreamHandler(sys.stdout)
formatter         = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)
console_handler.setLevel(console_log_level)

DEBUG = 10
'''----------------------------------------------'''

app = Typer()

def __print_version(
        use_print: bool
) -> None:
    """Build-in function that prints the CLI version

    Args:
        use_print (Optional[bool]): flag to print the CLI version

    Returns:
        None

    """
    if use_print:
        print("CLI version : {}".format(__version__))
        raise Exit(code=0)


@app.callback(invoke_without_command=True)
def __cli_commands(
        cxt: Context,
        version: Annotated[Optional[bool], Option(
            "--version", "-v",
            help="application version",
            callback=__print_version,
            is_eager=True, is_flag=True)] = False
) -> None:
    """Function that prints all the possible functions to call using the deep

    Args:
        cxt (Context): context object
        version (Annotated[Optional[bool]): flag to print the CLI version

    Returns:
        None

    """
    # this part is to ensure to only print when the function is called without any command
    if cxt.invoked_subcommand:
        return

    ssc_dif_cli_mgs = """

    ███████╗███╗   ███╗ █████╗       ██████╗ ██╗██╗      █████╗ ████████╗██╗   ██╗███████╗
    ██╔════╝████╗ ████║██╔══██╗      ██╔══██╗██║██║     ██╔══██╗╚══██╔══╝██║   ██║██╔════╝
    █████╗  ██╔████╔██║███████║█████╗██████╔╝██║██║     ███████║   ██║   ██║   ██║███████╗
    ██╔══╝  ██║╚██╔╝██║██╔══██║╚════╝██╔═══╝ ██║██║     ██╔══██║   ██║   ██║   ██║╚════██║
    ███████╗██║ ╚═╝ ██║██║  ██║      ██║     ██║███████╗██║  ██║   ██║   ╚██████╔╝███████║
    ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝      ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝
    """

    print("Welcome to the EMA-p CLI !!!\n")
    print(ssc_dif_cli_mgs)
    print("\nYou can use the followings commands to run the CLI : ")
    print(100 * "=")
    print("[green][b]calibration[/]")
    print("[blue][b]scan[/]")
    print("\nwhere:")
    print("[green]green[/green] pipeline for calibrate the Pilatus data")
    print("[blue]blue[/blue] pipeline for obtain the diffractogram using the scan parameters")

    print(100 * "=" + "\n")

    print("for more info about the functions, use the command ssc-dif function_name --help")


@app.command(name="calibration_ema", help="Calibration function for all Pilatus scan data.")
def calibration_ema(
    start_angle : Annotated[float, Argument(..., metavar="start_angle", help="First angle of the diffraction scan")],
    end_angle : Annotated[float, Argument(..., metavar="end_angle", help="Final angle of the diffraction scan")],
    step_size : Annotated[float, Argument(..., metavar="step_size", help="Size of the angle step performed in the scan")],
    steps : Annotated[int, Argument(..., metavar="steps", help="Number of steps performed in the scan")],
    xc : Annotated[float, Argument(..., metavar="xc", help="Center of the detector in the x axis")],
    yc : Annotated[float, Argument(..., metavar="yc", help="Center of the detector in the y axis")],
    cfo : Annotated[str, Argument(..., metavar="cfo", help="Absolute path of the calibration folder data")],
    cfi : Annotated[str, Argument(..., metavar="cfi", help="Name of the scan file")],
    xdet : Annotated[int, Argument(..., metavar="xdet", help="Size of the detector in the x axis in pixels")],
    ydet : Annotated[int, Argument(..., metavar="ydet", help="Size of the detector in the y axis in pixels")],
) -> None:

    """CLI function that apply the calibration pipeline.

    To use the CLI function, use the following command
    ```{.sh title=help command}
    ssc-dif calibration --help
    ```

    ```{.sh title=output command}
    Usage: ssc-dif calibration [OPTIONS]

    ╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ *    start_angle      start_angle  First angle of the diffraction scan [default: None] [required]                   │
    │ *    end_angle        end_angle    Final angle of the diffraction scan [default: None] [required]                   │
    │ *    step_size        step_size    Size of the angle step performed in the scan [default: None] [required]          │
    │ *    steps            steps        Number of steps performed in the scan [default: None] [required]                 │
    │ *    xc               xc           Center of the detector in the x axis [default: None] [required]                  │
    │ *    yc               yc           Center of the detector in the y axis [default: None] [required]                  │
    │ *    cfo              cfo          Absolute path of the calibration folder data [default: None] [required]          │
    │ *    cfi              cfi          Name of the scan file [default: None] [required]                                 │
    │ *    xdet             xdet         Size of the detector in the x axis in pixels [default: None] [required]          │
    │ *    ydet             ydet         Size of the detector in the y axis in pixels [default: None] [required]          │
    ╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
    ╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ --help          Show this message and exit.                                                                         │
    ╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

    ```

    Args:
        initial_angle (float): Initial angle for the scan.
        final_angle (float): Final angle for the scan.
        size_step (float): Step size for each scan increment.
        number_of_steps (int): Number of steps in the scan.
        pixel_theta (np.ndarray): Pixel theta values.
        xc (int): X-coordinate of the center.
        yc (int): Y-coordinate of the center.
        output_folder (str): Path to the output folder.
        scan_folder (str): Path to the scan folder.
        scan_filename (str): Filename of the scan file.
        ny (int): Number of y pixels.
        detector_size_x (int): Size of the detector in x-dimension.
    Returns:
        pixel_theta (np.ndarray): Calibrated pixel theta values.
        volume (np.ndarray): Volume of all TIFF image files in a 3D numpy array.

    """

    # Include Args

    # Include function call with args
    scan_calibration = calibration_cli(start_angle,
                                       end_angle,
                                       step_size,
                                       steps,
                                       xc,
                                       yc,
                                       ny,
                                       cfo=calibration_folder,
                                       cfi=calibration_filename,
                                       xdet=xdet,
                                       ydet=ydet)

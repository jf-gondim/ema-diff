import os
import sys
import h5py
import numpy as np

import typer

from rich import print
from typing_extensions import Annotated
from typing import List, Optional, Tuple
from typer import Typer, Context, Argument, Exit, Option
from .._version import __version__
from .utils.utils_functions import calibration_cli, scan_cli

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
        print("CLI version : {}".format(__version__[:5]))
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

    ema_diff_msg = """

    ███████╗███╗   ███╗ █████╗       ██████╗ ██╗███████╗███████╗
    ██╔════╝████╗ ████║██╔══██╗      ██╔══██╗██║██╔════╝██╔════╝
    █████╗  ██╔████╔██║███████║█████╗██║  ██║██║█████╗  █████╗
    ██╔══╝  ██║╚██╔╝██║██╔══██║╚════╝██║  ██║██║██╔══╝  ██╔══╝
    ███████╗██║ ╚═╝ ██║██║  ██║      ██████╔╝██║██║     ██║
    ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝      ╚═════╝ ╚═╝╚═╝     ╚═╝
    """

    print("Welcome to the EMADiff CLI !!!\n")
    print(ema_diff_msg)
    print("\nYou can use the followings commands to run the CLI : ")
    print(100 * "=")
    print("[green][b]calibration[/]")
    print("[blue][b]scan[/]")
    print("\nwhere:")
    print("[green]green[/green] pipeline to calibrate the Pilatus data")
    print("[blue]blue[/blue] pipeline to obtain the diffractogram using the scan parameters")

    print(100 * "=" + "\n")

    print("for more info about the functions, use the command ema-diff function_name --help")


@app.command(name="calibration", help="Calibration function for all Pilatus scan data.")
def calibration(
    start_angle : Annotated[float, Argument(..., metavar="start_angle", help="First angle of the diffraction scan")],
    end_angle : Annotated[float, Argument(..., metavar="end_angle", help="Final angle of the diffraction scan")],
    step_size : Annotated[float, Argument(..., metavar="step_size", help="Size of the angle step performed in the scan")],
    steps : Annotated[int, Argument(..., metavar="steps", help="Number of steps performed in the scan")],
    xc : Annotated[int, Argument(..., metavar="xc", help="Center of the detector in the x axis")],
    yc : Annotated[int, Argument(..., metavar="yc", help="Center of the detector in the y axis")],
    ny: Annotated[int, Argument(..., metavar="ny", help="y axis width to crop the scan TIFF file")],
    cfo : Annotated[str, Argument(..., metavar="cfo", help="Absolute path of the calibration folder data")],
    cfi : Annotated[str, Argument(..., metavar="cfi", help="Name of the scan file")],
    xdet : Annotated[int, Argument(..., metavar="xdet", help="Size of the detector in the x axis in pixels")],
    ydet : Annotated[int, Argument(..., metavar="ydet", help="Size of the detector in the y axis in pixels")],
    lids_border : Annotated[int, Argument(..., metavar="lids_border", help="Size of the border to crop the Mythen matrix")],
    output_file_path: Annotated[str, Argument(..., metavar="output_file_path", help="Absolute path to save the calibration file")]
) -> None:

    """CLI function that apply the calibration pipeline.

    To use the CLI function, use the following command
    ```{.sh title=help command}
    ema-diff calibration --help
    ```

    ```{.sh title=output command}
    Usage: ema-diff calibration_ema [OPTIONS] start_angle end_angle step_size
                                     steps xc yc ny cfo cfi xdet ydet lids_border

     Calibration function for all Pilatus scan data.

    ╭─ Arguments ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ *    start_angle      start_angle  First angle of the diffraction scan [default: None] [required]                                                                                     │
    │ *    end_angle        end_angle    Final angle of the diffraction scan [default: None] [required]                                                                                     │
    │ *    step_size        step_size    Size of the angle step performed in the scan [default: None] [required]                                                                            │
    │ *    steps            steps        Number of steps performed in the scan [default: None] [required]                                                                                   │
    │ *    xc               xc           Center of the detector in the x axis [default: None] [required]                                                                                    │
    │ *    yc               yc           Center of the detector in the y axis [default: None] [required]                                                                                    │
    │ *    ny               ny           y axis width to crop the scan TIFF file [default: None] [required]                                                                                 │
    │ *    cfo              cfo          Absolute path of the calibration folder data [default: None] [required]                                                                            │
    │ *    cfi              cfi          Name of the scan file [default: None] [required]                                                                                                   │
    │ *    xdet             xdet         Size of the detector in the x axis in pixels [default: None] [required]                                                                            │
    │ *    ydet             ydet         Size of the detector in the y axis in pixels [default: None] [required]                                                                            │
    │ *    lids_border      lids_border  Size of the border to crop the Mythen matrix [default: None] [required]                                                                            │
    ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
    ╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ --help          Show this message and exit.                                                                                                                                           │
    ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

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
        lids_border (int): Size of the border to crop the Mythen matrix.
    Returns:
        pixel_theta (np.ndarray): Calibrated pixel theta values.
        volume (np.ndarray): Volume of all TIFF image files in a 3D numpy array.

    """
    scan_calibration = calibration_cli(start_angle,
                                       end_angle,
                                       step_size,
                                       steps,
                                       xc,
                                       yc,
                                       ny,
                                       cfo,
                                       cfi,
                                       xdet,
                                       ydet,
                                       lids_border,
                                       output_file_path)

@app.command(name="scan", help="Function that generates the diffractogram for all Pilatus scan data.")
def scan(
    initial_angle : Annotated[float, Argument(..., metavar="initial_angle", help="First angle of the diffraction scan")],
    final_angle : Annotated[float, Argument(..., metavar="final_angle", help="Final angle of the diffraction scan")],
    size_step : Annotated[float, Argument(..., metavar="size_steps", help="Size of the angle step performed in the scan")],
    number_of_steps : Annotated[int, Argument(..., metavar="number_of_steps", help="Number of steps performed in the scan")],
    xc : Annotated[int, Argument(..., metavar="xc", help="Center of the detector in the x axis")],
    yc : Annotated[int, Argument(..., metavar="yc", help="Center of the detector in the y axis")],
    output_folder : Annotated[str, Argument(..., metavar="output_folder", help="Absolute path of the folder to save all the output values")],
    scan_folder : Annotated[str, Argument(..., metavar="scan_folder", help="Absolute path of the folder which contains the scan files")],
    scan_filename : Annotated[str, Argument(..., metavar="scan_filename", help="File name of the scan to generate the diffractogram")],
    ny : Annotated[int, Argument(..., metavar="ny", help="y axis width to crop the scan TIFF file")],
    detector_size_x : Annotated[int, Argument(..., metavar="detector_size_x", help="Size of the detector in the x axis in pixels")],
    calibration_pixel_file_path : Annotated[str, Argument(..., metavar="calibration_pixel_file_path", help="Size of the border to crop the Mythen matrix")],
) -> None:
    """CLI function that apply the scan pipeline and generate the diffractogram.

    To use the CLI function, use the following command
    ```{.sh title=help command}
    ema-diff scan --help
    ```

    ```{.sh title=output command}
    Usage: ema-diff scan_ema [OPTIONS] initial_angle final_angle size_steps
                              number_of_steps xc yc output_folder scan_folder
                              scan_filename ny detector_size_x lids
                              calibration_pixel_file_path

     Function that generates the diffractogram for all Pilatus scan data.

    ╭─ Arguments ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ *    initial_angle                    initial_angle                First angle of the diffraction scan [default: None] [required]                                                     │
    │ *    final_angle                      final_angle                  Final angle of the diffraction scan [default: None] [required]                                                     │
    │ *    size_step                        size_steps                   Size of the angle step performed in the scan [default: None] [required]                                            │
    │ *    number_of_steps                  number_of_steps              Number of steps performed in the scan [default: None] [required]                                                   │
    │ *    xc                               xc                           Center of the detector in the x axis [default: None] [required]                                                    │
    │ *    yc                               yc                           Center of the detector in the y axis [default: None] [required]                                                    │
    │ *    output_folder                    output_folder                Absolute path of the folder to save all the output values [default: None] [required]                               │
    │ *    scan_folder                      scan_folder                  Absolute path of the folder which contains the scan files [default: None] [required]                               │
    │ *    scan_filename                    scan_filename                File name of the scan to generate the diffractogram [default: None] [required]                                     │
    │ *    ny                               ny                           y axis width to crop the scan TIFF file [default: None] [required]                                                 │
    │ *    detector_size_x                  detector_size_x              Size of the detector in the x axis in pixels [default: None] [required]                                            │
    │ *    input_mythen_lids                input_mythen_lids            Size of the detector in the y axis in pixels [default: None] [required]                                            │
    │ *    calibration_pixel_file_path      calibration_pixel_file_path  Size of the border to crop the Mythen matrix [default: None] [required]                                            │
    ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
    ╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ --help          Show this message and exit.                                                                                                                                           │
    ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
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
        lids_border (int): Size of the border to crop the Mythen matrix.
    Returns:
        pixel_theta (np.ndarray): Calibrated pixel theta values.
        volume (np.ndarray): Volume of all TIFF image files in a 3D numpy array.

    """
    with h5py.File(calibration_pixel_file_path, "r") as h5f:
       calibration_pixel_vector = h5f["data/calibration_vector"][:].astype(np.float32)
       lids = h5f["data/mythen_lids"][:].astype(np.int16)

    scan_calibration = scan_cli(initial_angle,
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
                                lids,
                                calibration_pixel_vector)

if __name__ == "__main__":
    app()

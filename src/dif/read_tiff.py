#!/usr/bin/env python3

import os
import re
import uuid
import glob
import numpy as np
import SharedArray as sa
import PIL.Image as Image
import multiprocessing as mp
import matplotlib.pyplot as plt

def read_tif_volume(params):
    """
    Reads a volume of .tiff files in parallel.

    Reads a set of TIFF files and constructs a volume array. If a subset region
    of each image is to be read, specify the region using `sizex_min` and `sizex_max`.

    Args:
        params (tuple): A tuple containing:
            N (int): Number of files.
            sizex_max (int): Maximum x-dimension size.
            sizex_min (int, optional): Minimum x-dimension size (default: 0).
            sizey (int): y-dimension size.
            filelist (list): List of file paths.

    Returns:
        numpy.ndarray: A 3D array representing the volume constructed from TIFF files.

    Raises:
        FileNotFoundError: If any of the specified files are not found.
    """

    def _worker_read_tif_batch(params, start, end):
        _, sizex_max, sizex_min, _, filelist, _, volume = params

        for k in range(start, end):
            try:
                image_data = np.array(Image.open(filelist[k]))[sizex_min:sizex_max, :]
                volume[k] = image_data
            except FileNotFoundError as e:
                raise e(f"File '{filelist[k]}' not found.")

    def _read_tif_batch(params):
        t, N = params[5], params[0]
        b = int(np.ceil(N/t))

        processes = []
        for k in range(t):
            begin_ = k * b
            end_ = min((k + 1) * b, N)
            p = mp.Process(target=_worker_read_tif_batch, args=(params, begin_, end_))
            processes.append(p)

        for p in processes:
            p.start()

        for p in processes:
            p.join()

    if len(params) == 5:
        N, sizex_max, sizex_min, sizey, filelist = params
    else:
        N, sizex_max, sizey, filelist = params
        sizex_min = 0

    threads = len(os.sched_getaffinity(0))
    params.append(threads)

    volume_name = str(uuid.uuid4())
    try:
        sa.delete(volume_name)
    except:
        pass

    volume = sa.create(volume_name, [N, sizex_max-sizex_min, sizey], dtype='int32')
    params.append(volume)

    _read_tif_batch(params)

    sa.delete(volume_name)

    return volume

import uuid
import time
import numpy as np
import SharedArray as sa
import multiprocessing as mp

from .log_module import configure_logger

logger = configure_logger(__name__)

NTHREADS = mp.cpu_count()

def _get_xrd_batch(params):
    """
    Perform parallel processing to calculate XRD batch.

    Args:
        params (tuple): Tuple containing the parameters for XRD batch calculation.

    Returns:
        None
    """
    histogram_size = params[2]
    number_of_chunks = int(np.ceil(histogram_size / NTHREADS))

    processes = []
    for chunk_index in range(NTHREADS):
        begin_ = chunk_index * number_of_chunks
        end_ = min((chunk_index + 1) * number_of_chunks, histogram_size)
        process = mp.Process(target=_worker_get_xrd_batch_, args=(params, begin_, end_))
        processes.append(process)

    for p in processes:
        p.start()

    for p in processes:
        p.join()


def _worker_get_xrd_batch_(params, start, end):
    """
    Worker function to calculate XRD batch for a given range of indices.

    Args:
        params (tuple): Tuple containing the parameters for XRD batch calculation.
        start (int): Start index of the range.
        end (int): End index of the range.

    Returns:
        None
    """
    xrd, nthreads, N, bins, flat_pixel_address, flat_croped_mythen = params
    for index in range(start, end):
        min_ = tth_ = bins[index]
        max_ = bins[index + 1]
        tth_index = np.where(np.logical_and(flat_pixel_address >= min_, flat_pixel_address <= max_))[0]
        int_ = np.sum(flat_croped_mythen[tth_index])
        mean_ = np.mean(flat_croped_mythen[tth_index])
        std_ = np.std(flat_croped_mythen[tth_index])
        xrd[index] = [tth_, int_, mean_, std_]

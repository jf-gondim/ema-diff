import uuid
import time
import numpy as np
import SharedArray as sa
import multiprocessing as mp

NTHREADS = mp.cpu_count()

def _get_xrd_batch(params):

    # t, N = params[1], params[2]
    # b = int( np.ceil(N/t) )
    # t -> nthreads
    # N -> histogram_size
    #nthreads, histogram_size = params[1], params[2]
    histogram_size = params[2]
    number_of_chunks = int( np.ceil(histogram_size/NTHREADS) )

    processes = []
    # k -> chunk_index
    # b -> number_of_chunks
    for chunk_index in range(NTHREADS):
        begin_  = chunk_index * number_of_chunks
        end_    = min( (chunk_index+1) * number_of_chunks, histogram_size)
        process = mp.Process(target=_worker_get_xrd_batch_, args=(params, begin_, end_))
        processes.append(process)

    for p in processes:
        p.start()

    for p in processes:
        p.join()

def _worker_get_xrd_batch_(params, start, end):
    xrd, nthreads, N, bins, flat_pixel_address, flat_croped_mythen = params
    for index in range(start, end):
        min_       = tth_ = bins[index]
        max_       = bins[index + 1]
        tth_index  = np.where(np.logical_and(flat_pixel_address>=min_, flat_pixel_address<=max_))[0]
        int_       = np.sum(flat_croped_mythen[tth_index])
        mean_      = np.mean(flat_croped_mythen[tth_index])
        std_       = np.std(flat_croped_mythen[tth_index])
        xrd[index] = [tth_,int_,mean_,std_]

import os
import h5py
import unittest
import numpy as np
from ..io import save_scan_data

class IOTest(unittest.TestCase):
    def test_save_scan_data(self):
        # Added pdb entry point to debug
        import pdb;pdb.set_trace()

        # Create dummy data
        xrd_matrix = np.array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]])
        dic = {
            'output_folder': '/path/to/output',
            'scan_filename': 'scan',
            'initial_angle': 0.0,
            'final_angle': 180.0,
            'size_step': 1.0,
            'number_of_steps': 180,
            'scan_folder': '/path/to/scan',
            'det_x': 10.0,
            'xmin': 0.0,
            'xmax': 100.0,
            'ymin': 0.0,
            'ymax': 100.0,
            'input_mythen_lids': [1, 2, 3],
            'calibration_pixel': 5.0,
            'pixel_address': 100.0
        }


        # Verify the HDF5 file was created and contains the expected data
        # Get the current directory
        current_dir = os.getcwd()

        # Update the output folder path
        dic['output_folder'] = current_dir + '/'

        # Call the function
        save_scan_data(xrd_matrix, dic)

        # Verify the HDF5 file was created and contains the expected data
        with h5py.File(os.path.join(current_dir, 'scanproc.h5'), 'r') as h5f:
            # Rest of the code remains the same
            # Verify the shape of the saved data
            saved_data = h5f['proc/intensities'][:]
            self.assertEqual(saved_data.shape, xrd_matrix.shape)

            # Verify the values of the saved data
            self.assertTrue(np.array_equal(saved_data, xrd_matrix))

if __name__ == '__main__':
    unittest.main()
'''Author: Andrew Martin
Creation Date: 25/7/23

Function to load in the afterpulse file in the required format for calibrate_ingested().
'''

import numpy as np
import xarray as xr

def load_overlap(fname_overlap):
    '''Function to load the overlap profile for the calibration process.
    Code is taken from the original load_o_a_s function in workflows/create_ingested.py

    INPUTS:
        fname_overlap : string, None
            Full filename for the overlap data. If None, defaults to the Turner values.
    
    OUTPUTS:
        overlap : xr.DataArray | (2,k) np.ndarray
            Object containing the overlap function data for use in calibrate_ingested.
            If an xarray DataArray, it must have a single dimension 'height'.
            Otherwise, if a numpy ndarray, must have [0,:] be height values and [1,:] be the corresponding overlap corrections.
            
        source : string
            String describing where the data for the overlap has come from.
    '''
    if fname_overlap is not None:
        source = fname_overlap
        raise NotImplementedError('loading of overlap function not supported yet.')
    else:
        source = 'David Turner values from 31/01/2011.'
        ocorr = np.array([0.00530759, 0.0583835, 0.110524, 0.174668, 0.246036, 0.333440, 0.421466,0.510560, 0.599191, 0.676644, 0.744512, 0.808004, 0.848976,0.890453, 0.959738, 0.975302, 1.0, 1.0])
        oht = np.array([0.0149896, 0.164886, 0.314782, 0.464678, 0.614575, 0.764471, 0.914367,1.06426, 1.21416, 1.36406, 1.51395, 1.66385, 1.81374, 1.96364,2.11354, 2.26343, 2.5, 20]) * 1e3
        overlap = np.vstack((oht, ocorr))

    return overlap, source
    
'''Author: Andrew Martin
Creation date: 25/7/23

Function to load in an afterpulse file for use in steps.calibrate_ingested()
'''

import numpy as np
import xarray as xr

def load_afterpulse(fname_afterpulse):
    '''Function to load in the afterpulse profiles for use in steps.calibrate_ingested()
    Code is copied from workflows/create_ingested.load_o_a_s()
    
    INPUTS:
        fname_afterpulse : string, None
            Full filename for the afterpulse file. If None, will return None values (no afterpulse correction).

    OUTPUTS:
        afterpulse : xr.Dataset
            xarray dataset containing the vertical "height" coordinate, and the channel_1, channel_2 and E0 variables.
    '''
    afterpulse = None
    source = None
    if fname_afterpulse is not None:
        source = fname_afterpulse
        afterpulse = xr.load_dataset(fname_afterpulse)

    return afterpulse, source
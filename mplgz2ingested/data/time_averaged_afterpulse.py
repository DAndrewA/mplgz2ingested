'''Author: Andrew Martin
Creation date: 30/7/23

Script to allow the loading of the default time-averaged afterpulse profile.
'''

import xarray as xr
import os

def time_averaged_afterpulse():
    '''Function to load the default afterpulse profile.
    
    OUTPUTS:
        afterpulse : xarray.Dataset
            xarray dataset containing the requiree afterpulse profiles required for calibrate_ingested

        source : string
            description of source of afterpulse profiles.
    '''
    script_dir = os.path.abspath( os.path.dirname(__file__) )

    source = 'Energy-weighted time average of all afterpulse files from 2016012613 to 2023041213.'
    afterpulse = xr.load_dataset(os.path.join(script_dir,'time_averaged_afterpulse.cdf'))
    return afterpulse, source
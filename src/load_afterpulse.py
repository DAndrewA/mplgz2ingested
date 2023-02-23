'''Author: Andrew Martin
Date created: 16/2/23

Script to load in an afterpulse file and format it ready for use in calibrate_ingested.py.
'''

import load_mpl_inline
import raw_to_ingested
import xarray as xr
import numpy as np

def load_afterpulse(fname, energy_weighted=True):
    '''Function to load an afterpulse file from .mpl.gz format.
    https://www.arm.gov/publications/tech_reports/doe-sc-arm-tr-098.pdf

    INPUTS:
        fname : string
            Full filename for the afterpulse file being loaded

        energy_weighted : boolean
            If true, the afterpulse signal is weighted by the emitter energy, otherwise, a simple mean is taken.

    OUTPUTS:
        afterpulse : xr.Dataset
            Dataset containing the afterpulse profile in both channels at given height coordinates.    
    '''

    ds = load_mpl_inline.load_mpl_inline(fname)
    ds = raw_to_ingested.raw_to_ingested(None, None, data_loaded=ds)
    
    E0 = ds.energy.mean(dim='time')
    if energy_weighted:
        # a weighted average is taken as according to (Campbell 2002)
        E_ratio = ds.energy / E0
        aft1 = (ds.backscatter_1 * E_ratio).sum(dim='time') / E_ratio.sum()
        aft2 = (ds.backscatter_2 * E_ratio).sum(dim='time') / E_ratio.sum()
    else:
        aft1 = ds.backscatter_1.mean(dim='time')
        aft2 = ds.backscatter_2.mean(dim='time')

    afterpulse = xr.Dataset()
    afterpulse['channel_1'] = aft1
    afterpulse['channel_2'] = aft2
    afterpulse['E0'] = E0

    afterpulse.assign_attrs({'source_file': fname})

    return afterpulse
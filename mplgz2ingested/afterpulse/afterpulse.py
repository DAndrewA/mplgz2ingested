'''Author: Andrew Martin
Date created: 16/2/23

Script to load in an afterpulse file and format it ready for use in calibrate_ingested.py.
'''

from . import load
from . import raw_to_ingested
import xarray as xr
import numpy as np
import os
import datetime as dt

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

    ds = load.load_mplgz(fname)
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


def get_all_from_catalogue(catalogue, fname_fmt='%Y%m%d%H%M.mpl.gz'):
    '''Funciton to get all filenames and dates of valid afterpulse files from a catalogue.
    
    INPUTS:
        catalogue : string
            filename for the afterpulse catalogue to extract filenames from

        fname_fmt : string
            filename format for the afterpulse files, to allow for dt.datetime objects to be created.

    OUPUTS:
        fnames : list [strings]
            list of filenames for the afterpulse files

        datelist : list [dt.datetime]
            list of dt.datetime objects, corresponding to when the afterpulse files were recorded.
    '''
    f = open(catalogue, 'r')
    fnames = f.read().split(', ')
    f.close()
    datelist = [dt.datetime.strptime(fn,fname_fmt) for fn in fnames]
    return fnames, datelist


def get_all_afterpulse_candidates(dir_root):
    '''Function to get all of the candidate afterpulse files from a directory of .mpl.gz files
    
    INPUTS:
        dir_root : string
            Root directory containing all the .mpl.gz files.

    OUTPUTS:
        calibration_files : list [string]
            List of strinbgs for valid filenames that are candidates for afterpulse files
    '''
    # faster to use os.listdir than os.walk
    calibration_files = []

    for fname in os.listdir(dir_root):
        # this check assumes the end of the filename format end as (YYMMDDHH)mm.mpl.gz and that files generally start on the hour
        if fname[-9:] != '00.mpl.gz':
            if '.mpl.gz' in fname:
                calibration_files.append(fname)

    return sorted(calibration_files)

    
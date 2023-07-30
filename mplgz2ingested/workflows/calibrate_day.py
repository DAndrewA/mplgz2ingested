'''Author: Andrew Martin
Creation Date: 30/7/23

Function to load MPL data for a given date, ingest and calibrate that data.
'''

import datetime as dt
import xarray as xr
import os

from .. import steps

def calibrate_day(date, dir_target, dir_mpl, overwrite=False, fname_afterpulse=None, fname_overlap=None, fname_save_fmt = 'mpl_calibrated_{:04}{:02}{:02}.nc', afterpulse=None, overlap=None, sources=None):
    '''Function to load .mpl.gz files for a given day, and ingest and calibrate the data.

    The afterpulse and overlap data used in the calibration will take on the defauilt values given in the package.
    
    INPUTS:
        date : datetime.date, datetime.datetime
            Object containing a day, month and year field corresponding to the day of data that should be ingested.
        
        dir_target : string
            Path name for directory to save the dataset to.    

        dir_mpl : string
            Path name of the directory containing the .mpl.gz files to be loaded and ingested.

        overwrite : boolean
            Flag for whether or not to overwrite a pre-existing ingested file

        afterpulse : None, string
            If None, the default afterpulse profile will be loaded. If a string, then it must point to a file containing afterpulse data that can be loaded.

        overlap : None, string
            If None, the default overlap profile will be loaded. If a string, then it must point to a file containing overlap data that can be laoded.

        savename_fmt : string
            String containing the format for the filename to be saved, with {year}, {month} and {day} imposed in order.

        afterpulse : None, xarray.Dataset
            If None, then fname_afterpulse will be used to load an afterpulse profile. Otherwise, this overides that, so an afterpulse profile can be pre-provided.

        overlap : None, xr.DataArray, 2xk np.ndarray
            If None, fname_overlap is used to load an overlap function. Otherwise, this overrides the loaded, allowing the pre-loadiong of the overlap function.

        sources : None, dict
            sources for the provided afterpulse and overlap data.

    
    OUTPUTS:
        ds : xarray.Dataset
            Dataset object containing the ingested and calibrated data for the given date.
    '''
    save_fname = fname_save_fmt.format(date.year, date.month, date.day)
    if not overwrite:
        if os.path.isfile(os.path.join(dir_target,save_fname)):
            print(f'{save_fname} already exists in directory {dir_target}.')
            return

    ds = steps.load_fromdate(date, dir_mpl)

    # apply the raw_to_ingested algorithm on the already-loaded ds
    ds = steps.raw_to_ingested(data_loaded=ds)

    # load the afterpulse and overlap data
    if sources is None:
        sources = {}
    if afterpulse is None:
        afterpulse,sa = steps.load_afterpulse(fname_afterpulse)
        sources['afterpulse'] = sa
    if overlap is None:
        overlap,so = steps.load_overlap(fname_overlap)
        sources['overlap'] = so

    # add calibrated variables to the ingested format
    ds = steps.calibrate_ingested(ds, afterpulse=afterpulse, overlap=overlap, sources=sources)

    # now save the dataset as a netcdf file
    ds.to_netcdf(os.path.join(dir_target, save_fname))
    return
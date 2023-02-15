'''Author: Andrew Martin
Date created: 15/2/23

Python script for creating ingested mpl files for a given month.
'''

import datetime
import xarray as xr
import os

import load_mpl_inline
import raw_to_ingested

def create_ingested(date,dir_target,dir_mpl, overwrite):
    '''For a given date, create an ingested file and save it to the target directory.
    
    INPUTS:
        date : datetime.date
            The date for which data should be taken from.
            
        dir_target : string
            The directory into which the file should be saved.

        dir_mpl : string
            The directory from which the .mpl.gz files will be extracted.
            
        overwrite : boolean
            If true, pre-existing ingested files will be overwritten.
    '''
    # check to see if the ingested file already exists, and if it can be overwritten.
    save_fname = f'smtmplpolX1.a1.{date.year:04}{date.month:02}{date.day:02}.000000.cdf'
    if not overwrite:
        if os.path.isfile(os.path.join(dir_target,save_fname)):
            print(f'{save_fname} already exists.')
            return

    # create the filename format from the date
    fname_glob = f'{date.year:04}{date.month:02}{date.day:02}*.mpl.gz'
    print(fname_glob)
    ds = load_mpl_inline.mf_load_mpl_inline(fname_glob, dir_mpl)

    # apply the raw_to_ingested algorithm on the already-loaded ds
    ds = raw_to_ingested.raw_to_ingested(None, None, data_loaded=ds)
    # now save the dataset as a netcdf file
    ds.to_netcdf(os.path.join(dir_target, save_fname))


def create_ingested_month(year, month, dir_target, dir_mpl, overwrite):
    '''Function to call create_ingested() for every day in a month.
    
    INPUTS:
        year : int
            Year for data to be converted.
            
        month : int
            Month for data to be converted.

        dir_target : string
            Directory for the ingested files to be saved to.

        dir_mpl : string
            The directory from which the .mpl.gz files will be extracted.

        overwrite : boolean
            If true, pre-existing ingested files can be overwritten.
    '''
    delta_day = datetime.timedelta(days=1)
    date0 = datetime.date(year=year, month=month, day=1)
    while date0.month == month:
        create_ingested(date=date0, dir_target=dir_target, dir_mpl=dir_mpl, overwrite=overwrite)
        date0 = date0 + delta_day # increment the date



if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Script to convert archived .mpl.gz files to ingested .cdf files for a given month.')

    parser.add_argument('-y', '--year', required=True, type=int, help='The year for the month being converted.')
    parser.add_argument('-m', '--month', required=True, type=int, help='Month for the data being converted, as an integer.')
    parser.add_argument('-t', '--targetdir', default='/gws/nopw/j04/ncas_radar_vol2/data/ICECAPSarchive/mpl/ingested', help='The directory that the ingested files will be saved to.')
    parser.add_argument('-d', '--datadir', default='/gws/nopw/j04/ncas_radar_vol2/data/ICECAPSarchive/mpl/raw', help='The directory from which the raw .mpl.gz data will be extracted.')
    parser.add_argument('-o', '--overwrite', action='store_true', help='Overwrite existing ingested files at targetdir.')

    # an optional argument, if day is passed in then we just do a single day
    parser.add_argument('--day', type=int, help='Optional, specifies a particular day for which the ingestion should be done.')

    args = parser.parse_args()

    year = args.year
    month = args.month
    dir_target = args.targetdir
    dir_mpl = args.datadir
    overwrite = args.overwrite

    day = args.day
    if day is not None:
        date0 = datetime.date(year=year, month=month, day=day)
        create_ingested(date=date0, dir_target=dir_target, dir_mpl=dir_mpl, overwrite=overwrite)
    else:
        create_ingested_month(year=year, month=month, dir_target=dir_target, dir_mpl=dir_mpl, overwrite=overwrite)

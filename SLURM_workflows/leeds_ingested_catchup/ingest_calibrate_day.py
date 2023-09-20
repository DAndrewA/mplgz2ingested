'''Author: Andrew Martin
Creation Date: 20/9/23
Contirbutors:

Script that takes a date_string in the format YYYYMMDD and ingests and calibrates the hourly .mpl.gz files to create a daily cdf file
'''
import mplgz2ingested.steps as mplgz
import xarray as xr

import datetime as dt
import pathlib

import glob

def ingest_calibrate_mpl(date_string, dir_data, dir_out):
    '''Function to ingest a month of hourly .mpl.gz files, and store them as hourly .cdf files that can be loaded in an mf dataset call.
    
    INPUTS:
        date_string: string
            String of the format YYYYMMDD that determines the date of data to be loaded.
            
        dir_data: pathlib.Path
            Path to the directory containing the .mpl.gz raw files.
            
        dir_out: pathib.Path
            The path in which to store the output daily .cdf files        
    '''

    file_list = [f for f in dir_data.glob(f'{date_string}*.mpl.gz')]

    # determine non-calibration files
    non_cal = [f for f in file_list if '00.mpl.gz' in str(f)]
    
    # consider possible calibration cases
    poss_cal = sorted([f for f in file_list if '00.mpl.gz' not in str(f)])
    not_cal = []
    poss_cal.append('nope'*11)
    poss_cal.append('burp'*11)
    poss_cal.append('argh'*11) # stops the algorithm from allowing wrap-arounds if there's 3 or fewer elements in not_cal on the same day...
    if len(poss_cal) <= 3: # if there aren't enough files, abort
        pass
    else:
        for i,f in enumerate(poss_cal):
            if str(f)[:-11] in str(poss_cal[i-1]) and str(f)[:-11] in str(poss_cal[i-2]): # only take files if there's 3 in a row from the same day on non-standard timestamps
                not_cal.append(f)

    file_list = [str(f) for f in sorted(non_cal + not_cal)]

    print(f'{file_list=}')

    ds = mplgz.load_fromlist(file_list, dir_root='')
    ds = mplgz.raw_to_ingested(ds)

    # load the overlap, afterpulse, ready for calibration
    o,so = mplgz.load_overlap(None)
    a,sa = mplgz.load_afterpulse(None)
    sources = {'afterpulse':sa, 'overlap':so}

    ds = mplgz.calibrate_ingested(ds, overlap=o, afterpulse=a, sources=sources)

    save_fname = f'smtmplpolX1.a1.{date_string}.000000.cdf'
    print(f'Saving {dir_out / save_fname} | ',end='')
    
    ds.to_netcdf(dir_out / save_fname)
    print('success')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Ingest a month of hourly .mpl.gz files in the .cdf format.')

    dir_data = '/gws/nopw/j04/icecaps/ICECAPSarchive/mpl/raw'
    dir_target = '/gws/nopw/j04/icecaps/ICECAPSarchive/mpl/leeds_ingested'

    parser.add_argument('-d', '--data', default=dir_data)
    parser.add_argument('-t', '--target', default=dir_target)
    parser.add_argument('-m', '--month', required=True)

    args = parser.parse_args()

    dir_data = args.data
    dir_target = args.target
    date_string = args.month

    dir_data = pathlib.Path(dir_data)
    dir_target = pathlib.Path(dir_target)

    print(f'Running ingest_calibrate_mpl( {date_string=} , {dir_data=}, {dir_target=})')
    ingest_calibrate_mpl(date_string, dir_data, dir_target)
'''Author: Andrew Martin
Date created: 17/2/23

Script to create ingested files with the new format.
Will simply run through every day between two dates and create files for all the given dates.
'''

import xarray as xr
import numpy as np
import os
import datetime

import create_ingested

date_init = datetime.date(2019,1,1)
date_final = datetime.date(2023,2,17)

date0 = date_init

dir_target = '/gws/nopw/j04/ncas_radar_vol2/data/ICECAPSarchive/mpl/leeds_ingested'
dir_mpl = '/gws/nopw/j04/ncas_radar_vol2/data/ICECAPSarchive/mpl/raw'

fname_afterpulse = '/gws/nopw/j04/ncas_radar_vol2/data/ICECAPSarchive/mpl/raw/201907111242.mpl.gz'
overlap, afterpulse, sources = create_ingested.load_o_a_s(None, fname_afterpulse)

sources['afterpulse'] = '201907111242.mpl.gz  --- NOTE: singular file used for all days in this run (17/2/23)'


numfail=0
ntotal=0
while date0 <= date_final:
    ntotal+=1
    try:
        create_ingested.create_ingested(date=date0,dir_target=dir_target, dir_mpl=dir_mpl, afterpulse=afterpulse, overlap=overlap, sources=sources, overwrite=True)
    except:
        print(f'{date0=} failed: presumably no match on glob string')
        numfail +=1

    date0 = date0 + datetime.timedelta(days=1)

print('FINISHED!!!!!')
print(f'{ntotal=}  |  {numfail=}')
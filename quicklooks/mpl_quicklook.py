#%%
import sys
import os
import numpy as np
import xarray as xr
from datetime import datetime, timedelta
from glob import glob
from subprocess import call

import matplotlib.pyplot as plt

#%%
sys.path.append('/home/vonw/work/software/icecaps/mpl/')
import mpl

#%% Sets data directory for MPL data
d = '/mnt/vonw/fieldExperiments/2010-2021_Summit/data/mpl/raw/'

#%%
def unzipMPLfilesFromNOAA(date):
    # Using this function requires the NOAA ESRL ftp site for Summit Station data to be mounted as /mnt/NOAA_ESRL.

    # Identify MPL files to unzip
    yyyymmdd = date.strftime('%Y%m%d')
    os.chdir(d)
    noaa = '/mnt/NOAA_ESRL/mpl/raw/'
    filesToUnzip = noaa + yyyymmdd + '*.mpl.gz'
        
    # Unzip the files
    fns = glob(filesToUnzip)
    fns.sort()
    for fn in fns:
        call(['gunzip -c ' + fn + ' > ' + d + fn.split('/')[-1].split('.')[0] + '.mpl'], shell=True)
    
    return

#%%
def downloadMPLfilesFromNOAA(date):
    # Download MPL files and unzip
    yyyymmdd = date.strftime('%Y%m%d')
    os.chdir(d)
    filesToTransfer = [yyyymmdd + '*.mpl.gz']
    
    # Transfer the MPL files from NOAA public FTP site
    for f in filesToTransfer:
        call(['wget', 'ftp://ftp1.esrl.noaa.gov/psd3/arctic/summit/mpl/raw/' + f])
    
    # Unzip the files
    fns = glob(d+'*.gz')
    fns.sort()
    for fn in fns:
        call(['gunzip', fn])
    
    return

def MPLquicklook(date, normalization=True, overlap=False):
    #
    yyyymmdd = date.strftime('%Y%m%d')
    fns = glob(d+yyyymmdd+'*.mpl')
    fns.sort()
    for fn in fns:
        mpl108 = mpl.MPL(fn)
        mpl108.readData()
        if fn==fns[0]:  # first time thru
            ds = mpl108.to_xarray()
        else:
            ds = xr.concat([ds, mpl108.to_xarray()], dim='time') 
    
    # Apply the Background and Range Normalization
    if(normalization):
        ds['signal_1'] = (ds.backscatter_1 - ds.backscatter_1.sel(height=slice(-3,0)).mean(axis=1)) * ds.height * ds.height
        ds['signal_2'] = (ds.backscatter_2 - ds.backscatter_2.sel(height=slice(-3,0)).mean(axis=1)) * ds.height * ds.height
    
    # Apply the overlap correction
    # ....From Dave Turner: "This overlap correction was a simple estimation using real background subtracted, range corrected data and assuming a linear trend from 2.4 km to the surface using data at 1800 on 31 Jan 2011 at Summit"
    if(overlap):
        ocorr = [0.00530759, 0.0583835, 0.110524, 0.174668, 0.246036, 0.333440, 0.421466, 0.510560, 0.599191, 0.676644, 0.744512, 0.808004, 0.848976, 0.890453, 0.959738, 0.975302, 1.0, 1.0]
        oht = [0.0149896, 0.164886, 0.314782, 0.464678, 0.614575, 0.764471, 0.914367, 1.06426, 1.21416, 1.36406, 1.51395, 1.66385, 1.81374, 1.96364, 2.11354, 2.26343, 2.5, 20]
        olap = np.interp(ds.height, ocorr, oht)

        ds['signal_1'] = ds.signal_1 / olap
        ds['signal_2'] = ds.signal_2 / olap
    
    # MPL quicklook plot for ICECAPS-MELT
    fig, axs = plt.subplots(4, figsize=(8,11), facecolor='w')
    signalUnderLimit = 0
    signalOverLimit  = 1.5

    # Channel 1
    p0=axs[0].pcolormesh(ds.time, ds.height, ds.signal_1.T, vmin=signalUnderLimit, vmax=signalOverLimit, cmap='jet')
    cb0=p0.get_cmap().copy()
    cb0.set_under('k')
    cb0.set_over('w')
    axs[0].set_xticklabels([])
    axs[0].set_xlim(ds.time.min(), ds.time.max())
    axs[0].set_ylim(0,8)
    axs[0].set_ylabel('Altitude [km AGL]')
    axs[0].set_title('ICECAPS MPL Data for '+ date.strftime('%d %b %Y') + ': Signal_1')
    # Channel 2
    p1=axs[1].pcolormesh(ds.time, ds.height, ds.signal_2.T, vmin=signalUnderLimit, vmax=signalOverLimit, cmap='jet')
#    p1.set_cmap('jet')
#    p1.set_clim(signalUnderLimit,signalOverLimit)
    cb1=p1.get_cmap().copy()
    cb1.set_under('k')
    cb1.set_over('w')
    axs[1].set_xlim(ds.time.min(), ds.time.max())
    axs[1].set_xticklabels([])
    axs[1].set_ylim(0,8)
    axs[1].set_ylabel('Altitude [km AGL]')
    axs[1].set_title('ICECAPS MPL Data for '+ date.strftime('%d %b %Y') + ': Signal_2')
    # Instrument temperatures
    axs[2].plot(ds.time, ds.telescopeTemp, 'b')
    axs[2].plot(ds.time, ds.detectorTemp, 'k')
    axs[2].plot(ds.time, ds.laserTemp, 'r')
    axs[2].set_xticklabels([])
    axs[2].set_xlim(ds.time.min(), ds.time.max())
    axs[2].set_ylabel('Temperature [C]')
    axs[2].grid()
    axs[2].legend(['Telescope', 'Detector', 'Laser'], loc='best')
    axs[2].set_title('Instrument Temperatures')
    # Laser energy
    axs[3].plot(ds.time, ds.energyMonitor, 'k')
    axs[3].set_xlim(ds.time.min(), ds.time.max());
    axs[3].set_xlabel('Hour [UTC]')
    axs[3].set_ylim(0,6)
    axs[3].set_ylabel('Laser Energy [micro Joules]')
    axs[3].grid()
    axs[3].set_title('Laser Output Energy');
    xmin, xmax = axs[3].get_xlim()
    axs[3].hlines(y=4.2, xmin=xmin, xmax=xmax, color='r', linestyle='dotted', linewidth=1)

    btime = str(ds.time[0].values)[11:13]+str(ds.time[0].values)[14:16]+str(ds.time[0].values)[17:19]
    fig.savefig('/mnt/vonw/fieldExperiments/2010-2021_Summit/quicklooks/mpl/smtmpl_quicklook.'+yyyymmdd+'.'+btime+'.png')
    return

def cleanUpMPLfiles(date):
    os.chdir(d)
    fns = glob('*.mpl')
    for fn in fns:
        os.remove(fn)
    return


# %%

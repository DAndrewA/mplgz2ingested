#%%
import sys
from datetime import datetime, timedelta
from pandas import date_range

sys.path.append('/home/vonw/work/software/icecaps/mpl/')
import mpl_quicklook

#%%
#######################################################
#%% Use for yesterday
date = datetime.today() - timedelta(days=1)
#mpl_quicklook.unzipMPLfilesFromNOAA(date)
mpl_quicklook.downloadMPLfilesFromNOAA(date)
mpl_quicklook.MPLquicklook(date)
mpl_quicklook.cleanUpMPLfiles(date)

######################################################
#%% Use for multiple dates
#dates = date_range('2023-08-13', '2023-08-13')
#for date in dates:
#    print('Processing: ', date)
##    mpl_quicklook.unzipMPLfilesFromNOAA(date)
#    mpl_quicklook.downloadMPLfilesFromNOAA(date)
#    mpl_quicklook.MPLquicklook(date)
#    mpl_quicklook.cleanUpMPLfiles(date)

# %%

'''Author: Andrew Martin
Creation Date: 20/9/23

Script to schedule SLURM jobs on JASMIN to ingest raw data and create daily .cdf files for every day since the last daily file present in leeds_ingested on the ICECAPS archive on JASMIN.
'''

import os
import glob
import datetime as dt

dir_data = '/gws/nopw/j04/icecaps/ICECAPSarchive/mpl/raw'
dir_target = '/gws/nopw/j04/icecaps/ICECAPSarchive/mpl/leeds_ingested'

queue = 'short-serial'
timemax = '00:05:00' # in hh:mm:ss format
outdir = '/work/scratch-nopw2/eeasm'
memreq = '5G'
#ncores = 4


# determine the latest file in the leeds_ingested archive
glob_str = '*.000000.cdf'
existing_file_list = glob.glob(os.path.join(dir_target,glob_str))

latest = sorted(existing_file_list)[-1][-19:-11]

latest_date = dt.datetime.strptime(latest, '%Y%m%d').date()
one_day = dt.timedelta(days=1)
today = dt.date.today()

iter_date = latest_date + one_day

while iter_date < today:
    date_str = iter_date.strftime('%Y%m%d')
    iter_date += one_day

    jobname = 'mpl_raw_to_cdf'
    jobid = f'mpl_raw_to_cdf_{date_str}'

    cmd = f'sbatch -p {queue} -t {timemax} --mem={memreq} --job-name={jobname} -o {outdir}/{jobid}.out -e {outdir}/{jobid}.err runjob.sh {dir_data} {dir_target} {date_str}'

    print(cmd)
    os.system(cmd)

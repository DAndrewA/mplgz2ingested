#!/bin/bash
dir_data="$1"
dir_target="$2"
date_string="$3"

conda activate mplgz2ingested

# take a day of .mpl.gz files and create a daily .cdf
pythontime ingest_calibrate_day.py --month $date_string # --data $dir_data --target $scratch_folder 
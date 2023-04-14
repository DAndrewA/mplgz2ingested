# mplgz_to_ingested

A package to allow for raw `.mpl` files to be loaded, ingested and calibrated, and then output to netcdf format.

## Installation

Currently, my method of installing is to navigate to the root directory of the repository. Within the desired python environment, then execute the console command 

```pip install -e .```

This will install `mplgz_to_ingested` as an editable package, allowing for further modification.

## Usage

+ `load_mpl_inline`: functions to load raw `.mpl` files into an xarray format.

+ `load_afterpulse`: functions to load raw `.mpl` files into an xarray, and treating them as afterpulse files, return the time-averaged vertical profile in channels 1 and 2.

+ `raw_to_ingested`: functions to take the raw xarray-formatted data, and convert it to the Summit ingested format (created by #########) for backwards compatability.

+ `calibrate_ingested`: functions to takle the ingested xarray-formatted data and calibrate the lidar backscatter for afterpulse, overlap and deadtime corrections. The physical factors pertaining to the instrument itself are also estimated, to get lidar backscatter in physical units.

## To Do

-  Check that `create_ingested` and `run_create_ingested` function correctly now that package structure has changed.
-  Create functionality for loading in data on days with afterpulse files present.
-  Create functionality for loading in data on days where timestamps may overlap.
-  Create quicklooks functionality for afterpulse days and afterpulse profiles.
-  Create list of afterpulse files that appear to occur on cloud-free days.
-  Introduce CF compliancy into the data.
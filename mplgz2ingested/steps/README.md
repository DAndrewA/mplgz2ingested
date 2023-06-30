# `mplgz2ingested.steps`

Sub-package of `mplgz2ingested` containing scripts performing all the individual steps in the process of creating ingested data and calibrating it. 

## Data Format

The loaded data will follow a strict format to faccilitate the easy deve;lopment and deployment of this package. The data structure will be the `xarray.Dataset` object, containing `xarray.DataArray` objects to defined the individual data fields.

The Dataset, which will be denoted as `ds` will hav the dimensions:
+ 
+
+
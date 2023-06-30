# mplgz2ingested

A package to allow for raw `.mpl` files to be loaded, ingested and calibrated, and then output to netcdf format.

## Installation

Currently, my method of installing is to navigate to the root directory of the repository. Within the desired python environment, then execute the console command 

```pip install -e .```

This will install `mplgz_to_ingested` as an editable package, allowing for further modification.

If this fails, ensure `setuptools` is installed in the environment, and that pip in upgraded. These steps can be completed with the commands

```pip install --upgrade pip```
```conda install setuptools```

## Usage
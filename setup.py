from distutils.core import setup

setup(name='mplgz2ingested',
    version='0.1',
    description='Package to load raw .mpl.gz lidar data files and convert them to an ingested format.',
    author='Andrew Martin',
    author_email='eeasm@leeds.ac.uk',
    package_dir = {'mplgz2ingested': 'src'}
)
# `mplgz2ingested.afterpulse`

Sub package that handles the afterpulse calibrations for the MPL data.

## Data format

The afterpulse files are derived from the raw MPL data, but their implementation in the calibration nessesitates that they are handled differently to normal ingested data. For ease of handling, this subpackage allows for the creation of afterpulse datasets that contain the minimal amount of data fields required to replicate results.
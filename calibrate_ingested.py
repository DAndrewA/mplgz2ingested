'''Author: Andrew Martin
Date created: 16/2/23

Script to calibrate the ingested data format.
'''

import xarray as xr
import numpy as np
import copy

def calibrate_ingested(ds, overlap=None, afterpulse=None, deadtime=None, c=299792458, sources=None):
    '''Function to produce calibrated variables for the ingested MPL data format.
    
    The base function used can be found at https://www.orau.gov/support_files/2021ARMASR/posters/P002714.pdf although it should be noted that it uses inconsistent units and doesn't use the available variables derived from the data.

    https://www.arm.gov/publications/tech_reports/doe-sc-arm-tr-098.pdf

    We need to consider the conversion of our data from counts/s to counts/m, and can then apply the afterpulse, overlap and range^2 corrections.

    INPUTS:
        ds : xr.Dataset
            The dataset containing the ingested data format

        overlap : xr.DataArray | 2xk np.ndarray
            A xr.DataArray containing the overlap as a function of given heights;
            OR a 2xk np.ndarray, where [0,:] contains heights and [1,:] contains the overlap function for those corresponding heights.

        afterpulse : xr.Dataset
            Dataset containing the afterpulse profile in both channels for a given height coordinate.

        deadtime : xr.DataArray | 2xj np.ndarray
            An xr.DataArray containing the deadtime correction factor as a function of signal counts (coordinate);
            OR a 2xj np.ndarray where [0,:] contains the signal counts and [1,:] contains the deadtime correction factors for the corresponding signals.

        c : float
            The speed of light in [m/s]

        sources : dict
            Dictionary with the keys being 'afterpulse', 'overlap' and 'deadtime', and their values being strings containing information about the source of the values used.
    
    OUTPUTS:
        ds : xr.Dataset
            The ingested dataset, now with additional variables accounting for the calibration.
    '''
    # variables are given as counts / micro-s, so an additional conversion factor is required. ALSO microjoules to joules
    micro_conv = 1e6

    # boolean flags for if corrections have been given
    used_a = False
    used_o = False
    used_d = False
    # the correction factors may be given on different coordinate scales to the required values for the corrections. In this case, we will linearly interpolate between height/signal values
    if overlap is not None:
        used_o = True
        if type(overlap) == xr.DataArray:
            o = np.interp(ds.height.values, overlap.height.values, overlap.values)
        elif type(overlap) == np.ndarray:
            o = np.interp(ds.height.values, overlap[0,:], overlap[1,:])
        else:
            err_msg = 'overlap must be of type xr.DataArray or of type np.ndarray'
            raise TypeError(err_msg)
        overlap = xr.ones_like(ds.height) * o
    else:
        overlap = xr.ones_like(ds.height)

    if afterpulse is not None:
        used_a = True
        af1 = xr.ones_like(ds.height) * np.interp(ds.height.values, afterpulse.height.values, afterpulse.channel_1.values)
        af2 = xr.ones_like(ds.height) * np.interp(ds.height.values, afterpulse.height.values, afterpulse.channel_2.values)
        E0 = afterpulse.E0
        afterpulse = xr.Dataset()
        afterpulse['channel_1'] = af1 #* 2 / c * micro_conv
        afterpulse['channel_2'] = af2 #* 2 / c * micro_conv
        afterpulse['E0'] = E0
    else:
        afterpulse = xr.Dataset()
        afterpulse['channel_1'] = xr.zeros_like(ds.height)
        afterpulse['channel_2'] = xr.zeros_like(ds.height)
        afterpulse['E0'] = 1

    # TODO: implement deadtime
    if deadtime is not None:
        used_d = True
        raise NotImplementedError('deadtime is not yet implemented.')
    else:
        deadtime = xr.ones_like(ds.backscatter_1)

    
    # for both channels
    for channel in [1,2]:
        
        '''# INITIAL form of NRB calculation
        # start with a conversion to counts per meter
        backscatter_h = ds[f'backscatter_{channel}'] * 2 / c * micro_conv # backscatter
        background_h = ds[f'mn_background_{channel}'] * 2 / c * micro_conv # background
        background_sd_h = ds[f'sd_background_{channel}'] * 2 / c * micro_conv # sd of background
        ##### NRB CALCULATION #####
        NRB = backscatter_h
        if used_d: NRB = NRB * deadtime # apply deadtime correction
        NRB = NRB - background_h # subtract background
        if used_a: NRB = NRB - afterpulse[f'channel_{channel}'] * ds['energy'] / afterpulse['E0'] # subtract afterpulse
        NRB = NRB * np.power(ds.height,2) # range^2 correction
        if used_o: NRB = NRB / overlap # apply overlap correction
        # not applying energy correction as I believe we don't have power as our stored variable...
        #NRB = NRB / ds.energy * micro_conv # # apply energy conversion

        # only interested in NRB above ground [201:] height bin
        NRB = NRB.where(NRB.height > 0)
        '''
        '''
        ##### NRB CALCULATION #####
        # https://journals.ametsoc.org/view/journals/atot/19/4/1520-0426_2002_019_0431_ftesca_2_0_co_2.xml Campbell 2002

        NRB = ds[f'backscatter_{channel}']
        if used_d: NRB = NRB * deadtime # deadtime correction
        NRB = NRB - ds[f'mn_background_{channel}'] # subtract background
        if used_a: NRB = NRB - (afterpulse[f'channel_{channel}'] * ds['energy'] / afterpulse['E0']) # afterpulse correction
        NRB = NRB * np.power(ds.height,2) # range^2 correction
        if used_o: NRB = NRB / overlap # overlap correction
        NRB = NRB / ds['energy'] * micro_conv # pulse energy correction
        '''

        ##### NRB CALCULATION #####
        # This will be according to the Chu Lidar textbook pg192, and my subsequent derivation considering the integration time of the instrument.
        
        # start with the initial backscatter, in counts/s
        NRB = ds[f'backscatter_{channel}']
        if used_d: NRB = NRB * deadtime # deadtime correction
        if used_a: NRB = NRB - (afterpulse[f'channel_{channel}'] * ds['energy'] / afterpulse['E0']) # afterpulse correction
        NRB = NRB - ds[f'mn_background_{channel}'] # background subtraction
        NRB = NRB.where(NRB>0,0) # remove negative NRB values...

        NRB = NRB * np.power(ds['height'],2) # range2 correction
        if used_o: NRB = NRB / overlap # overlap correction
        NRB = NRB / (ds['energy'] / 1e6) # this gets us to the formula in Campbell 2002

        # the next few calculations concern getting the answer into the units sr^-1 m^-1:
        # The scaling factor is (E_photon) / (pulse frequency) / (detector area) / (dz for range bin)
        A_det = np.pi/4 * (0.2032)**2 # 8-inch diameter aperture [m^2]
        dz = np.ediff1d(ds['height']).mean() # difference between succdesive elements should be uniform, but mean taken just in case... [m]
        E_photon = (6.62607e-34)*c / (532e-9) # energy of the photon in [J]
        NRB = NRB * E_photon / dz / A_det
        NRB = NRB / ds['rep_rate']

        # generate attributes for the new variables
        attrs_NRB = ATTRIBUTES_CALIBRATION['NRB']
        attrs_NRB_fmt = ['NOT ']*3
        
        if used_a: # if an afterpulse was given, store it in the dataset
            attrs_NRB_fmt[0] = ''
            attrs_aft = copy.copy(ATTRIBUTES_CALIBRATION['afterpulse'])
            attrs_aft['comment'] = attrs_aft['comment'].format(channel)
            if 'afterpulse' in sources:
                attrs_aft['source'] = sources['afterpulse']

            afterpulse[f'channel_{channel}'] = afterpulse[f'channel_{channel}'].assign_attrs(attrs_aft)
            ds[f'afterpulse_{channel}'] = afterpulse[f'channel_{channel}']
            ds['afterpulse_E0'] = afterpulse['E0']

        if used_o: # if an overlap function was given, store it in the dataset
            attrs_NRB_fmt[1] = ''
            attrs_overlap = copy.copy(ATTRIBUTES_CALIBRATION['overlap'])
            if 'overlap' in sources:
                attrs_overlap['source'] = sources['overlap']
            
            overlap = overlap.assign_attrs(attrs_overlap)
            ds['overlap'] = overlap

        if used_d: # if the deadtime correction was used, store it in the dataset
            attrs_NRB_fmt[2] = ''
            attrs_deadtime = copy.copy(ATTRIBUTES_CALIBRATION['deadtime'])
            if 'deadtime' in sources:
                attrs_deadtime['source'] = sources['deadtime']
            
            deadtime = deadtime.assign_attrs(attrs_deadtime)
            ds['deadtime'] = deadtime

        # assign NRB with correct attributes to dataset
        attrs_NRB['comment'] = attrs_NRB['comment'].format(channel, *attrs_NRB_fmt)
        NRB = NRB.assign_attrs(attrs_NRB)
        ds[f'NRB_{channel}'] = NRB

        # assign variables for the scaling constants
        ds['A_det'] = xr.DataArray(A_det, attrs={'long_name': 'detector area', 'units': 'm^2', 'comment': 'The detector area for a circular 8" aperture, see https://www.arm.gov/publications/tech_reports/handbooks/mpl_handbook.pdf'})
        ds['dz'] = xr.DataArray(dz, attrs={'long_name': 'range bin height', 'units': 'm', 'comment': 'The mean height of the range bins data is collected in, derived from the height variable.'})
        ds['E_photon'] = xr.DataArray(E_photon, attrs={'long_name': 'photon energy', 'units': 'J', 'comment': 'The photon energy in Joules, assuming a monochromatic emission at 532nm.'})

        '''
        # also add background and sd to dataset
        attrs_background = copy.copy(ATTRIBUTES_CALIBRATION['NRB_background'])
        attrs_background['comment'] = attrs_background['comment'].format(channel,channel)
        background_h = background_h.assign_attrs(attrs_background)
        ds[f'NRB_{channel}_background'] = background_h

        attrs_background_sd = copy.copy(ATTRIBUTES_CALIBRATION['NRB_background_sd'])
        attrs_background_sd['comment'] = attrs_background_sd['comment'].format(channel, channel)
        background_sd_h = background_sd_h.assign_attrs(attrs_background_sd)
        ds[f'NRB_{channel}_background_sd'] = background_sd_h
        '''
    return ds



ATTRIBUTES_CALIBRATION = {
    'NRB': {'long_name': 'attenuated backscatter', 'units': 'sr^-1 m^-1', 'comment': 'The backscatter signal for channel {} that has been range-corrected, background corrected, {}corrected for afterpulse, {}corrected for overlap and {}corrected for deadtime effects. Has also been corrected for the detector aperture, pulse energy, etc.'},

    'afterpulse': {'long_name': 'Afterpulse signal', 'units': 'counts m^-1', 'comment': 'The afterpulse signal for channel {}.'},

    'overlap': {'long_name': 'overlap correction factor', 'units': 'unitless', 'comment': 'The overlap correction as a function of height.'},

    'deadtime': {'long_name': 'deadtime correction factor', 'units': 'unitless', 'comment': 'The deadtime correction factor as a function of received signal in counts/m.'},

    'NRB_background': {'long_name': 'Normalised relative backscatter background count', 'units': 'counts m^-1', 'comment': 'The background for the NRB in channel {}. Calculated from the field mn_background_{} * 2 / c * 1e6.'},

    'NRB_background_sd': {'long_name': 'normalised relative backscatter background standard deviation', 'units': 'counts m^-1', 'comment': 'Standard deviation on the NRB background count for channel {}. Calculated from the field sd_background_{} * 2 / c * 1e6.'}
}  

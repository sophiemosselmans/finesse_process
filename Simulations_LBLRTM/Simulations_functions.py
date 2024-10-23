"""
This contains functions needed for when comparing LBLRTM simulations to
FINESSE instrument measurements

Made by sophie using Laura and Sanjee's code"
"""

import numpy as np
from scipy.fftpack import fft, ifft
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import panel_file as panpy
from scipy.io import readsav
import numpy as np
import xarray
import pandas as pd


def apodise_spectrum(
    frequency,
    radiance,
    fre_grid,
    st,
    ed,
    new_pd,
    apodisation_func=False,
    test_delta=False,
):
    """
    Apodise a high resolution spectrum using a boxcar or
    triangle function

    Adapted from apodise_spectra_boxcar_v1.pro
    ;
    ; Original Author: J Murray (14-Oct-2020)
    ;
    ; Additional comments by R Bantges
    ; Version 1: Original
    ;
    Params
    ------
    frequency array
        Original wavenumber scale (cm^-1)
    radiance array
        Original spectrum
    fre_grid float
        The frequency of the  output grid for the apodised spectra (cm^-1)
    st float
        Wavenumber to start apodised spectrum (cm^-1)
    ed float
        Wavenumber to end apodised spectrum (cm^-1)
    new_pd float
        Optical path difference i.e. width of boxcar to apodise (cm)
    apodisation_func string
        deafult=False
        Function to use in addition to boxcar to apodise the spectrum
        Options
        -------
        "triangle" - Triangle function, running from 1 at centre of interferogram
        to zero at edge of interferogram
    test_delta bool
        deafult=False
        If True, the spectrum is taken to be a delta function, can be
        used to test the apodisation. This should return the ILS which is a sinc
        function in the case of a boxcar
        If False input spectrum is used

    Returns
    -------
    wn array
        Wavenumber of apodised spectrum (cm^-1)
    radiance array
        Radiance or transmission of apodised spectrum
        (same units as input)
    """
    # Determine the number of samples making up the output spectra
    samples = int(np.round((ed - st) / fre_grid))

    # Define the wavenumber grid resolution (Fixed high resolution grid.
    # The Monochromatic spectra will be interpolated onto this grid for
    # convenience and potentially reduce time taken for the FFT, the arbitrary
    # number of points in the spectra can be such that it significantly slows
    # the FFT.
    # NB: 0.0001 cm-1 was chosen to resolve the spectral features in the
    # high resolution simulation
    dum_new_res = 0.0001
    dum_samples = int(np.round((ed - st) / dum_new_res))
    # The number of samples in the high res frequency scale

    # ********** Define the arrays for the re-interpolated radiance files **********
    # generate a wavenumber scale running from st - ed wavenumbers
    # at new_res cm-1
    new_fre = np.arange(st, ed, fre_grid)
    # generate a wavenumber scale running from st - ed wavenumbers at 0.001 cm-1
    dum_new_fre = np.arange(st, ed, dum_new_res)
    # ******************************************************************************

    # ********** Interpolate the high res radiance to new array scales **********
    f_dum_spec = interp1d(frequency, radiance)
    dum_spec = f_dum_spec(dum_new_fre)
    if test_delta:
        dum_spec = np.zeros_like(
            dum_spec
        )  # These can be set to produce a delta function to check the sinc
        dum_spec[int(15000000 / 2) : int(15000000 / 2) + 101] = 100.0
    # *****************************************************************************

    # FFT the interpolated LBLRTM spectrum
    int_2 = fft(dum_spec)
    # sampling=1./(2*0.01)/samples/100.   # Sampling interval of the interferogram in cm these are the same for the 0.001 and 0.01 spectra
    sampling = 1.0 / (2 * fre_grid) / samples / 100.0
    # Sampling interval of the interferogram in cm these are the same for the 0.001 and 0.01 spectra

    # ********** Apodise the LBLRTM sim and transform **********
    Q = int(
        round(new_pd / 100.0 / sampling / 2.0)
    )  # number of samples required to extend the path difference to 1.26cm
    # *****************************************************************************

    # Define an array to hold the folded out inteferogram
    int_1 = np.zeros(samples, dtype=np.cdouble)

    # 'int_2' - this interferogram is equivalent to a sampling grid of 0.001 cm-1
    # in the spectral domain, this statement applies a boxcar apodisation over +/-1.26 cm
    int_2[Q:-Q] = 0.0

    # The following two lines reduce the output spectra to a sampling grid of 0.01 cm-1
    # while copying in the truncated interferogram from the high resolution interferogram
    int_1[0 : int(round((samples / 2)))] = int_2[0 : int(round((samples / 2)))]
    int_1[int(round((samples / 2))) : samples] = int_2[
        (dum_samples) - int(round((samples / 2))) : dum_samples
    ]

    if apodisation_func == "triangle":
        print("Apodising with triangle")
        int_1_unapodised = np.copy(int_1)
        triangle_left = [1, 0]
        triangle_left_x = [0, Q]
        triangle_left_x_all = np.arange(len(int_1[0:Q]) + 1)
        f_triangle_left = interp1d(triangle_left_x, triangle_left)
        triangle_right = [0, 1]
        triangle_right_x = [len(int_1) - Q - 1, len(int_1)]
        triangle_right_x_all = np.arange(len(int_1) - Q - 1, len(int_1), 1)
        f_triangle_right = interp1d(triangle_right_x, triangle_right)

        int_1[0 : Q + 1] = int_1[0 : Q + 1] * f_triangle_left(triangle_left_x_all)
        int_1[-Q - 2 : -1] = int_1[-Q - 2 : -1] * f_triangle_right(triangle_right_x_all)

    elif not apodisation_func:
        print("Apodising with boxcar")

    else:
        print("No recognised function selected, defaulting to boxcar")

    new_lbl_spec = ifft(int_1)

    # ***********************************************************************
    apodised_spectra = np.real(new_lbl_spec / (fre_grid / dum_new_res))
    return new_fre, apodised_spectra



# Didn't change anything within the def apply_ILS_sav
def apply_ILS_sav(ILS, start_freq, end_freq, wn, spectrum, pad_length=10):
    """Apply ILS to a spectrum

    Args:
        ILS (array (ILS, frequency bin)): ILS axis 0 is the
            ILS axis 1 is the frequency bin as defined by
            start_fre, end_fre
        start_fre (array): Start frequency for wn bin (cm-1)
        end_fre (array): end frequency for wn bin (cm-1)
        wn (array): wn scale of spectrum (cm-1)
        spectrum (array): spectrum
        padlength (int): amount to add to end of each wavenumber
            section to remove edge effects. Expressed in units of
            wavenumber
    """
    # Specify frequency scale of ILS
    ILS_frequency_scale = np.linspace(-5, 5, np.shape(ILS)[0])

    # Loop through each chunk of spectrum and apply the ILS
    # to that chunk
    for i in range(len(start_freq)):
        # , END_WN, ils_now in zip(
        #     ILS["start_fre_range"],
        #     ILS["end_fre_range"],
        #     ILS["ils_function"],
        # comment out lines 50-54 in Sophie's file as the wavenumber interpolation would no longer be necessary
        # Trim to correct chunk of spectrum
        # Add extra for convolution overlap
        index = np.where(
            np.logical_and(
                wn >= start_freq[i] - pad_length,
                wn <= end_freq[i] + pad_length,
            )
        )
        wn_now = wn[index]
        spectrum_now = spectrum[index]

        # if len(wn_now) == 0:
        #     return None, None  # Or return empty arrays
        
        # Interpolate ILS onto frequency of signal COMMENT OUT LINES BELOW 
        ILS_frequency_scale_interp = np.arange(-5, 5, np.average(np.diff(wn_now)))
        ils_now_interp = np.interp(
            ILS_frequency_scale_interp, ILS_frequency_scale, ILS[:, i]
        )[::-1]
        # convolution below, REPLACED ILS_INTERP WITH WN_NOW

        spectrum_interp = np.convolve(
            spectrum_now,
            ils_now_interp,
            mode="same",
        ) / sum(ils_now_interp)


        # Trim so only spectrum in area of interest is
        # retained
        index_out = index = np.where(
            np.logical_and(
                wn_now >= start_freq[i],
                wn_now < end_freq[i],
            )
        )

        wn_out = wn_now[index_out]
        spectrum_out = spectrum_interp[index_out]
        # plt.cla()
        # plt.plot(wn_now, spectrum_now)
        # plt.plot(wn_now, spectrum_interp)
        # plt.plot(wn_out, spectrum_out)
        # plt.savefig(
        #     "/net/shamal/disk1/lw2214/Water emissivity results/"
        #     + "Water 3/test_convolve_1.png")
        if i == 0:
            wn_all = wn_out
            spectrum_all = spectrum_out
        else:
            wn_all = np.append(wn_all, wn_out)
            spectrum_all = np.append(spectrum_all, spectrum_out)
    return wn_all, spectrum_all



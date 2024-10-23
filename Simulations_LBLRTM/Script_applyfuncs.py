"""
This file takes from Ouput of LBLRTM (TAPE12) to something that can be compared
to our FINESSE measurements

It performs FFT and applies ILS 

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
import Simulations_functions as simf

"STEP 1 LETS LOAD THE TAPE 12 FILE"
panel_data = panpy.panel_file('/net/sirocco/disk1/sm4219/LBLRTM_FOR_SOPHIE/TAPE12', do_load_data = True)

"Direct your final output name"
path_new_out_final = '/net/sirocco/disk1/sm4219/LBLRTM_FOR_SOPHIE/LBLRTM_SIMGA_BOUNDS_40/aposided_RS_542layer_aug13.txt'

# Handy print statements 
# print(panel_data)
# print(panel_data.hdr)
# # print(panel_data.hdr.secant)

"""
If the data is loaded, then object attributes v, data1 are defined for a single panel file, 
and in addition, data2 for a double panel file. 
That is data1 will be radiance and data2 will be the tranmission. 
"""
# what does single panel and double panel mean??? - this bit above is from Laura

# WRITE CODE HERE TO ACCES THE RADIANCES
# print("Radiance values, data 1:", panel_data.data1)
# print("Transmission values, data 2:", panel_data.data2)

rad_in_raw = panel_data.data1
wn_in_raw = panel_data.v


"""
STEP 2 applying FFT to the thing
the original file for this code is: /disk1/sm4219/GIT/fft_for_sophie/fft_for_sophie.py

"""

# wn_in, rad_in  = np.loadtxt("/disk1/sm4219/LBLRTM_FOR_SOPHIE/wavenumbers_radiance.txt",  unpack = True, dtype=np.float64) 

wn_out, rad_out = simf.apodise_spectrum(wn_in_raw, rad_in_raw, 0.2, 300, 1600, 1.21)
# print(wn_out,rad_out)
# np.savetxt('/disk1/sm4219/LBLRTM_FOR_SOPHIE/apodized_wn_IDL_aug.txt',wn_out)
# np.savetxt('/disk1/sm4219/LBLRTM_FOR_SOPHIE/apodized_rad_IDL_aug.txt',rad_out)
print('DONE step 1 FFT')


"""
STEP 3: APPLYING APODIATION ils?
the original code is found at /disk1/sm4219/LBLRTM_FOR_SOPHIE/apodise_finesse.py

"""
# Here I have redefined the start and end fre such that it is an array, to get the bins 
# the function requires the inputs start_fre and end_fre to be arrays of wavenumber rather than float values
# ILS_LOCATION = '/net/fennec-store/disk2/lw2214/Bruker_Data/EM27_ILS.sav'
ILS_LOCATION = '/disk1/sm4219/EM27_ILS.sav'
ils = readsav(ILS_LOCATION)
ILS = ils['em27_ils'][:]

# HERE WE LOAD IN THE VARAIBLES FROM EARLIER FROM STEP 2 
wnT = wn_out
spectrumT = rad_out

print(wnT)

start_fre=np.array([300,350,400,450,560,630,730,850,950,1050,1150,1250,1360,1450,1550])
end_fre=np.array([350,400,450,560,630,730,850,950,1050,1150,1250,1360,1450,1550,1600])

# print(start_fre[0],1950, np.shape(spectrumT)[0])

wnT = np.linspace(300,1600,np.shape(spectrumT)[0]) 

for hour in ['0800_only_radiosonde']: #['0200', '0300', '0400','0500','0600','0700']:
    path = '/net/sirocco/disk1/sm4219/LBLRTM_FOR_SOPHIE/LBLRTM_SIMGA_BOUNDS_40/'
    # wn_B,spectrum_B = np.loadtxt(path+'example_spectrum_joncopy.txt', unpack = True) 
    # /net/sirocco/disk1/sm4219/LBLRTM_FOR_SOPHIE/LBLRTM_SIMGA_BOUNDS_40/apodised_AFTERHAT_9am_comp_new.txt
    # spectrum2 = xarray.DataArray(data = spectrum_B*1E4, dims = ['wn'], 
    #  coords=dict(wn=wn_B))
    # spectrum = rad_jon
    spectrum = spectrumT
    wn = wnT
    # np.linspace(start_fre[0],1950,np.shape(spectrum)[0])     # changed end freq to the final number 
    apodised_wn, apodised_spectrum = simf.apply_ILS_sav(ILS, start_fre, end_fre, wn,
                    spectrum, pad_length=10)
    
    # changed the number here to 8500, in the .interp
    # apodised_interp = xarray.DataArray(data = apodised_spectrum*1E4, dims = ['wn'], coords=dict(wn=apodised_wn)).interp(wn=np.linspace(300,2000,8500))


    np.savetxt(path_new_out_final,np.vstack([apodised_wn, apodised_spectrum]).T)
    # np.savetxt(path+'/apodised_spectra_NEW_old.txt',np.vstack([wn,apodised_interp]).T)

# podised_AFTERHAT_ANDoya.txt", unpack=True)
# print(len(apodised_interp), len(wn))
print('DONE step 2 APODISE')

print('All done and ready to plot', 'saved:', path_new_out_final)
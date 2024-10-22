"""
Calculate spectra from interferograms averaged
in each cycle
"""

from glob import glob
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import calibration_functions_sanjee as cal
from math import floor

# Location and names of files to combine
PATH = '/disk1/Andoya/sp1016/FINESSE_CALIB_SAND_EMISS_UROP/MEASUREMENT_FOLDER_FOR_UROP_TEMP/'
INT_LOCATION = PATH
# RUN NAME is the string at the end of the folder
RUN_NAME = "Measurement"
GUI_DATA_LOCATION = INT_LOCATION + "sand_emissivity1_20240620_081952.csv"

# The AVERAGED_SAVE_LOCATION will be created if it does not already exist
AVERAGED_INT_LOCATION = PATH+f"Processed_Data/prepared_ints/"

DATA_LOCATION = GUI_DATA_LOCATION
SPECTRUM_LOCATION = PATH + "calibrated_spectra/"

Path(SPECTRUM_LOCATION).mkdir(parents=True, exist_ok=True)
OPD = 1.21
OUTPUT_FREQUENCY = 0.0605 / OPD
CAL_OFFSET = 0.2  # K
STRETCH_FACTOR = 1.00016

gui_data = cal.load_gui(GUI_DATA_LOCATION)

# Find all averaged interferogram files
int_list = glob(AVERAGED_INT_LOCATION + "*.txt")
int_list.sort()

#Select which ones
#int_list=int_list[234:]
# Load interferograms and get HBB and CBB temps
ints = []
HBB_temps = []
HBB_std = []
CBB_temps = []
CBB_std = []
angles = []
times = []
total_ints = len(int_list)

for i, name in enumerate(int_list):
    if i % 5 == 0:
        print("Loading %i of %i" % (i, total_ints))
    print(name)
    inter_temp, times_temp, angle_temp = cal.load_averaged_int(name)
    HBB_temp, HBB_std_temp = cal.colocate_time_range_gui(
        gui_data, times_temp, "HBB",)
    CBB_temp, CBB_std_temp = cal.colocate_time_range_gui(
        gui_data, times_temp, "CBB",)
    ints.append(inter_temp)
    times.append(times_temp)
    angles.append(angle_temp)
    HBB_temps.append(HBB_temp)
    HBB_std.append(HBB_std_temp)
    CBB_temps.append(CBB_temp)
    CBB_std.append(CBB_std_temp)

print("Interferograms loaded")
for i, angle in enumerate(angles):
    print(i, angle)

# THIS IS WHERE YOU REMOVE EXTRA INTERFEROGRAMS
# to_delete = [0, 201, 202, 203]
# to_delete = [0, 124]  # water 2
# to_delete = [0, 1, 2, 3, 4, 5, 6, 7, 20, 21, 64, 65]  # water 3
# to_delete = [0, 7, 8, 165, ]  # Water 4
# to_delete.sort(reverse=True)
# to_delete=[0,1]

print(angles)

# for index in to_delete:
#     ints.pop(index)
#     HBB_temps.pop(index)
#     HBB_std.pop(index)
#     CBB_temps.pop(index)
#     CBB_std.pop(index)
#     angles.pop(index)
#     times.pop(index)

# Check all ok
if all((x == 270.0 for x in angles[::6])):
    print("HBB angles ok")
else:
    print(angles[::6])
    print("HBB angles not in expected positions")
    exit()
if all((x == 225.0 for x in angles[1::6])):
    print("CBB angles ok")
else:
    print(angles[1::6])
    print("CBB angles not in expected positions")
    exit()

SCENE_NUMBER = floor(len(ints) / 6)
for i in range(SCENE_NUMBER):
    print("Spectrum %i of %i" % (i + 1, SCENE_NUMBER))
    # Customise for inputs
    HBB_index = i * 6 
    CBB_index = i * 6 + 1
    for x in range(2,6):
        scene_index=i*6+x
        if not angles[HBB_index] == 270.0:
            print("HBB angles wrong")
            exit()
        if not angles[CBB_index] == 225.0:
            print("CBB angles wrong")
            exit()
        (
            wn,
            rad,
            NESR,
            (plus_cal_error, minus_cal_error),
        ) = cal.calibrate_spectrum_with_cal_error(
            ints[scene_index],
            ints[HBB_index],
            ints[CBB_index],
            HBB_temps[HBB_index],
            CBB_temps[CBB_index],
            np.sqrt(HBB_std[HBB_index]**2 + CAL_OFFSET**2),
            np.sqrt(CBB_std[CBB_index]**2 + CAL_OFFSET**2),
            fre_interval=OUTPUT_FREQUENCY,
        )
        # Stretch spectrum by pre calculated amount
        wn = wn*STRETCH_FACTOR
        header = (
            "Spectrum %i of %i including wn stretch\n\n" % (i + 1, SCENE_NUMBER)
            + "Scene\nStart and end times (seconds since midnight)\n"
            + "%.3f %.3f\n" % (times[scene_index][0], times[scene_index][1])
            + "Angle %.2f\n\n" % angles[scene_index]
            + "Hot black body\nStart and end times (seconds since midnight)\n"
            + "%.3f %.3f\n" % (times[HBB_index][0], times[HBB_index][1])
            + "Temperature (C)\n%.3f +/- %.3f\n\n"
            % (HBB_temps[HBB_index], HBB_std[HBB_index])
            + "Cold black body\nStart and end times (seconds since midnight)\n"
            + "%.3f %.3f\n" % (times[CBB_index][0], times[CBB_index][1])
            + "Temperature (C)\n%.3f +/- %.3f\n\n"
            % (CBB_temps[CBB_index], CBB_std[CBB_index])
            + "Wavenumber (cm-1), Radiance, NESR, "
            + "+ve Calibration error, -ve Calibration error"
        )
        print(header, "\n")
        data_out = np.column_stack(
            (wn, rad, NESR, plus_cal_error, minus_cal_error))
        np.savetxt(
            SPECTRUM_LOCATION + "%i.txt" % int(times[scene_index][0]),
            data_out,
            header=header,
        )
        fig,axs = plt.subplots()
        axs.plot(wn,rad)
        axs.set_ylim(0,0.2)
        axs.set_xlim(400,1600)
        axs.set_xlabel('WN (cm$^{-1}$)')
        axs.set_ylabel('Radiance \n (W/m$^2$/sr/cm$^{-1}$)')
        fig.suptitle('Angle '+ str(angles[scene_index]))
        fig.savefig(SPECTRUM_LOCATION +"%i.jpg" % int(times[scene_index][0]), bbox_inches='tight')
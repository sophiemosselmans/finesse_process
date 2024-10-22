"""Calibrate individual interferograms to get a spectrum based on only that one

This code runs but the output response function is totally wrong :)


"""
# %%
import calibration_functions_sanjee as cal
import matplotlib.pyplot as plt
from glob import glob
from pathlib import Path
import numpy as np
import glob

# prepare interferograms from 1_prepare_individual_interferograms.py
# creates a folder with each interferogram from a measurement cycle
DATE = "20230220"
PATH = '/disk1/Andoya/sp1016/'
INT_LOCATION = PATH+ f"Raw_Data/{DATE}/"
# RUN NAME is the string at the end of the folder
RUN_NAME = "zenith_test1"
GUI_DATA_LOCATION = INT_LOCATION + "clear_sky1-20230220103722.log"
gui_data = cal.load_gui(GUI_DATA_LOCATION)

PATH2 = '/disk1/sm4219/GIT/'
# The INDIVIDUAL_SAVE_LOCATION will be created if it does not already exist
INDIVIDUAL_SAVE_LOCATION = PATH2+f"Processed_Data_soph_single/prepared_individual_ints/"
Path(INDIVIDUAL_SAVE_LOCATION).mkdir(parents=True, exist_ok=True)
INDIVIDUAL_SPECTRUM_SAVE_LOCATION = PATH2+ f"PROCESSED_EXAMPLE/Processed_Data/individual_spectra/"

PATH2 = '/disk1/sm4219/GIT/FINESSE_CAL/'
DATA_LOCATION = PATH2+f"/Processed_Data_soph_single/"
# DATA_LOCATION = PATH+f"Processed_Data_FOR_SOPHIE/{DATE}/"
single_INT_LOCATION = "/disk1/sm4219/GIT/FINESSE_CAL/Processed_Data_soph_single/prepared_individual_ints/"
# print(single_INT_LOCATION)
RESPONSE_FUNCTION_LOCATION = DATA_LOCATION \
    + "response_functions/"

Path(RESPONSE_FUNCTION_LOCATION).mkdir(parents=True, exist_ok=True)
# paths to average HBB and CBB
# HBB_PATH = PATH+ f"PROCESSED_EXAMPLE/Processed_Data/prepared_ints/int_59340.txt"
# CBB_PATH = PATH+ f"PROCESSED_EXAMPLE/Processed_Data/prepared_ints/int_59403.txt"

# # path to folder containing individual HBB and CBB interferograms
# HBB_INT_PATH =PATH+  f"PROCESSED_EXAMPLE/Processed_Data/prepared_individual_ints/(2024_06_20_16_28_57)_Measurement/"
# CBB_INT_PATH = PATH+ f"PROCESSED_EXAMPLE/Processed_Data/prepared_individual_ints/(2024_06_20_16_30_00)_Measurement/"

# INT_LOCATION = "/disk1/sm4219/GIT/FINESSE_CAL/Processed_Data_soph_single/prepared_individual_ints/"
# FOLDERS = glob(INT_LOCATION + "*" + RUN_NAME + "/")
# FOLDERS.sort()
# print("Folders", FOLDERS)
FOLDERS = glob.glob(single_INT_LOCATION + "*" + RUN_NAME + "/")
FOLDERS.sort()
print("Folders", FOLDERS)

int_list = []
for folder in FOLDERS:
    int_files = glob.glob(folder + "*.txt")
    int_list.extend(int_files)

int_list.sort()
print("INT files:", int_list)
total_ints = len(int_list)
# # retrieve the relevant HBB and CBB files from the folder
# HBBs = glob(HBB_INT_PATH + "*.txt")
# HBBs.sort()
# CBBs = glob(CBB_INT_PATH + "*.txt")
# CBBs.sort()

OPD = 1.21
OUTPUT_FREQUENCY = 0.0605 / OPD
CAL_OFFSET = 0.2  # K
STRETCH_FACTOR = 1.00016  # not sure the origin of these constants; pulled from 3a_calibrate_spectra_in_cycles

# placeholder lists for spectra
ints = []
HBB_temps = []
HBB_std = []
CBB_temps = []
CBB_std = []
angles = []
times = []
wn_calibrateds = []
rad_calibrateds = []
nesr_calibrateds = []
cal_errors = []

for i, name in enumerate(int_list):
    # as in 3a_calibrate_spectra_in_cycles, get interferogram data
    if i % 5 == 0:
        print("Loading %i of %i" % (i, total_ints))
    
    # print("NAME HERE:",name)
    inter_temp, times_temp, angle_temp = cal.load_single_int(
        name)  # using the function for averaged interferograms, but passing a single (not averaged) interferogram into it
   
    HBB_temp, HBB_std_temp = cal.colocate_time_range_gui(
        gui_data, times_temp, "HBB", )
    CBB_temp, CBB_std_temp = cal.colocate_time_range_gui(
        gui_data, times_temp, "CBB", )
    ints.append(inter_temp)
    times.append(times_temp)
    angles.append(angle_temp)
    HBB_temps.append(HBB_temp)
    HBB_std.append(HBB_std_temp)
    CBB_temps.append(CBB_temp)
    CBB_std.append(CBB_std_temp)

# print("Angles are here:", angles)
cal_sequence = [270,225]
cal_locations = [i for i in range(len(angles))
    if angles[i:i+len(cal_sequence)] == cal_sequence]

RESP_NUMBER = cal_locations
# RESP_NUMBER = len(cal_locations)
print("Number of response functions: ", RESP_NUMBER)
# cal.update_figure(1, size=(15, 15/1.68))
print("Check the callibrations have been found", cal_locations)

cal.update_figure(1, size=(15, 15/1.68))

"Locating the HBB and CBB interferograms"
for i, index in enumerate(cal_locations):
    # print("Response %i of %i" % (i + 1, RESP_NUMBER))
    int_HBB = ints[index]
    int_CBB = ints[index+1]
    HBB = HBB_temps[index]
    CBB = CBB_temps[index+1]
    HBB_error = HBB_std[index]
    CBB_error = CBB_std[index + 1]
    HBB_angle = angles[index]
    CBB_angle = angles[index + 1]
    HBB_times = times[index]
    CBB_times = times[index + 1]
    print("HBB_angle: ", HBB_angle)
    print("HBB temp: ", HBB)
    print("CBB_angle: ", CBB_angle)
    print("CBB temp: ", CBB, "\n")

"Unsure here"
hbb_int = int_HBB
cbb_int = int_CBB

FOLDERS_EXAMINING=FOLDERS[0:1]

for FOLDER in FOLDERS_EXAMINING:  # folders 2, 3 are 50º; folders 4, 5 are 130º; change numbers to whatever folder is desired
    print("processing folder " + str(FOLDER))
    # Find all interferogram files
    int_list = glob.glob(FOLDER + "*.txt")
    int_list.sort()
    total_ints = len(int_list)

    # Load interferograms and get HBB and CBB temps

    # get HBB and CBB average interferograms (used for calibration)
    # hbb_int, hbb_time, hbb_angle = cal.load_averaged_int(HBB_PATH)
    # cbb_int, cbb_time, cbb_angle = cal.load_averaged_int(CBB_PATH)

    for i, name in enumerate(int_list):
        # as in 3a_calibrate_spectra_in_cycles, get interferogram data
        if i % 5 == 0:
            print("Loading %i of %i" % (i, total_ints))
        
        print("NAME HERE:",name)
        inter_temp, times_temp, angle_temp = cal.load_single_int(
            name)  # using the function for averaged interferograms, but passing a single (not averaged) interferogram into it
       
        HBB_temp, HBB_std_temp = cal.colocate_time_range_gui(
            gui_data, times_temp, "HBB", )
        CBB_temp, CBB_std_temp = cal.colocate_time_range_gui(
            gui_data, times_temp, "CBB", )
        ints.append(inter_temp)
        times.append(times_temp)
        angles.append(angle_temp)
        HBB_temps.append(HBB_temp)
        HBB_std.append(HBB_std_temp)
        CBB_temps.append(CBB_temp)
        CBB_std.append(CBB_std_temp)

        # get spectrum and add to lists (technically not all the lists are not used, but are here for completion)
        wn_calibrated, rad_calibrated, nesr_calibrated, (
            plus_cal_error, minus_cal_error) = cal.calibrate_spectrum_with_cal_error(
            inter_temp, hbb_int, cbb_int, HBB_temp, CBB_temp, HBB_std_temp, CBB_std_temp, fre_interval=OUTPUT_FREQUENCY)
        wn_calibrated *= STRETCH_FACTOR  # apply pre-determined stretch factor
        wn_calibrateds.append(wn_calibrated)
        rad_calibrateds.append(rad_calibrated)
        nesr_calibrateds.append(nesr_calibrated)
        cal_errors.append((plus_cal_error, minus_cal_error))
        print(angle_temp)

# %%
    # get NESR according to correct method
    # This currently looks at the RMS of the NESR between all 40 measurements you're looking at.
print('Calculating NESR')
nesr_calibrateds = cal.calculate_nesr(wn_calibrateds, rad_calibrateds)

hbb_time = HBB_times
cbb_time = CBB_times

for FOLDER in FOLDERS_EXAMINING:  # folders 2, 3 are 50º; folders 4, 5 are 130º; change numbers to whatever folder is desired
    print("processing folder " + str(FOLDER))
    int_list = glob.glob(FOLDER + "*.txt")
    int_list.sort()
    total_ints = len(int_list)
    Path(INDIVIDUAL_SPECTRUM_SAVE_LOCATION+FOLDER[len(INT_LOCATION):]).mkdir(parents=True, exist_ok=True)

    for i, name in enumerate(int_list):
        wn_calibrated = wn_calibrateds[i]
        rad_calibrated = rad_calibrateds[i]
        nesr_calibrated = nesr_calibrateds
        (plus_cal_error, minus_cal_error) = cal_errors[i]
        # output data (same way as in 3a_calibrate_spectra_in_cycles)
        data_out = np.column_stack(
            (wn_calibrated, rad_calibrated, nesr_calibrated, plus_cal_error, minus_cal_error))

        SCENE_NUMBER = i  # not sure about these, so just leaving them as the counter
        scene_index = i

        header = (
                "Spectrum %i of %i including wn stretch\n\n" % (i + 1, SCENE_NUMBER)
                + "Scene\nStart and end times (seconds since midnight)\n"
                + "%.3f %.3f\n" % (times[scene_index][0], times[scene_index][1])
                + "Angle %.2f\n\n" % angles[scene_index]
                + "Hot black body\nStart and end times (seconds since midnight)\n"
                + "%.3f %.3f\n" % (hbb_time[0], hbb_time[1])
                + "Temperature (C)\n%.3f +/- %.3f\n\n"
                % (HBB_temps[i], HBB_std[i])
                + "Cold black body\nStart and end times (seconds since midnight)\n"
                + "%.3f %.3f\n" % (cbb_time[0], cbb_time[1])
                + "Temperature (C)\n%.3f +/- %.3f\n\n"
                % (CBB_temps[i], CBB_std[i])
                + "Wavenumber (cm-1), Radiance, NESR, "
                + "+ve Calibration error, -ve Calibration error"
        )

        np.savetxt(
            INDIVIDUAL_SPECTRUM_SAVE_LOCATION +FOLDER[len(INT_LOCATION):] + "%i.txt" % int(times[scene_index][0]),
            data_out,
            header=header,
        )

        fig, axs1 = plt.subplots(nrows=2)
        fig.tight_layout()
        axs=axs1[0]
        axs.plot(wn_calibrated, rad_calibrated)
        axs.set_ylim(0, 0.2)
        axs.set_xlim(400, 1600)
        axs.set_xlabel('WN (cm$^{-1}$)')
        axs.set_ylabel('Radiance \n (W/m$^2$/sr/cm$^{-1}$)')

        axs=axs1[1]
        axs.plot(wn_calibrated, nesr_calibrated,label='NESR')
        axs.plot(wn_calibrated, plus_cal_error,label='+CAL')
        axs.set_ylim(0, 0.2)
        axs.set_xlim(400, 1600)
        axs.set_xlabel('WN (cm$^{-1}$)')
        axs.set_ylabel('Error \n (W/m$^2$/sr/cm$^{-1}$)')
        axs.legend()
        fig.suptitle('Angle ' + str(angles[scene_index]))
        fig.savefig(INDIVIDUAL_SPECTRUM_SAVE_LOCATION + FOLDER[len(INT_LOCATION):]+ "%i.jpg" % int(times[scene_index][0]), bbox_inches='tight')
        plt.close(fig)



# %%

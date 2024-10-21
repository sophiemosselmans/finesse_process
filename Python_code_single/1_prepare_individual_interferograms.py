"""
Prepare interferograms for use in calibration
Produces interferograms averaged for each scan cycle
"""

from glob import glob
from pathlib import Path
from matplotlib import pyplot as plt
import numpy as np
import calibration_functions_sanjee as cal

# Location and names of files to combine
PATH = '/disk1/Andoya/sp1016/FINESSE_CALIB_SAND_EMISS_UROP/MEASUREMENT_FOLDER_FOR_UROP_TEMP/'
INT_LOCATION = PATH
# RUN NAME is the string at the end of the folder
RUN_NAME = "Measurement"
GUI_DATA_LOCATION = INT_LOCATION + "sand_emissivity1_20240620_081952.csv"

# The INDIVIDUAL_SAVE_LOCATION will be created if it does not already exist
INDIVIDUAL_SAVE_LOCATION = PATH+f"PROCESSED_EXAMPLE/Processed_Data/prepared_individual_ints/"
Path(INDIVIDUAL_SAVE_LOCATION).mkdir(parents=True, exist_ok=True)

gui_data = cal.load_gui(GUI_DATA_LOCATION)

FOLDERS = glob(INT_LOCATION + "*" + RUN_NAME + "/")
FOLDERS.sort()

ints: list = []
n: list = []
centre_place: list = []

for FOLDER in FOLDERS:
    print(FOLDER)
    times: list = []

    Path(INDIVIDUAL_SAVE_LOCATION+FOLDER[len(INT_LOCATION):]).mkdir(parents=True, exist_ok=True)

    int_temp, start_end_temp, n_temp, centre_place_temp = cal.average_ints_in_folder_return_individuals(
        FOLDER,
        len_int=57090,
        return_n=True,
        centre_place=True
    )
    ints=int_temp
    # times.append(start_end_temp)
    print('OFFSETTING TIME BY 5 SECONDS)')
    for t in start_end_temp:
        times.append(t-5)
    n=n_temp
    centre_place=centre_place_temp
    angles = []

    for i, interferogram in enumerate(ints):
        cal.update_figure(1)

        gui_index_start = gui_data["time"].sub(times[i]-1).abs().idxmin()
        gui_index_end = gui_data["time"].sub(times[i]+1).abs().idxmin()
        variable = gui_data.loc[gui_index_start:gui_index_end, 'angle']
        angle, angle_std= np.mean(variable), np.std(variable)
        angles=angle

        header = (
            "Interferogram %i of %i\n" % (i + 1, len(ints))
            + "Start and end times (seconds since midnight)\n"
            + "%.1f " % (times[i])
            + "Mirror angle\n%.1f\n" % angles
        )
        print(header)
        np.savetxt(
            INDIVIDUAL_SAVE_LOCATION +FOLDER[len(INT_LOCATION):]+ "int_%.0f.txt" % times[i],
            interferogram,
            header=header,
        )
        fig1, ax1 = plt.subplots(1,1)
        ax1.plot(interferogram)
        ax1.set(
            title=f"Start time: {times[i]:.0f} Angle: {angles}",
            ylim=(-0.15, 0.15),
            xlim=(20000, 37000)
        )
        fig1.savefig(INDIVIDUAL_SAVE_LOCATION +FOLDER[len(INT_LOCATION):]+ "int_%.0f.png" % times[i])
        plt.close(fig1)

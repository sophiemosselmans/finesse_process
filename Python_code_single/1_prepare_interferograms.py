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

# The AVERAGED_SAVE_LOCATION will be created if it does not already exist
AVERAGED_SAVE_LOCATION =PATH+f"Processed_Data/prepared_ints/"
Path(AVERAGED_SAVE_LOCATION).mkdir(parents=True, exist_ok=True)
AVERAGING_LENGTH = 40

gui_data = cal.load_gui(GUI_DATA_LOCATION)

FOLDERS = glob(INT_LOCATION + "*" + RUN_NAME + "/")
FOLDERS.sort()
print(len(FOLDERS))

# FOLDERS=FOLDERS[-2:-1]

ints: list = []
times: list = []
n: list = []
centre_place: list = []

for FOLDER in FOLDERS:
    int_temp, start_end_temp, n_temp, centre_place_temp = cal.average_ints_in_folder(
        FOLDER,
        len_int=57090,
        return_n=True,
        centre_place=True
    )
    ints.append(int_temp)
    # times.append(start_end_temp)
    print('OFFSETTING TIME BY 5 SECONDS)')
    times.append((start_end_temp[0]-5,start_end_temp[1]-5))
    n.append(n_temp)
    centre_place.append(centre_place_temp)

angles = []
for time in times:
    angle, angle_std = cal.colocate_time_range_gui(gui_data, time, "angle")
    angles.append(angle)

print(angles)

cal.update_figure(1)
for i, interferogram in enumerate(ints):
    header = (
        "Averaged interferogram %i of %i\n" % (i + 1, len(ints))
        + "Start and end times (seconds since midnight)\n"
        + "%.1f %.1f\n" % (times[i][0], times[i][1])
        + "Mirror angle\n%.1f\n" % angles[i]
    )
    print(header)
    np.savetxt(
        AVERAGED_SAVE_LOCATION + "int_%.0f.txt" % times[i][0],
        interferogram,
        header=header,
    )
    fig1, ax1 = plt.subplots(1,1)
    ax1.plot(interferogram)
    ax1.set(
        title=f"Start time: {times[i][0]:.0f} Angle: {angles[i]}",
        ylim=(-0.15, 0.15),
        xlim=(20000, 37000)
    )
    fig1.savefig(AVERAGED_SAVE_LOCATION + "int_%.0f.png" % times[i][0])
    plt.close(fig1)

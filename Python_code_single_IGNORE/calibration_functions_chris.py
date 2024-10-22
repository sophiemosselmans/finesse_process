"""More helper functions for spectrum calibration"""

import calibration_functions_sanjee as cal
import numpy as np


def load_single_int(filename):
    """Load single interferogram produced using
        2_prepare_interferogram.py; adapted from load_average_int

        Args:
            filename (string): Location of interferogram file

        Returns:
            array: interferogram
            array: start time of interfergram (appears twice in the list for consistency with other methods)
            float: mirror angle for interferogram
        """
    interferogram = np.loadtxt(filename)
    with open(filename, "r") as f:
        for i, line in enumerate(f):
            if i == 2:
                times_raw = line
            if i == 3:
                angle_raw = line
            if i > 3:
                break
    times_split = times_raw.split(" ")[1:]
    time = np.array((times_split[0], times_split[0]), dtype=float)
    angle = float(angle_raw[2:-1])
    return interferogram, time, angle


def calculate_nesr_from_bb(bb_ints):
    """DEPRECATED but kept here as a record.

    Find the residual between one interferogram and the average of the other interferograms in a scan
    cycle in order to calculate the NESR. Can be applied to hot or cold blackbody.

    Args:
        bb_ints (np.array): list containing all the interferogram radiances of a blackbody from a single scan cycle

    Returns:
        np.array: NESR for this cycle
    """
    # separate first interferogram from others, and take average of all others
    separated_rad = bb_ints[0]
    rads_to_average = bb_ints[1:]
    average_rad = np.zeros(len(rads_to_average[0]))  # initialise list for averages
    for rads in rads_to_average:
        for j, rad in enumerate(rads):
            average_rad[j] += rad / len(rads_to_average)  # contribute to the average list
    # find difference of radiance at each wavenumber between first interferogram and average interferogram
    nesr = []
    for i in range(len(separated_rad)):
        nesr.append(average_rad[i] - separated_rad[i])
    return np.array(nesr)


def calculate_nesr(wns, rads):
    """Calculate the NESR.

    Args:
        wns (np.array): List of list of wavenumbers for all scans
        rads (np.array): List of list of radiances for all scans at the wavenumber of the same index in wn

    Returns:
        float: NESR
    """
    # get difference between each radiance
    rad_differences = []
    for i in range(len(rads) - 1):
        current_rad = rads[i]
        next_rad = rads[i + 1]
        rad_difference = []
        for j in range(len(current_rad)):
            rad_difference.append(next_rad[j] - current_rad[j])
        rad_differences.append(rad_difference)

    # get the RMS of the differences in rolling 5 cm^-1 bands
    # get indices of the rolling 5 cm^-1 bands
    first_wavenumber = 400
    last_wavenumber = 1605
    indices = []
    for i, wn in enumerate(wns[0]):  # all the wavenumbers for every scan should be the same
        if first_wavenumber < wn < last_wavenumber:
            indices.append([i, i + 100])        # wavenumber increases by 5 cm^-1 after 100 steps

    # get RMS for the radiances inside the bands
    nesr_values = []
    for i, index in enumerate(indices):
        start_index = index[0]
        end_index = index[1]
        # go through all the radiance difference lists, get RMS for each list, then take square root of mean RMS
        rms_for_each_scan = []
        for j, rad_difference_list in enumerate(rad_differences):
            # get RMS of radiance differences in this wavenumber range for this scan
            relevant_square_rad_differences = []
            for rad_difference in rad_difference_list[start_index:end_index]:
                relevant_square_rad_differences.append(rad_difference ** 2)     # square the difference to get RMS later
            # take mean and square root to get RMS
            rms_for_each_scan.append(np.sqrt(np.mean(relevant_square_rad_differences)))
        # take mean of RMS for each scan, then take square root to get NESR
        nesr = np.sqrt(np.mean(rms_for_each_scan))
        # return with the start index (which is the index for which this NESR is valid)
        nesr_values.append([start_index, nesr])

    # create a list with NESR values between the first and last wavenumber. Outside of those bounds, return nan
    nesr = []
    for i in range(len(wns[0])):
        if indices[0][0] <= i <= indices[-1][0]:
            nesr.append(nesr_values[i-indices[0][0]][1])
        else:
            nesr.append(np.nan)

    return nesr

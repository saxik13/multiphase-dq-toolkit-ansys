import math


def compute_mech_offset_from_winding(inputs):

    Q = inputs.params["slot_number"]# number of slots
    p = inputs.params["pole_pairs"]        # pole pairs
    m = inputs.params["num_phases"]        # phases
    u2 = inputs.params["layers"]       # 1 or 2
    ys = inputs.params["coil_pitch"]        # coil pitch (slots)

    alpha_s = p * 360.0 / Q         # electrical angle between slots
    phase_sector = 180.0 / m

    angles = []

    # slot iteration step. for a single-layer winding, the front coil sides are only in odd slots
    step = 1 if u2 == 2 else 2

    for k in range(1, Q + 1, step):

        theta = ((k - 1) * alpha_s) % 180

        # slot belongs to phase A sector
        if 0 <= theta < phase_sector:
            angles.append(theta)

    if not angles:
        raise ValueError("No slots found for phase A. Check winding parameters.")

    theta_avg = sum(angles) / len(angles)

    # shift from slot side to coil axis
    theta_shift = (ys / 2.0) * alpha_s

    phAaxis = theta_avg + theta_shift + alpha_s/2 #in FEM model, the angle 0 deg is between first and last slots
    mech_offset = inputs.params["rotation_sign"]*(phAaxis - 90.0)/p # the north PM location is at 90 el. degrees. For the negative rotation, the stator winding is built inversely by Motor-CAD 
    inputs.params["mechanical_offset_deg"] = mech_offset
    return inputs
from datetime import datetime

def in_fcy(time_str, windows):
    """
    Inputs:
        time_str - time at which the lap was completed "%H:%M:%S.%f"
        windows - array of times in which the FCY was active
    Output:
        T/F flag if in FCY
    """

    t = datetime.strptime(time_str, "%H:%M:%S.%f").time()
    for w in windows:
        start = datetime.strptime(w["start"], "%H:%M:%S.%f").time()
        end = datetime.strptime(w["end"], "%H:%M:%S.%f").time()
        if start <= t <= end:
            return True
    return False
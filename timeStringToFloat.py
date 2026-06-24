def timeStringToFloat(timeString):
    """"
    Input: time in any string fromat (hh:mm:ss.ms, mm:ss.ms, ss.ms) and
    Retrun: a float of the time in ss.ms format
    """
    import re

    if not timeString:
        print("timeString empty")
        return None
    if not re.match(r"^(\d+:)*\d+\.\d+$", timeString):
        print("timeString not in accepted time format")
        return None
    

    timeParts = timeString.split(":")
    if len(timeParts) == 3:
        h = float(timeParts[0])
        m = float(timeParts[1])
        s = float(timeParts[2])
        time = h*3600 + m*60 + s
    elif len(timeParts) == 2:
        m = float(timeParts[0])
        s = float(timeParts[1])
        time = m*60 + s
    else:
        time = float(timeParts[0])

    return time
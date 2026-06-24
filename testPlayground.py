from timeStringToFloat import timeStringToFloat
from FCY_Check import in_fcy

#print(timeStringToFloat("1:10.365"))

window = [
    {"start" : "11:24:34.537",
     "end": "13:24:34.537"},
     {"start" : "15:24:34.537",
     "end": "16:24:34.537"}
]

if in_fcy("12:24:34.537", window):
    print("FCY")
else:
    print("GF")
## Setup ##
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy
import simpy
import gymnasium
import stable_baselines3
import requests
import truststore
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from verifyPython import verify_environment
import json
import re
from timeStringToFloat import timeStringToFloat
from FCY_Check import in_fcy
from webRequest import web_request
from get_dropdown_options import get_dropdown_options
from season_event_select_GUI import season_event_select_GUI
from series_event_select_GUI import series_event_select_GUI

verify_environment()
truststore.inject_into_ssl()


base_url = series_event_select_GUI()
params = season_event_select_GUI(base_url)

selectedSoup, final_url = web_request(base_url, params=params)

## JSON capture ##

jsonFiles = selectedSoup.find_all("a", href = lambda h: h and (hl := h.lower()) and hl.endswith(".json") and "points" not in hl and "01_imsa%20weathertech" in hl and ("time%20cards" in hl or "flagsanalysiswithrcmessages" in hl))

urls = []
relativePaths = []
finalHour = []

for link in jsonFiles:
    urls.append(urljoin(final_url, link["href"]))
    relativePaths.append(link["href"])

for relativePath in relativePaths:
    parts = relativePath.split("/")
    hourString = [part for part in parts if "Hour" in part]
    if hourString:
        if len(finalHour) == 0:
            finalHour = hourString[0]
        else:
            if finalHour < hourString[0]:
                finalHour = hourString[0]

if finalHour:
    filtered = [(rp, url) for rp, url in zip(relativePaths, urls)
          if finalHour.lower() in url.lower() or "practice" in url.lower() or "qualifying" in url.lower()]
else:
    filtered = [(rp, url) for rp, url in zip(relativePaths, urls)
          if "practice" in url.lower() or "qualifying" in url.lower() or "_race" in url.lower()]
sessions = {}

for relativePath, url in filtered:
    parts = unquote(relativePath).split("/")
    parts = [re.sub(r"^\d+_", "", p).replace("_", " ") for p in parts]
    session = next(
        (
            p for p in parts
            if re.search(r"\bpractice\b", p.lower())
            or re.search(r"\bqualifying\b", p.lower())
            or re.search(r"\brace\b", p.lower())
        ),
        None,
    )
    if session:
        session_key = session.title()
        response = requests.get(url,
                                headers={"User-Agent": "Mozilla/5.0"})
        data = json.loads(response.content.decode("utf-8-sig"))
        filename = parts[-1].lower()


        if "time card" in filename:
            sessions.setdefault(session_key, {})["Timing"] = data
        elif "flagsanalysiswithrcmessages" in filename:
            sessions.setdefault(session_key, {})["Flags"] = data
        elif "pit stops time cards" in filename:
            sessions.setdefault(session_key, {})["Pit stop timing"] = data

## Pulling Data from JSON ##

car = {}
fcy_windows = []
current_start = None

for session_key in sessions:
    fcy_windows = []
    current_start = None
    timing = sessions[session_key]["Timing"]
    flags = sessions[session_key].get("Flags")
    if flags is None:
        fcy_windows = []
    else:
        for entry in flags["flags"]:
            rec_type = entry["rec_type"]
            time = entry["time"]

            if rec_type == "FCY":
                current_start = time

            elif rec_type == "GF" and current_start:
                fcy_windows.append({
                    "start" : current_start,
                    "end" : time
                })
    #print(session_key, "\n", fcy_windows, "\n")
    for participant in timing["participants"]:
        car.setdefault(participant["number"], {
            "lap_times": [],
            "sector_1": [],
            "sector_2": [],
            "sector_3": [],
            "session": [],
            "driver": []
        })
        for lap in participant.get("laps", []):
            if lap["is_valid"] and not lap["crossing_pit_finish_lane"] and not in_fcy(lap["hour"], fcy_windows):
                lTime = timeStringToFloat(lap["time"])
                driver = lap.get("driver_number", [])
                if lTime is not None:
                    car[participant["number"]]["lap_times"].append(lTime)
                    car[participant["number"]]["session"].append(session_key)
                    car[participant["number"]]["driver"].append(driver)
                    for sector in lap["sector_times"]:
                        sTime = timeStringToFloat(sector.get("time"))
                        if sTime is not None:
                            car[participant["number"]][f"sector_{sector['index']}"].append(sTime)


data = car['31']
drivers = set(data["driver"])

binwidth = 0.1
bins = np.arange(min(data["lap_times"]), max(data["lap_times"])+binwidth, binwidth)

for driver in drivers:
    driver_laptime = [t for t, d in zip(data["lap_times"], data["driver"])
                      if d == driver]
    plt.hist(driver_laptime, bins = bins, alpha = 0.5, label = f"Driver {driver}")

plt.xlabel("Lap Time [s]", fontsize = 12)
plt.ylabel("Probability", fontsize = 12)
plt.title('Car #31 - Watkins Glen - Lap Time Probability')
plt.legend()
plt.show()
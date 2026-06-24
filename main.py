## Setup ##
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy
import simpy
import gymnasium
import stable_baselines3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from verifyPython import verify_environment
import json
import re
from timeStringToFloat import timeStringToFloat
from FCY_Check import in_fcy

verify_environment()

## Web Request ##
response = requests.get("https://imsa.results.alkamelcloud.com/",
                    headers={"User-Agent": "Mozilla/5.0"})
#print("Satus code:", response.status_code, "\n\n")
#print("-- Web PAGE --\n")
#print(response.text)
response.raise_for_status()

## Web Parsing ##
html = response.text
soup = BeautifulSoup(html, "lxml")
eventsSelect = soup.find("select", attrs = {"name": "evvent"})
events = eventsSelect.find_all("option")
seasonsSelect = soup.find("select", attrs = {"name": "season"})
seasons = seasonsSelect.find_all("option")

season_options = []
event_options = []
for option in seasons:
    season_options.append((option.text.strip(), option["value"]))
for option in events:
    event_options.append((option.text.strip(), option["value"]))

## User Selection ##
print("-- Seaons --")
for i, (text, value) in enumerate(season_options):
    print(f"{i + 1}. {text}")

seasonChoice = int(input("Select a season (input list number): ")) - 1

print("\n-- Races --")
for i, (text, value) in enumerate(event_options):
    print(f"{i + 1}. {text}")

eventChoice = int(input("Select a race (input list number):")) - 1

selectedSeason = season_options[seasonChoice][1]
selectedEvent = event_options[eventChoice][1]

params = {"season": selectedSeason, "evvent": selectedEvent}

response = requests.get("https://imsa.results.alkamelcloud.com/", params=params)
print(response.url, "\n\n")

## JSON capture ##

slectedHtml = response.text
selectedSoup = BeautifulSoup(slectedHtml, "lxml")

jsonFiles = selectedSoup.find_all("a", href = lambda h: h and (hl := h.lower()) and hl.endswith(".json") and "points" not in hl and "01_imsa%20weathertech" in hl and ("time%20cards" in hl or "flagsanalysiswithrcmessages" in hl))

urls = []
relativePaths = []
finalHour = []

for link in jsonFiles:
    urls.append(urljoin(response.url, link["href"]))
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
plt.title('Car #31 - Sebring - Lap Time Probability')
plt.legend()
plt.show()
# alfred/backend/utils/tools/location_date_tools.py

from datetime import datetime
import parsedatetime
import requests
import os
import time

DEBUG = True

def get_current_date(query: str) -> str:
    """
    Use this tool when you need the current date and/or time to complete a task.
    """
    if DEBUG:
        print(f"ALFRED USING GET CURRENT TIME TOOL")
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def get_lat_lon(city: str):
    """
    Use this tool to turn a location into a lat/lon
    """
    if DEBUG:
        start = time.perf_counter()
    print(f"WEATHER AGENT USING GET LAT LON TOOL FOR {city}")
    url = f"https://api.opencagedata.com/geocode/v1/json?q={city}&key={os.getenv('GEOCODE_API')}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        lat = data['results'][0]['geometry']['lat']
        lon = data['results'][0]['geometry']['lng']
        if DEBUG:
            print(f"Lat Lon Raw Data: {data}")
            print(f"LAT LON: {lat},{lon}")
            duration = time.perf_counter() - start
            print(f"[DEBUG] get_lat_lon took: {duration:.2f}s")
        return lat, lon
    else:
        return None, None
    
def parse_date(text):
    """
    Use this to parse natural language dates.
    """
    if DEBUG:
        print(f"[DEBUG] parse_date text input: {text}")
    cal = parsedatetime.Calendar()
    time_struct, parse_status = cal.parse(text)
    if parse_status == 0:
        raise ValueError("Could not parse date")
    return datetime(*time_struct[:6])
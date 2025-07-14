# alfred/backend/utils/tools/location_date_tools.py

from datetime import datetime
import parsedatetime
import requests
import os
import time
from config import DEBUG, DEEP_DEBUG

def get_current_date(query: str) -> str:
    """
    Use this tool when you need the current date and/or time to complete a task.
    """
    if DEBUG:
        print(f"[DEBUG] Using get_current_date TOOL\n")
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def get_lat_lon(city: str):
    """
    Use this tool to turn a location into a lat/lon
    """
    if DEBUG:
        start = time.perf_counter()
        print(f"[DEBUG] Using get_lat_lon TOOL for {city}\n")

    url = f"https://api.opencagedata.com/geocode/v1/json?q={city}&key={os.getenv('GEOCODE_API')}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        lat = data['results'][0]['geometry']['lat']
        lon = data['results'][0]['geometry']['lng']
        formatted = data['results'][0].get('formatted', '')
        if DEEP_DEBUG:
            print(f"[DEEP_DEBUG] get_lat_lon RAW DATA: {data}")
        if DEBUG:
            # Minimal info
            print(f"[DEBUG] LAT LON: {lat},{lon} - {formatted}")
            # Only full dump if DEEP_DEBUG is True
            duration = time.perf_counter() - start
            print(f"[DEBUG] get_lat_lon took: {duration:.2f}s\n")
        return lat, lon
    else:
        return None, None
    
def parse_date(text):
    """
    Use this to parse natural language dates.
    """
    if DEBUG:
        print(f"[DEBUG] parse_date text input: {text}\n")
    cal = parsedatetime.Calendar()
    time_struct, parse_status = cal.parse(text)
    if parse_status == 0:
        raise ValueError("Could not parse date")
    return datetime(*time_struct[:6])
# alfred/backend/utils/tools/weather_tools.py

from .location_date_tools import get_lat_lon
from datetime import datetime
import requests
import os
import time
from langchain_core.tools import tool

default_location = os.getenv('LOCATION')

DEBUG = True

@tool
def get_current_weather(location: str = None):
    """
    Use this tool to get the current weather for a location.
    """
    if DEBUG:
        start = time.perf_counter()
        print("WEATHER AGENT USING GET CURRENT WEATHER TOOL")

    if not location or location == "home":
        location = default_location
    print(f"LOCATION: {location}")

    lat, lon = get_lat_lon(location)

    if lat is None or lon is None:
        return f"Sorry, I couldn't find the weather for {location}."
    params = {
        'lat': lat,
        'lon': lon,
        'appid': os.getenv("WEATHER_API_KEY"),
        'units': 'imperial',
        'lang': 'en'
    }
    url = "http://api.openweathermap.org/data/2.5/weather"
    if DEBUG:
        start_weather = time.perf_counter()
    response = requests.get(url, params=params)
    if DEBUG:
        duration_weather = time.perf_counter() - start_weather
        print(f"[DEBUG] weather_API took {duration_weather:.2f}s")
        print(f'WEATHER API RESPONSE: {response}')
    data = response.json()
    desc = data['weather'][0]['description']
    temp = int(data['main']['temp'])
    humidity = data['main']['humidity']
    city_name = data['name']

    if DEBUG:
        duration = time.perf_counter() - start
        print(f"[DEBUG] get_current_weather took {duration:.2f}s")

    print(f"CITY NAME: {city_name}. DESCRIPTION: {desc}, TEMP: {temp}, HUMIDITY: {humidity}")
    return f"{city_name} | {desc} | {temp}F | Humidity: {humidity}%"

@tool
def get_forecast_weather(location: str = None):
    """
    Use this tool to get the forecast weather for a location.
    """

    if DEBUG:
        start = time.perf_counter()
        print("WEATHER AGENT USING GET FORECAST WEATHER TOOL")

    if not location or location == "home":
        location = default_location
    print(f"LOCATION: {location}")

    lat, lon = get_lat_lon(location)
    if lat is None or lon is None:
        return f"Sorry, I couldn't find the weather for {location}."
    params = {
        'lat': lat,
        'lon': lon,
        'appid': os.getenv("WEATHER_API_KEY"),
        'units': 'imperial',
        'lang': 'en'
    }
    url = "http://api.openweathermap.org/data/2.5/forecast"
    response = requests.get(url, params=params)
    data = response.json()

    daily = {}
    for entry in data['list']:
        dt = entry["dt_txt"][:10]  # Local date in YYYY-MM-DD
        temp = entry['main']['temp']
        sky = entry['weather'][0]['description']
        pop = entry.get("pop", 0)
        if dt not in daily:
            daily[dt] = {'high': temp, 'low': temp, 'sky': sky, 'pop': pop}
        else:
            daily[dt]['high'] = max(daily[dt]['high'], temp)
            daily[dt]['low'] = min(daily[dt]['low'], temp)
            daily[dt]['pop'] = max(daily[dt]['pop'], pop)
    
    forecast = ["date | hi | lo | sky | pop"]
    for day, val in daily.items():
        forecast.append(
            f"{day} | {round(val['high'])} | {round(val['low'])} | {val['sky']} | {round(val['pop'] * 100)}"
        )
    if DEBUG:
        duration = time.perf_counter() - start
        print(f"[DEBUG] get_forecast_weather took {duration:.2f}s")
        print(f"FORECAST: {forecast}")

    return f"Here is the forecast for {location}:\n" + "\n".join(forecast)
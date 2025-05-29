# alfred_v0.1.3/backend/nodes/weather_node.py

import os
import openai
import json
import requests
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import END

model = ChatOpenAI(model="gpt-4o-mini")
default_location = os.getenv('LOCATION')

DEBUG = True

openai.api_key = os.getenv("OPENAI_API_KEY")

#########################################
##########_WEATHER_AGENT_TOOLS_##########
#########################################

def get_lat_lon(city: str):
    """
    Use this tool to turn a location into a lat/lon
    """
    print(f"WEATHER AGENT USING GET LAT LON TOOL FOR {city}")
    url = f"https://api.opencagedata.com/geocode/v1/json?q={city}&key={os.getenv('GEOCODE_API')}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        lat = data['results'][0]['geometry']['lat']
        lon = data['results'][0]['geometry']['lng']
        if DEBUG:
            print(f"LAT LON: {lat},{lon}")
        return lat, lon
    else:
        return None, None

def get_current_weather(location: str):
    """
    Use this tool to get the current weather for a location.
    """
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
    response = requests.get(url, params=params)
    data = response.json()
    desc = data['weather'][0]['description']
    temp = int(data['main']['temp'])
    humidity = data['main']['humidity']
    city_name = data['name']

    if DEBUG:
        print(f"CITY NAME: {city_name}. DESCRIPTION: {desc}, TEMP: {temp}, HUMIDITY: {humidity}")
    return f"The current weather in {city_name} is {desc} with a temperature of {temp}°F, humidity is {humidity}%."

def get_forecast_weather(location: str):
    """
    Use this tool to get the forecast weather for a location.
    """
    print("WEATHER AGENT USING GET FORECAST TOOL")
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
        dt = datetime.fromtimestamp(entry['dt']).strftime("%Y-%m-%d")
        temp = entry['main']['temp']
        sky = entry['weather'][0]['description']
        pop = entry.get("pop", 0)
        if dt not in daily:
            daily[dt] = {'high': temp, 'low': temp, 'sky': sky, 'pop': pop}
        else:
            daily[dt]['high'] = max(daily[dt]['high'], temp)
            daily[dt]['low'] = min(daily[dt]['low'], temp)
            daily[dt]['pop'] = max(daily[dt]['pop'], pop)
    forecast = []
    for day, val in daily.items():
        forecast.append(
            f"{day}: High {round(val['high'])}°F, Low {round(val['low'])}°F, Sky: {val['sky']}, Precipitation: {round(val['pop']*100)}%"
        )
        if DEBUG:
            print(f"FORECAST: {forecast}")

    return f"Here is the forecast for {location}:\n" + "\n".join(forecast)

##########################################
##########_CREATE_WEATHER_AGENT_##########
##########################################

weather_agent = create_react_agent(
    model=model,
    tools=[get_lat_lon, get_current_weather, get_forecast_weather],
    name='weather_agent',
    prompt="""
            You are an expert in the current weather and the forecast weather. You have access to tools that can:
            - Turn a named location into a lat/lon using 'get_lat_lon' to use in other tools 
            - Get the current weather using 'get_current_weather'
            - Get the forecast weather using 'get_forecast_weather'

            If no location is provided, these tools will default to home themselves.

            When you get the information, ALWAYS finish by replying with the final weather or forecast summary in natural language.
            Use the tool outputs directly to summarize your final response. DO NOT respond without the specific weather information
            unless you were unable to find it, then say 'I was unable to find weather information for that location'.

            Example:
            Tool: get_forecast_weather
            Tool Output: "Here is the forecast for Anchorage: ..."
            Final Answer: "Here is the forecast for Anchorage: ..."

            Your job is not complete until you explicitly say the full forecast or advise that you were unable to find the requested
            weather data.
            """
)

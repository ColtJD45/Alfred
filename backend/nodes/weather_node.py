# alfred/backend/nodes/weather_node.py

import os
import openai
import json
import requests
from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from utils.tools.location_date_tools import get_lat_lon
from utils.tools.weather_tools import get_current_weather, get_forecast_weather

model = ChatOpenAI(model=os.getenv('OPENAI_MODEL'))
default_location = os.getenv('LOCATION')
openai.api_key = os.getenv("OPENAI_API_KEY")

DEBUG = True

weather_agent = create_react_agent(
    model=model,
    tools=[get_lat_lon, get_current_weather, get_forecast_weather],
    name='weather_agent',
    prompt="""
            You are an expert in the current weather and the forecast weather. You have access to tools that can:
            - Get the current weather using 'get_current_weather'
            - Get the forecast weather using 'get_forecast_weather'
            - Get the rest of the forecast weather for 'today' using 'get_forecast_weather'

            If no location is provided, these tools will default to home themselves.

            When you get the information, ALWAYS finish by replying with the final weather or forecast summary in natural 
            language. Use the tool outputs directly to summarize your final response. DO NOT respond without the specific 
            weather information unless you were unable to find it, then say 'I was unable to find weather information for
            that location'.

            Example:
            Tool: get_forecast_weather
            Tool Output: "Here is the forecast for Anchorage: ..."
            Final Answer: "Here is the forecast for Anchorage: ..."

            Your job is not complete until you explicitly say the full forecast or advise that you were unable to find 
            the requested weather data.

            If the user is asking for current weather, use the get_current_weather tool.
            """
)

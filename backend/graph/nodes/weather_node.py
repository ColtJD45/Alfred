# alfred/backend/graph/nodes/weather_node.py

import os
import time
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from graph.state import State
from utils.tools.weather_tools import get_current_weather, get_forecast_weather

DEBUG = True

default_location = os.getenv("LOCATION")
weather_tools = [get_current_weather, get_forecast_weather]

#llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL"))
llm = ChatOllama(model=os.getenv("OLLAMA_MODEL"))
llm_with_tools = llm.bind_tools(weather_tools)

sys_msg = SystemMessage(content=f"""
    You are a helpful assistant tasked with retrieving weather information: current or forecast.
    If no location is given, default to {default_location}.
    """)

def weather_node(state: State):
    if DEBUG:
        start = time.perf_counter()
        print(f"WEATHER NODE STATE: {state}")

    response = llm_with_tools.invoke([sys_msg] + state["messages"])
    new_messages = state["messages"] + [response]

    if DEBUG:
        duration = time.perf_counter() - start
        print(f"WEATHER NODE TOOK {duration:.2f}s")
    return {"messages": new_messages}
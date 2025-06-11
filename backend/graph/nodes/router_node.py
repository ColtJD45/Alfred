# alfred/backend/graph/nodes/router_node.py
from graph.state import State
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
import os
import time

DEBUG = True

#llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL"))
llm = ChatOllama(model=os.getenv("OLLAMA_MODEL"))

system_prompt = """
        You are a fine tuned router. You will take the input and decide whether it should be routed to:
        alfred_node - if the response requires chit chat or general knowledge trained in gpt.
        memory_node - if the response requires any recall of memory or information about the user.
        weather_node - if the response requires information about current or forecast weather.
        task_node - if the user input needs any kind of task management: create a task, delete a task, edit a task, mark a task as completed.
            - in addition, task node can handle reminders and scheduling.
        ONLY respond with one of the following:
            - alfred_node
            - memory_node
            - weather_node
            - task_node
        DO NOT respond with any other words besides the ones above.
        
"""
def router_node(state: State):
    if DEBUG:
        start = time.perf_counter()
        print("DEBUG: Starting router node.")
    last_message = state["messages"][-1].content.lower()
    decision = llm.invoke([
        {"role": "system", "content": system_prompt},
        last_message
    ]).content.strip()
    if DEBUG:
        duration = time.perf_counter() - start
        print(f"ROUTER NODE TOOK {duration:.2f}s")
    print(f"ROUTER DECISION: {decision}")
    return {"next": decision.strip("'")}


    
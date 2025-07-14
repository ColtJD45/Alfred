# alfred/backend/graph/nodes/router_node.py
from graph.state import State
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
from langchain_community.chat_models import ChatOllama
from utils.tools.chat_tools import load_chat_history
import os
import time
from config import DEBUG, DEEP_DEBUG

llm = ChatOpenAI(model=os.getenv("OPENAI_SECONDARY_MODEL", "gpt-3.5-turbo"))
#---llm = ChatOllama(model=os.getenv("OLLAMA_MODEL"))

def router_node(state: State):
    if DEBUG:
        start = time.perf_counter()
        print("DEBUG: Starting router node.\n")
    system_prompt = """
        You are a fine tuned router. Use earlier messages ONLY for context, but make your decision on the last message.
        You will take the input and decide whether it should be routed to:
        alfred_node - if the response requires chit chat or general knowledge trained in gpt.
        memory_node - if the response requires any recall of memory or information about the user.
        weather_node - if the response requires information about current or forecast weather.
        task_node - if the user input needs any kind of task management: create a task, delete a task, edit a task, mark a task as completed.
            - in addition, task node can handle reminders and scheduling.
        ONLY respond with one of the following, DO NOT respond with any other words besides these:
            - alfred_node
            - memory_node
            - weather_node
            - task_node
        """
    user_id = state.get("user_id").lower()
    session_id = state.get("session_id").lower()

    chat_history = load_chat_history(user_id, session_id, 6)
    system_msg = SystemMessage(content=system_prompt)
    all_messages = state["messages"]

    if DEEP_DEBUG:
        print(f"[DEEP_DEBUG] Router_node state input: {all_messages}\n")

    messages = [system_msg] + chat_history + all_messages

    reply = llm.invoke(messages)
    decision = reply.content

    if DEBUG:
        duration = time.perf_counter() - start
        print(f"[DEBUG] Router node took {duration:.2f}s\n")
    print(f"[DEBUG] Router decision: {decision}\n")
    return {"next": decision.strip("'")}


    
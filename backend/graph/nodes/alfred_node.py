# alfred/backend/graph/nodes/alfred_node.py
from graph.state import State
from utils.tools.chat_tools import load_chat_history

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage

import os
import time
from config import DEBUG, DEEP_DEBUG
from datetime import datetime

llm = ChatOpenAI(model=os.getenv("OPENAI_SECONDARY_MODEL"))

def alfred_node(state: State):
    if DEBUG:
        start = time.perf_counter()
        print("[DEBUG] Starting alfred_node\n")
    user_id = state.get("user_id").lower()
    session_id = state.get("session_id").lower()
    today = datetime.now()
    system_prompt = f"""
        Your name is Alfred. You are a personal assistant digital butler. You are always kind and courteous.
        You are sometimes friendly sarcastic. 
        You call the user by {user_id} whenever necessary.
        Today is {today}.
        Take the messages given to you and answer the prompt or summarize the data to respond to the user.
        Output should be plain text only. AVOID using markdown formatting. If the summary is a list of dates, use this format:
            Example:
            Here are your tasks.
            Friday, June 13th - Mow the lawn
            Saturday, June 14th - Wash the dog

    """
    chat_history = load_chat_history(user_id, session_id, 6)
    if DEEP_DEBUG:
        print(f"[DEEP_DEBUG] Alfred_node chat history: {chat_history}\n")

    system_msg = SystemMessage(content=system_prompt)
    all_messages = state["messages"]

    messages = [system_msg] + chat_history + all_messages
    if DEEP_DEBUG:
        print(f"[DEEP_DEBUG] Alfred_node state: {messages}\n")

    reply = llm.invoke(messages)
    if DEBUG:
        duration = time.perf_counter() - start
        print(f"[DEBUG] Alfred_node took {duration:.2f}s\n")

    return {"messages": [{"role": "assistant", "content": reply.content}]}
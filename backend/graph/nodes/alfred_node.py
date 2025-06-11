# alfred/backend/graph/nodes/alfred_node.py
from graph.state import State
from utils.tools.chat_tools import load_chat_history

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage

import os
from datetime import datetime

DEBUG = True

llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL"))

def alfred_node(state: State):
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
    if DEBUG:
        print(f"ALFRED NODE CHAT HISTORY: {chat_history}")
    system_msg = SystemMessage(content=system_prompt)
    all_messages = state["messages"]
    if DEBUG:
        print(f"ALFRED NODE STATE INPUT: {all_messages}")

    messages = [system_msg] + chat_history + all_messages
    if DEBUG:
        print(f"ALFRED STATE: {messages}")

    reply = llm.invoke(messages)

    return {"messages": [{"role": "assistant", "content": reply.content}]}
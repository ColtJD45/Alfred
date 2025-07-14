# alfred/backend/graph/nodes/task_node.py

import os
import time
from config import DEBUG, DEEP_DEBUG
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from graph.state import State
from utils.tools.task_tools import get_tasks
from utils.tools.memory_tools import save_longterm_memory, get_context

default_location = os.getenv("LOCATION")
memory_tools = [get_tasks, save_longterm_memory, get_context]

#llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL"))
llm = ChatOllama(model=os.getenv("OLLAMA_MODEL"))
print(f"OLLAMA MODEL: {llm}")
llm_with_tools = llm.bind_tools(memory_tools)

async def memory_node(state: State):
    if DEBUG:
        start = time.perf_counter()
        print("[DEBUG] Starting memory_node\n")
    if DEEP_DEBUG:
        print(f"[DEEP_DEBUG] Memory node state: {state}\n")

    user_id = state.get("user_id").lower().strip()

    sys_msg = SystemMessage(content=f"""
    You are a helpful assistant expert in memory management. You will help the user retrieve memory based on their prompt.
    ALWAYS RUN A TOOL CALL.
    For the user_id ALWAYS use {user_id}.
    Available tools:
    get_context - use this when you need to search the users preferences or longterm memories
    get_tasks - use this to retrieve a list of tasks for the user, ONLY use for tasks.
    save_longterm_memory - use this when the user wants you to save a longterm memory
                        
    Args:
    get_tasks: 
        user_id: str
    save_longterm_memory:
        user_id: str
        content: str
        summary: str
        tags: list (e.g. "tag1", "tag2", "tag3")
    get_context:
        query: str
        user_id: str
    """)

    response = await llm_with_tools.ainvoke([sys_msg] + state["messages"])
    if DEBUG:
        duration = time.perf_counter() - start
        print(f"[DEBUG] Memory_node took {duration:.2f}s\n")
        print(f"[DEBUG] Memory node response: {response.content}\n")
    new_messages = state["messages"] + [response]
    return {"messages": new_messages}
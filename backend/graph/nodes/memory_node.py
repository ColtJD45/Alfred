# alfred/backend/graph/nodes/task_node.py

import os
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from graph.state import State
from utils.tools.task_tools import get_tasks
from utils.tools.memory_tools import save_longterm_memory, get_context

DEBUG = True

default_location = os.getenv("LOCATION")
memory_tools = [get_tasks, save_longterm_memory, get_context]

#llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL"))
llm = ChatOllama(model=os.getenv("OLLAMA_MODEL"))
print(f"OLLAMA MODEL: {llm}")
llm_with_tools = llm.bind_tools(memory_tools)

def memory_node(state: State):
    print(f"MEMORY NODE STATE: {state}")

    user_id = state.get("user_id").lower().strip()

    sys_msg = SystemMessage(content=f"""
    You are a helpful assistant expert in memory management. You will help the user retrieve memory based on their prompt.
    ALWAYS RUN A TOOL CALL.
    For the user_id ALWAYS use {user_id}.
    Available tools:
    get_tasks - use this to retrieve a list of tasks for the user
    save_longterm_memory - use this when the user wants you to save a longterm memory
    get_context - use this when you need to search the users preferences or longterm memories
                        
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

    response = llm_with_tools.invoke([sys_msg] + state["messages"])
    if DEBUG:
        print(f"TASK AGENT RESPONSE: {response.content}")
    new_messages = state["messages"] + [response]
    return {"messages": new_messages}
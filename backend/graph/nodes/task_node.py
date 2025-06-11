# alfred/backend/graph/nodes/task_node.py

import os
import time
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from graph.state import State
from utils.tools.task_tools import create_new_task, get_tasks, mark_task_completed
from utils.tools.location_date_tools import parse_date
from datetime import datetime

DEBUG = True

default_location = os.getenv("LOCATION")
task_tools = [create_new_task, get_tasks, mark_task_completed, parse_date]

llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL"))
#llm = ChatOllama(model=os.getenv("OLLAMA_MODEL"))
llm_with_tools = llm.bind_tools(task_tools)
today = datetime.now()

def task_node(state: State):
    start = time.perf_counter()
    print(f"TASK NODE STATE: {state}")

    user_id = state.get("user_id").lower().strip()

    sys_msg = SystemMessage(content=f"""
    You are a helpful assistant expert in task management. You will help the user create tasks, retrieve a list of tasks,
    or mark tasks as completed. You must retrieve information out of the prompt to pass to the tool.
    ALWAYS RUN A TOOL CALL.
    NEVER ASK THE USER FOR MORE INFORMATION. DECIDE THE INFORMATION YOURSELF.
    Today is {today}.
    For the user_id ALWAYS use {user_id}.
    Available tools:
    create_new_task - use this to create a new task, include times if given by the user
    get_tasks - use this to retrieve a list of tasks for the user
    mark_task_completed - use this to mark a task as completed
                        
    Args:
    create_new_task: 
        user_id: str (e.g. {user_id})
        category: str (available categories: houshold cleaning, household maintenance, lawncare, laundry, pet_care, personal_care)
        task: str
        date: str (e.g. 'tomorrow', 'thursday', 'june 20th', 'next wednesday', June 22nd at 8:00)
        recurrence: str (e.g. 'once', 'daily', 'weekly', 'monthly', 'bi-weekly')
        notes: str | None
    get_tasks: user_id: str
    mark_task_completed: user_id: str, query: str
    """)

    response = llm_with_tools.invoke([sys_msg] + state["messages"])
    new_messages = state["messages"] + [response]

    if DEBUG:
        print(f"TASK AGENT RESPONSE: {response.content}")
        duration = time.perf_counter() - start
        print(f"TASK NODE TOOK: {duration:.2f}s")

    return {"messages": new_messages}
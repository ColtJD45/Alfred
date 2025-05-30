# alfred/backend/nodes/memory_node.py

import os 
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from utils.tools.memory_tools import (
    check_for_longterm_storage,
    get_context
)

model = ChatOpenAI(model=os.getenv('OPENAI_MODEL'))

memory_agent = create_react_agent(
    model=model,
    tools=[get_context],
    name='memory_agent',
    prompt="""
    You are an expert in memory storage and retrieval. You have access to memory tools that will help you search and filter 
    relevant memories to answer questions or recall facts or events.

    Tool: get_context
        If you are asked to get memory context, use the get_context tool. This tool requires a query, a user_id and a session_id. 
        Use the user_id and session_id that are passed to you in the prompt.
        Tool Use Example: (DO NOT USE THE INPUTS IN THIS EXAMPLE SPECIFICALLY UNLESS IT MATCHES THE USER PROMPT)
        Tool: get_context
        Inputs:
            query: str: Search information about the user's favorite animal.
            user_id: str: Colt
            session_id: str: Colt
        The get_context tool will respond with plain text. Use this plain text for your respons, and also respond in plain text, NOT JSON.
    """
)
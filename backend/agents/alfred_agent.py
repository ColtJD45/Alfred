# alfred_v0.1.3/backend/agents/alfred_agent.py
import os
from langchain.chat_models import ChatOpenAI
from langchain.tools import tool, Tool
from dotenv import load_dotenv
from .state import State
from .memory_llama import MemoryAgent
from utils.tools import (
    create_task, 
    load_longterm_memory, 
    get_current_date, 
    get_context, 
    save_longterm_memory, 
    mark_task_completed,
    get_tasks
)
import json
from datetime import datetime, date
from typing import Dict

load_dotenv() # This loads your .env file to import your secrets.
model = os.getenv('OPENAI_MODEL') # Adjust this to match your .env file where you store your model.
DEBUG = True # One way to use print statements to track the LLM thought process throughout.

class AlfredAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=model,
            openai_api_key=os.getenv('OPENAI_API_KEY'), # Adjust in .env
            temperature=0.7
        )
        self.memory_llama = MemoryAgent()
        self.tools: Dict[str, Tool] = {
            'create_task': Tool(
                name="create_task",
                func=create_task,
                description="Create tasks and reminders"
            ),
            'get_context': Tool(
                name="get_context",
                func=get_context,
                description="Search past conversations and memories"
            ),
            'get_current_date': Tool(
                name="get_current_date",
                func=get_current_date,
                description="Get current date and time"
            ),
            'save_longterm_memory': Tool(
                name="save_longterm_memory",
                func=save_longterm_memory,
                description="Store important information for future reference"
            ),
            'mark_task_completed': Tool(
                name="mark_task_completed",
                func=mark_task_completed,
                description="Mark tasks as completed in the task table in the database"
            ),
            'get_tasks': Tool(
                name="get_tasks",
                func=get_tasks,
                description="Get tasks from the task table in the database by searching user_id, or category, or due_date"
            ),
            
        }

        family_name = os.getenv('FAMILY_NAME')

        self.system_prompt = f"""
            You are Alfred, a sophisticated, sometimes sarcastic, charming, professional butler AI assistant. You are extremely loyal to the {family_name} family. 
            Always maintain a formal, respectful demeanor, while being helpful and attentive. Use the user's name occasionally in a courteous tone. 
            If you are unsure of something, do not guess or hallucinate. Instead, explain that you are uncertain of the answer to the
            question, or how to carry out the task.

            IMPORTANT: Before ever saying you don't know something, first attempt to retrieve relevant information using the `get_context` tool. 
            This gives you access to prior conversations and long-term memory, which may include what you need.

            You have access to the following tools:

            1. get_context — Use to retrieve memory or conversation context. You MUST use this before saying you don't remember or don't know, 
            especially for preferences, past events, or user references to previous chats.
                Tool usage format:
                TOOL: create_task
                INPUT: str: relevant information you need to answer the question or complete the request

                Example (never use this specific information unless it matches the user request):
                User: What is my favorite food?
                TOOL: create_task
                INPUT: I am looking for stored memories containing information about <user>'s favorite food.
                Do not discuss the process of searching and finding the favorite food of the user. Give the user an answer as if you were a friendly
                butler speaking to them and telling them their favorite color.

            2. create_task — Use to schedule reminders or household-related tasks.
                Use get_current_date if you need to determine the relative date of the day requested by the user.
                Tool usage format:
                TOOL: create_task
                INPUT: <user_id>, <category>, <task description>, <due_date YYYY-MM-DD>, <recurrence>, <notes>

                Example (never use this specific information unless it matches the user request):
                You will need to figure out a way to get the current date to find the relative date of the requested schedule day.
                User: Create a task to wash the primary sheets every saturday.
                TOOL: create_task
                INPUT: Colt, cleaning, wash primary sheets, 2025-05-24, weekly

            3. get_current_date — Use when you need to determine the current date or time (e.g., to calculate relative dates for due dates).
                Tool usage format:
                    TOOL: get_current_date
                    INPUT: ""

            4. save_longterm_memory — Use to store significant information the user shares (e.g., personal preferences, routines, 
            changes).

            5. mark_task_completed — Use to mark a task complete once you have identified it using get_tasks.

            6. get_tasks — Use to retrieve current or past tasks, filtered by time, category, or status.

            **Tool format (when invoking):**

            TOOL: <tool_name>  
            INPUT: <structured input string>

            If you decide you need multiple tools, call the first tool and wait for the response. Use that response to decide what 
            you need to call the second tool, whether that be the input for the second tool or you need the response from the first
            tool to calculate what you need for the second tool (example: first tool responds with a date and you use it to calculate
            the relative date of a due date for a task). Call the second tool, then the third and so on if needed. Do not discuss 
            anything with the user until all tool calls are complete. Your responses during tool calling should be through 'process'.

            Do not repeat example scenarios verbatim unless the user's request matches them directly. Always adapt your actions 
            to the actual user request.

            Maintain your butler persona and formal tone at all times.
            """

        
    def process(self, state):
        try:
            user_message = state['messages'][0]['content']
            user_id = state.get('user_id', 'default')

            # First, let the LLM decide if and which tools to use
            response = self.llm.invoke([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ])
            if DEBUG:
                print("LLM raw response:", response.content)

            # Process the response to check for tool usage
            final_response = response.content
            max_tool_loops = 4
            loop_count = 0

            if "TOOL:" in final_response:
                final_response = self.handle_gpt_response(final_response, user_id)
                
                return {
                "messages": [
                    {
                        "role": "assistant",
                        "content": final_response
                    }
                ]
                }
            else:
                return {
                "messages": [
                    {
                        "role": "assistant",
                        "content": final_response
                    }
                ]
                }

        except Exception as e:
            print(f"Error in Alfred's processing: {e}")
            return {"messages": [{"content": "I apologize, but I seem to be experiencing some technical difficulties. How else may I be of assistance?"}]}
    
    def handle_gpt_response(self, response: str, user_id: str):
        if DEBUG:
            print(f"RESPONSE ON HANDLE GPT RESPONSE: {response}")
        if "TOOL:" in response:
            lines = response.strip().split("\n")
            tool_name = None
            tool_input = None
            for line in lines:
                if line.startswith("TOOL:"):
                    tool_name = line.split("TOOL:")[1].strip()
                    if DEBUG:
                        print(f"TOOL NAME: {tool_name}")
                elif line.startswith("INPUT:"):
                    tool_input = line.split("INPUT:")[1].strip()
                    if DEBUG:
                        print(f"TOOL INPUT: {tool_input}")
            
            if tool_name and tool_name in self.tools:
                if tool_name in ['create_task', 'get_tasks', 'get_context', 'save_longterm_memory']:
                    tool_input += f"|{user_id}"

                result = self.tools[tool_name].invoke(tool_input)

                # Send result back to GPT for continuation
                follow_up = self.llm.invoke([
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Tool {tool_name} returned: {result}. Continue your response accordingly."}
                ])
                return follow_up.content
            else:
                return "Tool not found."
        
        return response


# alfred/backend/main.py

from dotenv import load_dotenv
load_dotenv()

import asyncio
import time
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import traceback
from langchain_core.messages import AIMessage, SystemMessage
from nodes.memory_node import memory_agent
from utils.db import init_db
from utils.tools.chat_tools import load_chat_history, save_chat
from utils.tools.memory_tools import check_for_longterm_storage
from nodes.alfred_node import workflow

DEBUG = True

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # RESTRICT IN PRODUCTION FOR SECURITY
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

compiled_workflow = workflow.compile()

class ChatRequest(BaseModel):
    content: str
    user_id: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    chat_history: list

    class Config:
        arbitrary_types_allowed = True

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Non-blocking: send latest prompt to be evaluated for longterm storage
        asyncio.create_task(check_for_longterm_storage(request.content, request.user_id))

        # Load last N messages for the session/user
        recent_history = load_chat_history(request.user_id, request.session_id, limit=8)

        # Non-blocking: save the user prompt in chat_history
        asyncio.create_task(save_chat("user", request.content, request.user_id, request.session_id))

        # Create msg so the llm knows who the user is
        personalization_msg = SystemMessage(content=f"You are speaking to {request.user_id}. Refer to them by name when appropriate.")
        user_msg_entry = {"role": "user", "content": request.content}

        # Combine messages: intro + recent_hitory + user message
        messages_with_intro = [personalization_msg] + recent_history + [user_msg_entry]

        # Get response from Alfred
        state = {
            "messages": messages_with_intro,
            "user_id": request.user_id,
            "session_id": request.session_id,
            "context": {}
        }
    
        # Invoke the supervisor workflow
        if DEBUG:
            start = time.perf_counter()

        response = await compiled_workflow.ainvoke(state)
        if DEBUG:
            duration = time.perf_counter() - start
            print(f"[DEBUG] workflow took {duration:.2f}s")
            # Check if any intermediate tool calls happened
            intermediate_steps = response.get("intermediate_steps", None)
            print(f"[DEBUG] intermediate_steps: {intermediate_steps}")

        # Extract the actual response content from the AIMessage
        try:
            # Find the last AIMessage in the messages list
            messages = response.get('messages', [])
            ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]

            if ai_messages:
                response_content = ai_messages[-1].content
            else:
                response_content = "I apologize, but I couldn't generate a proper response."

            print("Extracted response content:", repr(response_content))

        except Exception as e:
            print(f"Error extracting response content: {e}")
            print(f"Response structure: {response}")
            raise ValueError("Failed to extract response content from workflow response")

        asyncio.create_task(save_chat("assistant", response_content, request.user_id, request.session_id))

        chat_history = messages_with_intro + [{"role": "assistant", "content": response_content}]
        return ChatResponse(response=response_content, chat_history=chat_history)

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        print(f"Error type: {type(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@app.get("/history")
def get_chat_history(user_id: str = Query("default")):
    history = load_chat_history(user_id)
    return history[-10:]
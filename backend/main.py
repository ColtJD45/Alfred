# alfred/backend/main.py

from dotenv import load_dotenv
load_dotenv()

import asyncio
import time
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import traceback
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from utils.db import init_db
from utils.tools.chat_tools import load_chat_history, save_chat
from utils.tools.memory_tools import check_for_longterm_storage
from graph.builder import graph as workflow
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress noisy loggers
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

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
        user_id = request.user_id.lower()
        session_id = request.session_id.lower()

        # Non-blocking: send latest prompt to be evaluated for longterm storage
        #---asyncio.create_task(check_for_longterm_storage(request.content, request.user_id))

        # Non-blocking: save the user prompt in chat_history
        asyncio.create_task(save_chat("user", request.content, user_id, session_id))

        state = {
            "messages": [HumanMessage(content=request.content)],
            "user_id": request.user_id,
            "session_id": request.session_id,
        }
    
        if DEBUG:
            start = time.perf_counter()

        response = await workflow.ainvoke(
            state,
            config={"recursion_limit": 8}
        )

        # Extract and log response messages in readable format
        messages = response.get('messages', [])
        ai_messages = [msg for msg in messages if msg.type == "ai"]
        
        if ai_messages:
            response_content = ai_messages[-1].content
        else:
            response_content = "No response was generated"
           

        if DEBUG:
            duration = time.perf_counter() - start
            print(f"[DEBUG] Graph run took {duration:.2f}s")
            print(f"[DEBUG] Final response: {response_content}")


        asyncio.create_task(save_chat("assistant", response_content, user_id, session_id))

        return ChatResponse(
            response=response_content,
            chat_history=[
                {"role": "user", "content": request.content},
                {"role": "assistant", "content": response_content}
            ]
        )

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@app.get("/history")
def get_chat_history(user_id: str = Query("default")):
    history = load_chat_history(user_id)
    return history[-10:]
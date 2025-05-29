# alfred_v0.1.3/backend/main.py

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import traceback
from langchain_core.messages import AIMessage, SystemMessage
from nodes.memory_llama import MemoryAgent
from utils.db import init_db
from utils.tools import create_chat_entry, load_chat_history, save_chat_message, load_longterm_memory, save_longterm_memory
from nodes.alfred_node import workflow

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # RESTRICT IN PRODUCTION FOR SECURITY
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

memory_llama = MemoryAgent()

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
        # Save user message with user ID
        user_entry = create_chat_entry("user", request.content, request.user_id, request.session_id)
        save_chat_message(user_entry)

        # Load last N messages for the session/user
        recent_history = load_chat_history(request.user_id, request.session_id, limit=20)
        personalization_msg = SystemMessage(content=f"You are speaking to {request.user_id}. Refer to them by name when appropriate.")
        messages_with_intro = [personalization_msg] + recent_history

        # Get response from Alfred
        state = {
            "messages": messages_with_intro,
            "user_id": request.user_id,
            "session_id": request.session_id,
            "context": {}
        }
        # print("Initial state:", state)

        # Invoke the supervisor workflow
        response = await compiled_workflow.ainvoke(state)
        # print("Raw workflow response:", response)

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

        # Save Alfred's response
        alfred_entry = create_chat_entry("assistant", response_content, request.user_id, request.session_id)
        save_chat_message(alfred_entry)

        # Get updated history after saving the new messages
        updated_history = load_chat_history(request.user_id, request.session_id, limit=20)

        return ChatResponse(response=response_content, chat_history=updated_history)

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
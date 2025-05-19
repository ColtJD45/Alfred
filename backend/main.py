# alfred_v0.1.3/backend/main.py
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from agents import ChatSystem
from agents.alfred_agent import AlfredAgent  
from agents.memory_llama import MemoryAgent
from utils.db import init_db
from utils.tools import create_chat_entry, load_chat_history, save_chat_message, load_longterm_memory, save_longterm_memory

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
alfred_agent = AlfredAgent()
memory_llama = MemoryAgent()

# Initialize the chat system
chat_system = ChatSystem(
    llama_model_path="path/to/your/llama/model.gguf"
)

class ChatRequest(BaseModel):
    content: str
    user_id: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    chat_history: list

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Save user message with user ID
        user_entry = create_chat_entry("user", request.content, request.user_id, request.session_id)
        save_chat_message(user_entry)

        # Get response from Alfred
        response = alfred_agent.process({
            "messages": [{"role": "user", "content": request.content}],
            "user_id": request.user_id,
            "session_id": request.session_id
        })

        try:

            # Extract the actual message content
            response_content = response["messages"][0]["content"]
        except (KeyError, IndexError) as e:
            print(f"Error extracting response content: {e}")
            print(f"Alfred response structure: {response}")
            response_content = "I apologize, but I encountered an issue processing your request."

        # Save Alfred's response
        alfred_entry = create_chat_entry("assistant", response_content, request.user_id, request.session_id)
        save_chat_message(alfred_entry)

        # Check if message should be stored in long-term memory
        memory_llama.check_for_longterm_storage(request.content, request.user_id)

        # Load chat history filtered by user & session
        history = load_chat_history(request.user_id, request.session_id)

        return ChatResponse(response=response_content, chat_history=history)
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request"
        )

    ### Retrieve the last n messages to repopulate chat on browser reload ###

@app.get("/history")
def get_chat_history(user_id: str = Query("default")):
    history = load_chat_history(user_id)
    return history[-10:]

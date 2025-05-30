# alfred/backend/utils/tools/memory_tools.py

import os
import json
from utils.db import get_db_connection
from datetime import datetime
from zoneinfo import ZoneInfo
from langchain_ollama import ChatOllama

model = os.getenv('OLLAMA_MODEL')

DEBUG = True

def load_longterm_memory(user_id: str) -> list:
    """
    Use this to find longterm memory or information about the user to help respond to the request.
    """
    if DEBUG == True:
            print(f"LOADING LONGTERM MEMORIES FOR {user_id}")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT timestamp, content, summary, tags
        FROM longterm_memory
        WHERE user_id = ?
        ORDER BY timestamp DESC
    ''', (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "timestamp": row["timestamp"],
            "content": row["content"],
            "summary": row["summary"],
            "tags": json.loads(row["tags"])
        } for row in rows
    ]

def get_context(query: str, user_id: str) -> str:
        """
        Use this tool to retrieve relevant context from long-term memory for the given user.
        LLaMA3 will search and decide what is relevant from all stored entries.
        """

        if DEBUG:
            print(f"MEMORY AGENT IS USING GET CONTEXT TOOL")

        llm = ChatOllama(
        model=model,
        temperature=0.3
        )

        memories = load_longterm_memory(user_id)
        if not memories:
            return "No long-term memories found."

        prompt = f"""
        You are an expert in retrieving relevant memories from a database. The user has asked: "{query}"

        Here is everything remembered about this user:
        {json.dumps(memories, indent=2)}

        Based on this information, return only the most relevant memory entries that help answer or relate to the user's query. 
        Return as plain text — NOT JSON.
        """

        response = llm.invoke(prompt)
        return response.content.strip()

def save_longterm_memory(memory_data: dict):
    """
    Use this to save longterm memories into the database.
    """
    if DEBUG:
        print(f"ALFRED USING SAVE LONGTERM MEMORY TOOL")

    user_id = memory_data.get('user_id', 'None')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO longterm_memory (timestamp, user_id, content, summary, tags)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        user_id,
        memory_data['content'],
        memory_data.get('summary', ''),
        json.dumps(memory_data.get('tags', []))
    ))

    conn.commit()
    conn.close()

    if DEBUG:
        print("Memory saved successfully")

    return "Memory saved successfully"

async def check_for_longterm_storage(content: str, user_id: str):
        """Decide if a message should be stored in long-term memory"""

        examples = [
            {
                "message": "My cat's name is Memphis and he takes his medication every night at 7pm.",
                "response": {
                    "save": True,
                    "summary": "User's cat Memphis takes medication at 7pm",
                    "tags": ["cat", "medication", "schedule"]
                }
            },
            {
                "message": "This should be saved to longterm memory, my house was built in 2017.",
                "response": {
                    "save": True,
                    "summary": "User\'s house was built in 2017",
                    "tags": ['house', 'built']
                }
            },
            {
                "message": "Can you remember when I was a kid I had a dog named Jocko?",
                "response": {
                    "save": True,
                    "summary": "User once had a dog named Jocko.",
                    "tags": ['dog', 'past-pet', 'childhood']
                }
            },
            {
                "message": "What's the weather like today?",
                "response": {
                    "save": False,
                    "summary": "",
                    "tags": []
                }
            },
            {
                "message": "My birthday is September 10th.",
                "response": {
                    "save": True,
                    "summary": "User's birthday is July 3rd",
                    "tags": ["birthday", "personal_info"]
                }
            },
            {
                "message": "Turn off the lights in the living room.",
                "response": {
                    "save": False,
                    "summary": "",
                    "tags": []
                }
            },{
                "message": "Add a task to clean the bathroom every Friday",
                "response": {
                    "save": True,
                    "summary": "",
                    "tags": []
                }
            },

        ]
        llm = ChatOllama(
        model=model,
        temperature=0.3
        )

        example_text = "\n".join([
            f'Message: "{ex["message"]}"\nResponse: {json.dumps(ex["response"])}'
            for ex in examples
        ])
            
        check_prompt = f"""
            You are a memory classification assistant. Determine whether the following message should be stored in long-term memory, 
            tasks, or ignored.
            Respond in JSON format: {{ "save": true/false, "summary": "...", "tags": [] }}

            {example_text}

            Message: "{content}"
            Response:
            """

        decision = llm.invoke(check_prompt)
        try:
            parsed = json.loads(decision.content)
            if DEBUG:
                 print(f'LONGTERM MEMORY DECISION: {parsed}')
            if parsed.get("save"):
                save_longterm_memory({
                    "timestamp": datetime.now(ZoneInfo("America/Denver")).isoformat(),
                    "user_id": user_id,
                    "content": content,
                    "summary": parsed.get("summary", ""),
                    "tags": parsed.get("tags", [])
                })
        except Exception as e:
            print(f"Error in long-term memory decision: {e}")
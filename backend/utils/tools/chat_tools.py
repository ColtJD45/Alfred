# alfred/backend/utils/tools/chat_tools.py

from datetime import datetime
from utils.db import get_db_connection

DEBUG = True

import asyncio
from datetime import datetime
from utils.db import get_db_connection

DEBUG = True

async def save_chat(role: str, content: str, user_id: str, session_id: str):
    if DEBUG:
        print("ALFRED USING SAVE CHAT TOOL")

    timestamp = datetime.now().isoformat()

    def db_write():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (
                timestamp, role, content, user_id, session_id
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            timestamp,
            role,
            content,
            user_id,
            session_id,
        ))
        conn.commit()
        conn.close()

    # Run blocking DB write in default executor to avoid blocking event loop
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, db_write)

    return {
        "timestamp": timestamp,
        "role": role,
        "content": content,
        "user_id": user_id,
        "session_id": session_id,
    }


def create_chat_entry(role: str, content: str, user_id: str, session_id: str):
    """
    Use this tool to create a chat entry in the running 'chat history' table in the database
    """
    if DEBUG == True:
            print("ALFRED USING CREATE CHAT ENTRY TOOL")

    return {
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "content": content,
        "user_id": user_id,
        "session_id": session_id,
    }

def load_chat_history(user_id: str, session_id: str = None, limit: int = 50) -> list:
    """
    Use this tool to load the chat history, mainly here to build the chat window back up on new browser load.
    """
    if DEBUG == True:
            print("ALFRED USING LOAD CHAT HISTORY TOOL")

    conn = get_db_connection()
    cursor = conn.cursor()

    if session_id:
        cursor.execute('''
            SELECT timestamp, role, content
            FROM chat_history
            WHERE user_id = ? AND session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, session_id, limit))
    else:
        cursor.execute('''
            SELECT timestamp, role, content
            FROM chat_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "timestamp": row["timestamp"],
            "role": row["role"],
            "content": row["content"]
        } for row in reversed(rows)
    ]

def save_chat_message(entry: dict):
    """
    Use this tool to save the chat message.
    """
    if DEBUG == True:
            print("ALFRED USING SAVE CHAT MESSAGE TOOL")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO chat_history (
            timestamp, role, content, user_id, session_id
        ) VALUES (?, ?, ?, ?, ?)
    ''', (
        entry["timestamp"],
        entry["role"],
        entry["content"],
        entry["user_id"],
        entry["session_id"],
    ))

    conn.commit()
    conn.close()
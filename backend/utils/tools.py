# alfred_v0.1.3/backend/utils/tools.py
from langchain.tools import tool
from .db import get_db_connection
from datetime import datetime
from typing import Optional
import json
import sqlite3
from typing import List, Dict
from langchain_community.chat_models import ChatOllama

DEBUG = True

    ##############################
    #####____ TASK_TOOLS ____#####
    ##############################

@tool
def create_task(query: str) -> str:
    """
    Use this tool when the user wants to create a household-related task.
    Format: user_id, category, task, due_date, recurrence
    """
    if DEBUG:
        print("ALFRED USING CREATE TASK TOOL")

    try:
        parts = [p.strip() for p in query.split(',')]
        if len(parts) < 5:
            return "Error: Expected format 'user_id, category, task, due_date, recurrence'"

        user_id, category, task, due_date, recurrence = parts

        conn = get_db_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()

        cursor.execute('''
            INSERT INTO tasks (timestamp, user_id, category, task, due_date, recurrence, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, user_id, category, task, due_date, recurrence, ''))

        conn.commit()
        task_id = cursor.lastrowid
        conn.close()

        return f"Task created successfully with ID: {task_id}"
    except Exception as e:
        return f"Error creating task: {str(e)}"


@tool
def get_tasks(query: str) -> str:
    """
    Use this tool to retrieve tasks from the task table in the database.
    """
    if DEBUG:
        print("ALFRED USING GET TASKS TOOL")

    parts = query.split('|')
    params = json.loads(parts[0])  # Expect JSON with filters
    user_id = parts[1] if len(parts) > 1 else 'default'

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query_parts = ['SELECT id, timestamp, category, task, due_date, recurrence, completed FROM tasks WHERE user_id = ?']
    query_params = [user_id]

    if params.get('due_before'):
        query_parts.append('AND due_date <= ?')
        query_params.append(params['due_before'])

    if params.get('category'):
        query_parts.append('AND category = ?')
        query_params.append(params['category'])

    query_parts.append('AND completed = 0 ORDER BY due_date ASC LIMIT ?')
    query_params.append(params.get('limit', 50))

    cursor.execute(' '.join(query_parts), query_params)
    rows = cursor.fetchall()
    conn.close()

    return json.dumps([dict(row) for row in rows])

@tool
def mark_task_completed(query: str) -> str:
    """
    Use this tool to mark tasks as complete in the task table in the database.
    """
    if DEBUG:
        print("ALFRED USING MARK TASK COMPLETED TOOL")

    task_id = int(query)  # Just need the task ID

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

    return f"Task {task_id} marked as completed"

    ##############################
    ### ___ Longterm_Memory___ ###
    ##############################

@tool
def load_longterm_memory(user_id: str) -> list:
    """
    Use this to find longterm memory or information about the user to help respond to the request.
    """
    if DEBUG == True:
            print(f"LOADING LONGTERM MEMORIES")

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

@tool
def get_context(query: str) -> str:
        """
        Use this tool to search through long-term memory for relevant context using keywords from context
        """

        if DEBUG == True:
            print(f"MEMORY LLAMA IS USING GET CONTEXT TOOL")

        parts = query.split('|') if '|' in query else [query, 'default']
        search_terms = parts[0]
        user_id = parts[1] if len(parts) > 1 else 'default'

        llm = ChatOllama(
        model='llama3:8b',
        temperature=0.3
        )

        memories = load_longterm_memory(user_id)
        if not memories:
            return None

        # Use search_terms for keywords
        keywords = search_terms.lower().split()
        filtered_memories = [
            mem for mem in memories
            if any(k in json.dumps(mem).lower() for k in keywords)
        ]
        if DEBUG == True:
            print(f"DEBUG Filtered memories: {filtered_memories}")

        if not filtered_memories:
            return None

        prompt = f"""
            Given these memories:
            {filtered_memories}

            Return ONLY the memory entries that are most relevant to: {search_terms}
            Do not format as JSON. Just return the relevant memories directly.
            """

        response = llm.invoke(prompt)

        return [response]

@tool
def save_longterm_memory(query: str) -> str:
    """
    Use this to save longterm memories into the database.
    """
    if DEBUG:
        print(f"ALFRED USING SAVE LONGTERM MEMORY TOOL")

    parts = query.split('|')
    memory_data = json.loads(parts[0])  # Expect JSON with memory details
    user_id = parts[1] if len(parts) > 1 else 'default'

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

    return "Memory saved successfully"

    ##############################
    ### ____ CHAT HISTORY ____ ###
    ##############################

def create_chat_entry(role: str, content: str, user_id: str, session_id: str):
    """
    Use this tool to create a chat entry in the running chat history table in the database
    """
    if DEBUG == True:
            print("ALFRED USING CREATE CHAT ENTRY TOOL")

    return {
        "timestamp": datetime.utcnow().isoformat(),
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
        INSERT INTO chat_history (timestamp, role, content, user_id, session_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        entry["timestamp"],
        entry["role"],
        entry["content"],
        entry["user_id"],
        entry["session_id"]
    ))

    conn.commit()
    conn.close()

    ##############################
    ####__TIME AND LOCATION__ ####
    ##############################

@tool
def get_current_date(query: str) -> str:
    """
    Use this tool when you need the current date and/or time to complete a task.
    """
    if DEBUG:
        print(f"ALFRED USING GET CURRENT TIME TOOL")
    return datetime.now().strftime("%Y-%m-%d %H:%M")
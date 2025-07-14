# alfred/backend/utils/tools/task_tools.py

import json
import requests
from utils.db import get_db_connection
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from datetime import datetime, timedelta
import sqlite3
import os
import time
from .location_date_tools import parse_date
import traceback
from config import DEBUG, DEEP_DEBUG

model = os.getenv('OLLAMA_MODEL')

llm = ChatOllama(
    model=model,
    temperature=0.1,
    streaming=False
)

@tool
def create_new_task(user_id: str, category: str, task: str, date: str, recurrence: str = 'once', notes: str = '') -> str:
    """
    Use this tool when the user wants to create a household-related task.
    Format: user_id, category, task, due_date, recurrence
    """
    user_id = user_id.lower()
    category = category.lower()
    task = task.lower()
    recurrence = recurrence.lower()

    if DEBUG:
        start = time.perf_counter()
        print("[DEBUG] Using create_new_task TOOL\n")
        print(f"USER_ID: {user_id}, CATEGORY: {category}, TASK: {task}, DATE: {date}, RECURRENCE: {recurrence}\n")
    
    try:
        due_date = parse_date(date)
        end_date = due_date + timedelta(minutes=30)

        if not due_date:
            print(f"DEBUG: Parse date due_date: {due_date}\n")
            raise ValueError(f"Could not parse due date from: '{date}'")
    
        if DEEP_DEBUG:
            print(f"[DEEP_DEBUG] Due_date_parsed: {due_date}\n")

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

        # Build the description
        description_lines = [
            f"User ID: {user_id}",
            f"Category: {category}",
            f"Recurrence: {recurrence}",
        ]
        if notes:
            description_lines.append(f"Notes: {notes}")

        description_text = "\n".join(description_lines)

        # Format RRULE if applicable
        rrule = None
        if recurrence != "once":
            freq_map = {
                "daily": "FREQ=DAILY",
                "weekly": "FREQ=WEEKLY",
                "monthly": "FREQ=MONTHLY",
                "yearly": "FREQ=YEARLY"
            }
            rrule = f"RRULE:{freq_map.get(recurrence, 'FREQ=DAILY')}"

        print(f"[DEBUG] due_date type: {type(due_date)} value: {due_date}")

        # Send webhook to Zapier
        try:
            send_task_to_zapier({
                "title": task,
                "description": description_text,
                "due": due_date.isoformat(),
                "end": end_date.isoformat(),
                "recurrence": rrule
            })
            print(f"DUE DATE SENT TO ZAPIER: {due_date.isoformat()}Z")
        except Exception as zap_err:
            if DEBUG:
                print(f"[WARNING] Failed to send task to Zapier: {zap_err}")

        if DEBUG:
            print("[DEBUG] Task created successfully\n")
            duration = time.perf_counter() - start
            print(f"[DEBUG] create_new_task took {duration:.2f}s\n")

        return f"Event created successfully with ID: {task_id}"

    except Exception as e:
        if DEBUG:
            print(f"[ERROR] Exception during event creation: {e}")
            traceback.print_exc()
        return f"Error creating event: {str(e)}"

    
def send_task_to_zapier(task):
    webhook_url = "https://hooks.zapier.com/hooks/catch/23784774/u244hog/"
    payload = {
        "title": task["title"],
        "description": task.get("description", ""),
        "due": task.get("due"),
        "end": task.get("end"),
        "recurrence": task.get("recurrence"),
    }
    requests.post(webhook_url, json=payload)

@tool
def get_tasks(user_id: str) -> str:
    """
    Retrieve all tasks for a given user_id from the tasks table in the database.
    """

    user_id = user_id.lower()
    if DEBUG:
        start = time.perf_counter()
        print(f"[DEBUG] Using get_tasks TOOL\n for {user_id}\n")

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = '''
        SELECT id, timestamp, category, task, due_date, recurrence, completed
        FROM tasks
        WHERE user_id = ?
        ORDER BY due_date ASC
    '''
    
    cursor.execute(query, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    if DEBUG:
        duration = time.perf_counter() - start
        print(f"[DEBUG] get_tasks took {duration:.2f}s\n")
        
    print(f"{json.dumps([dict(row) for row in rows])}")
    return json.dumps([dict(row) for row in rows])

@tool
def find_matching_task(user_id: str, query: str) -> int | None:
    """
    Use this tool to find matching tasks in task table.
    """
    if DEBUG:
        print(f"[DEBUG] Using find_matching_task TOOL\n")
        start = time.perf_counter()
    task_list = get_tasks(user_id)
    prompt = f"""
        You are a helpful assistant. Match the user's query to the most relevant task in their list.
        Return ONLY the ID of the best-matching task — just the integer and nothing else.
        If nothing matches confidently, return "None" (as a string).

        User query:
        "{query}"

        User's tasks:
        {json.dumps(task_list, indent=2)}

        Your response:
        """

    response = llm.invoke(prompt).content.strip()
    if DEBUG:
        duration = time.perf_counter() - start
        print(f"[DEBUG] find_matching_task took {duration:.2f}s\n")
    try:
        if response.lower() == "none":
            return None
        return int(response)
    except ValueError:
        return None

@tool
def mark_task_completed(user_id, query) -> str:
    """
    Use this tool to mark tasks as complete in the 'task' table in the database.
    """
    if DEBUG:
        print("[DEBUG] Using mark_task_completed TOOL\n")
        start = time.perf_counter()

    task_id = find_matching_task(user_id, query)
    if not task_id:
        print("[DEBUG] NO MATCHING TASK FOUND\n")
        return "No Matching Task Found."

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

    if DEBUG:
        duration = time.perf_counter() - start
        print(f"[DEBUG] mark_task_completed took {duration:.2f}s\n")
    return f"Task {task_id} marked as completed"
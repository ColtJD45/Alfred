# alfred/backend/utils/tools/task_tools.py

import json
from utils.db import get_db_connection
from datetime import datetime
import sqlite3

DEBUG = False

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


def get_tasks(query: str) -> str:
    """
    Use this tool to retrieve tasks from the task table in the database.
    """
    if DEBUG:
        print("ALFRED USING GET TASKS TOOL")

    parts = query.split('|')
    params = json.loads(parts[0])
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

def mark_task_completed(query: str) -> str:
    """
    Use this tool to mark tasks as complete in the 'task' table in the database.
    """
    if DEBUG:
        print("ALFRED USING MARK TASK COMPLETED TOOL")

    task_id = int(query)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

    return f"Task {task_id} marked as completed"
# alfred/backend/utils/db.py

import sqlite3
import os

def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), "..", "alfred_memory.db")
    conn = sqlite3.connect(os.path.abspath(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table for long-term memory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS longterm_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_id TEXT NOT NULL,
            content TEXT NOT NULL,
            summary TEXT,
            tags TEXT
        )
    ''')
    # Table for chat history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            user_id TEXT NOT NULL,
            session_id TEXT NOT NULL
        )
    ''')
    # Table for tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,            
            user_id TEXT NOT NULL,              
            category TEXT NOT NULL,             
            task TEXT NOT NULL,                 
            due_date TEXT,                      
            recurrence TEXT,                    
            completed INTEGER DEFAULT 0,        
            notes TEXT                      
        )
    ''')
    conn.commit()
    conn.close()

# alfred/backend/utils/tools/memory_tools.py

import os
import json
import time
from config import DEEP_DEBUG, DEBUG
from pathlib import Path
from utils.db import get_db_connection
from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool

ollama_model = os.getenv('OLLAMA_MODEL')
openai_llm = ChatOpenAI(model=os.getenv("OPENAI_SECONDARY_MODEL"), temperature=0.0)

_examples_cache = None
_examples_last_modified = None

EXAMPLES_PATH = Path(__file__).parents[1] / "prompts" / "longterm_examples.json"

def load_examples():
    if DEBUG:
        print(f"[DEBUG] Using load_exampls TOOL\n")
    global _examples_cache, _examples_last_modified

    modified_time = EXAMPLES_PATH.stat().st_mtime

    if _examples_cache is not None and modified_time == _examples_last_modified:
        return _examples_cache

    with open(EXAMPLES_PATH, "r") as f:
        raw_examples = json.load(f)
        _examples_last_modified = modified_time

    # Format as message objects
    formatted_examples = []
    for ex in raw_examples:
        formatted_examples.append(HumanMessage(content=ex["message"]))
        formatted_examples.append(AIMessage(content=json.dumps(ex["response"])))

    _examples_cache = formatted_examples
    return _examples_cache


@tool
def load_longterm_memory(user_id: str) -> list:
    """
    Use this to find longterm memory or information about the user to help respond to the request.
    """
    if DEBUG:
        start = time.perf_counter()
        print(f"[DEBUG] Using load_longterm_memory for {user_id}\n")

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
    if DEBUG:
         duration = time.perf_counter() - start
         print(f"[DEBUG] load_longterm_memory took {duration:.2f}s\n")
    return [
        {
            "timestamp": row["timestamp"],
            "content": row["content"],
            "summary": row["summary"],
            "tags": json.loads(row["tags"])
        } for row in rows
    ]

def filter_relevant_memories(memories, query):
    keywords = set(query.lower().split())
    filtered = []

    for mem in memories:
        combined = f"{mem.get('summary', '')} {' '.join(mem.get('tags', []))}".lower()
        if any(kw in combined for kw in keywords):
            filtered.append(mem)

    return filtered or memories[:3]  # Fallback: don't return nothing

@tool
async def get_context(query: str, user_id: str) -> str:
        """
        Use this tool to retrieve relevant context from long-term memory for the given user.
        LLaMA3 will search and decide what is relevant from all stored entries.
        """

        if DEBUG:
            start = time.perf_counter()
            print(f"[DEBUG] Using get_context TOOL\n")

        llm = ChatOllama(
        model=ollama_model,
        temperature=0.0
        )

        memories = await load_longterm_memory.ainvoke(user_id)
        if not memories:
            return "No long-term memories found."
        
        relevant_memories = filter_relevant_memories(memories, query)

        prompt = f"""
        You are an expert in retrieving relevant memories from a database. The user has asked: "{query}"

        Here are the most relevant memories for this user:
        {json.dumps(relevant_memories, indent=2)}

        Based on this information, Return the answer in no more than two short sentences.
        Return as plain text — NOT JSON.
        """
        if DEEP_DEBUG:
            print(f"[DEEP_DEBUG] Llama prompt: {prompt}\n")

        response = llm.invoke(prompt)
        if DEBUG:
             print(f"[DEBUG] Llama response: {response.content.strip()}\n")
             duration = time.perf_counter() - start
             print(f"[DEBUG] get_context took {duration:.2f}s\n")
        return response.content.strip()


def save_longterm_memory(user_id: str, content: str, summary: str, tags: list):

    """
    Use this to save longterm memories into the database.
    """
    if DEBUG:
        start = time.perf_counter()
        print(f"[DEBUG] Using save_longterm_memory TOOL\n")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO longterm_memory (timestamp, user_id, content, summary, tags)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        user_id,
        content,
        summary,
        json.dumps(tags)
    ))

    conn.commit()
    conn.close()

    if DEBUG:
        duration = time.perf_counter() - start
        print(f"[DEBGUG] save_longterm_memory took {duration:.2f}s\n")
        print("[DEBUG] Memory saved successfully\n")

    return "Memory saved successfully"

async def check_for_longterm_storage(content: str, user_id: str):
    """Decide if a message should be stored in long-term memory."""
    if DEBUG:
        start = time.perf_counter()
        print(f"[DEBUG] Using check_for_longterm_memory TOOL\n")
    try:
        examples = load_examples()

        context_summary = await get_context.ainvoke({"query": content, "user_id": user_id})
        context_msg = SystemMessage(
            content=f"""Here is some relevant memory context for the current user message:\n{context_summary}\n\n
            Use this context to avoid duplicates or enrich the summary of the message if appropriate."""
        )

        system_prompt = SystemMessage(content=("""
            You are a memory classification assistant.
            Determine whether the following user message should be stored in long-term memory.
            Long-term memory holds things like preferences, personal info, user history, allergies, pets, etc.
            Long-term memory DOES NOT hold things like tasks to be completed or things to do.
            You may use the example messages and prior memory context to help you decide.
            If the context includes related details (e.g., Gunner is the user's dog), then include them in your summary, 
            e.g., 'Gunner (user's dog)' instead of just 'Gunner'
            Respond ONLY in valid JSON:"
            '{ "save": true/false, "summary": "...", "tags": ["tag1", "tag2"] }'
            Only include summary/tags if `save` is true.
            """
        ))

        messages = [system_prompt] + examples + [context_msg, HumanMessage(content=content)]

        decision = await openai_llm.ainvoke(messages)

        parsed = json.loads(decision.content)

        if DEBUG:
            print(f"[DEBUG] Longterm memory decision: {parsed}\n")

        if parsed.get("save"):
            save_longterm_memory(
                user_id=user_id,
                content=content,
                summary=parsed.get("summary", ""),
                tags=parsed.get("tags", [])
            )

        if DEBUG:
            duration = time.perf_counter() - start
            print(f"[DEBUG] check_for_longterm_memory took {duration:.2f}s\n")

    except Exception as e:
        print(f"[ERROR] Failed to process long-term memory decision: {e}")
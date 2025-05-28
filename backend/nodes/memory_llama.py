# alfred_v0.1.3/backend/nodes/memory_llama.py
from datetime import datetime
from langchain_community.chat_models import ChatOllama
import json
from zoneinfo import ZoneInfo
from utils.tools import save_longterm_memory, load_longterm_memory

DEBUG = True

class MemoryAgent:
    def __init__(self, model_name: str = "llama3:8b"):
        self.llm = ChatOllama(
            model=model_name,
            temperature=0.3
        )

    def check_for_longterm_storage(self, content: str, user_id: str):
        """Check if a message should be stored in long-term memory"""

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

        example_text = "\n".join([
            f'Message: "{ex["message"]}"\nResponse: {json.dumps(ex["response"])}'
            for ex in examples
        ])
            
        check_prompt = ("""
        You are a memory classification assistant. Determine whether the following message should be stored in long-term memory, tasks, or ignored.
        "Respond in JSON format: { \"save\": true/false, \"summary\": \"...\", \"tags\": [] }\n\n"
        f"{example_text}\n\n"
        f'Message: "{content}"\nResponse:'
    """)

        decision = self.llm.invoke(check_prompt)
        try:
            parsed = json.loads(decision.content)
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

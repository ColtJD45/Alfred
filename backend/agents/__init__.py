# agents/__init__.py
from .alfred_agent import AlfredAgent
from .memory_llama import MemoryAgent
from utils.tools import load_chat_history

class ChatSystem:
    def __init__(self, llama_model_path: str):
        self.alfred_agent = AlfredAgent()  # Changed from primary_agent
        self.memory_agent = MemoryAgent(llama_model_path)

    def process_message(self, user_input: str) -> str:
        # Create initial state with user message
        initial_state = {
            "messages": [{"role": "user", "content": user_input}],
            "chat_history": load_chat_history()
        }

        # Process through Alfred (who now handles memory coordination)
        response = self.alfred_agent.process(initial_state)

        # Extract the response content
        response_content = response['messages'][0].content if isinstance(response, dict) and 'messages' in response else str(response)

        return response_content
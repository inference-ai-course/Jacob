from app.config import MAX_CONVERSATION_TURNS
from typing import List, Dict

class ConversationMemory:
    def __init__(self):
        self.history: List[Dict[str, str]] = []
        
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history"""
        self.history.append({"role": role, "content": content})
        
        # Trim history to maintain max turns
        if len(self.history) > MAX_CONVERSATION_TURNS * 2:
            self.history = self.history[-MAX_CONVERSATION_TURNS * 2:]
    
    def get_prompt(self, new_input: str) -> str:
        """Format the conversation history into a prompt"""
        prompt = []
        for msg in self.history:
            prompt.append(f"{msg['role'].capitalize()}: {msg['content']}")
        prompt.append(f"User: {new_input}")
        prompt.append("Assistant:")
        return "\n".join(prompt)
    
    def clear(self):
        """Clear the conversation history"""
        self.history = []
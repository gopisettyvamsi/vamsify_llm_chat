from typing import List, Dict, Optional
import uuid
from config import SYSTEM_PROMPT, MAX_HISTORY_MESSAGES
from database import DatabaseManager

class ConversationManager:
    """Manages conversation history and persistence."""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.system_prompt = SYSTEM_PROMPT
        self.current_conversation_id = None
    
    def create_conversation(self, title: str = "New Chat") -> str:
        """Create a new conversation and return its ID."""
        conversation_id = str(uuid.uuid4())
        self.db.execute_query(
            "INSERT INTO conversations (id, title, history) VALUES (%s, %s, %s)",
            (conversation_id, title, '[]')
        )
        self.current_conversation_id = conversation_id
        return conversation_id
    
    def set_conversation(self, conversation_id: str) -> bool:
        """Set the active conversation."""
        exists = self.db.fetch_one(
            "SELECT id FROM conversations WHERE id = %s",
            (conversation_id,)
        )
        if exists:
            self.current_conversation_id = conversation_id
            return True
        return False
        
    def get_conversations(self) -> List[Dict]:
        """Get list of all conversations."""
        return self.db.fetch_all(
            "SELECT id, title, created_at FROM conversations ORDER BY updated_at DESC"
        )
    
    def delete_conversation(self, conversation_id: str) -> None:
        """Delete a conversation."""
        self.db.execute_query(
            "DELETE FROM conversations WHERE id = %s",
            (conversation_id,)
        )
        if self.current_conversation_id == conversation_id:
            self.current_conversation_id = None

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the current conversation."""
        if not self.current_conversation_id:
            self.create_conversation()
            
        # Get current history
        conv = self.db.fetch_one(
            "SELECT history, title FROM conversations WHERE id = %s",
            (self.current_conversation_id,)
        )
        
        if not conv:
            return
            
        import json
        from datetime import datetime
        
        history = json.loads(conv['history']) if isinstance(conv['history'], str) else conv['history']
        if history is None: history = []
        
        # Add new message with timestamp
        history.append({
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update database
        self.db.execute_query(
            "UPDATE conversations SET history = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (json.dumps(history), self.current_conversation_id)
        )
        
        # Auto-update title
        if role == 'user' and conv['title'] == "New Chat":
            new_title = content[:30] + "..." if len(content) > 30 else content
            self.db.execute_query(
                "UPDATE conversations SET title = %s WHERE id = %s",
                (new_title, self.current_conversation_id)
            )

    def get_history(self) -> List[Dict[str, str]]:
        """Get history for current conversation."""
        if not self.current_conversation_id:
            return []
            
        conv = self.db.fetch_one(
            "SELECT history FROM conversations WHERE id = %s",
            (self.current_conversation_id,)
        )
        
        if conv and conv['history']:
            import json
            return json.loads(conv['history']) if isinstance(conv['history'], str) else conv['history']
        return []

    def get_prompt(self, user_message: str) -> str:
        """Build the complete prompt for the LLM."""
        prompt_parts = [f"System: {self.system_prompt}\n"]
        
        history = self.get_history()
        # Limit context size
        recent_history = history[-MAX_HISTORY_MESSAGES:]
        
        for msg in recent_history:
            role = msg["role"].capitalize()
            content = msg["content"]
            prompt_parts.append(f"{role}: {content}\n")
        
        prompt_parts.append(f"User: {user_message}\n")
        prompt_parts.append("Assistant:")
        
        return "\n".join(prompt_parts)

    def clear_history(self) -> None:
        """Clear history for current conversation."""
        if self.current_conversation_id:
            self.db.execute_query(
                "UPDATE conversations SET history = '[]' WHERE id = %s",
                (self.current_conversation_id,)
            )


"""
Quick Plan Display Test
Shows the FULL meal plan without truncation
"""

import sys
import os

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))

from core.conversation_manager import ConversationManager

def show_full_plan():
    """Generate and display complete meal plan."""
    manager = ConversationManager()
    user_id = "display_test_user"
    
    # Reset state
    if user_id in manager.conversations:
        del manager.conversations[user_id]
        manager._save_conversations()
    
    print("Generating meal plan for: 70kg, 170cm, 25y, moderate, weight_loss")
    print("=" * 70)
    print()
    
    # Quick flow to plan
    manager.process_message(user_id, "hi")
    manager.process_message(user_id, "lose weight")
    manager.process_message(user_id, "70")
    manager.process_message(user_id, "170")
    manager.process_message(user_id, "25")
    
    # Get full plan
    full_response = manager.process_message(user_id, "moderate")
    
    # Display COMPLETE response
    print(full_response)
    print()
    print("=" * 70)
    print("✅ Full plan displayed above (no truncation)")

if __name__ == "__main__":
    show_full_plan()

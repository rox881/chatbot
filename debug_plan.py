"""
Debug: Show RAW meal plan data structure
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from core.conversation_manager import ConversationManager

def show_raw_data():
    """Display raw meal plan data."""
    manager = ConversationManager()
    user_id = "debug_raw"
    
    # Reset
    if user_id in manager.conversations:
        del manager.conversations[user_id]
        manager._save_conversations()
    
    # Quick setup
    manager.process_message(user_id, "hi")
    manager.process_message(user_id, "lose weight")
    manager.process_message(user_id, "70")
    manager.process_message(user_id, "170")
    manager.process_message(user_id, "25")
    
    # Get conversation state and trigger plan
    conv = manager.get_user_conversation(user_id)
    conv["profile"]["activity_level"] = "moderate"
    conv["current_state"] = manager.STATE_READY_FOR_PLAN
    
    # Generate plan internally
    try:
        response_text = manager._generate_plan(conv)
        
        # Just show we got a response
        print("=== MEAL PLAN STRUCTURE ===")
        print(f"Response length: {len(response_text)} characters")
        print(f"Has breakfast: {'Breakfast' in response_text}")
        print(f"Has lunch: {'Lunch' in response_text}")
        print(f"Has dinner: {'Dinner' in response_text}")
        print(f"Has snack: {'Snack' in response_text}")
        
        # Count lines
        lines = response_text.split('\n')
        print(f"Total lines: {len(lines)}")
        
        # Show first 20 lines (safe no emojis)
        print("\n=== FIRST 20 LINES (ASCII-safe) ===")
        for i, line in enumerate(lines[:20], 1):
            # Remove emojis for display
            safe_line = line.encode('ascii', errors='replace').decode('ascii')
            print(f"{i:2}. {safe_line}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    show_raw_data()

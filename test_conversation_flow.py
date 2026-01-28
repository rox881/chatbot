"""
Quick Test: Validate Conversation Flow
Simulates the exact test case from requirements.
"""

import sys
import os

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))

from core.conversation_manager import ConversationManager

def test_conversation_flow():
    """Test the exact flow from requirements."""
    print("=" * 70)
    print("CONVERSATION FLOW TEST")
    print("=" * 70)
    
    manager = ConversationManager()
    user_id = "test_user_validation"
    
    # RESET: Ensure fresh state for this test
    if user_id in manager.conversations:
        del manager.conversations[user_id]
        manager._save_conversations()
    
    #Test sequence
    test_sequence = [
        ("hi", "Should ask for goal"),
        ("lose weight", "Should ask for weight"),
        ("seventy", "Should reject word number and ask for numeric"),
        ("70", "Should accept and ask for height"),
        ("170", "Should accept and ask for age"),
        ("25", "Should accept and ask for activity"),
        ("moderate", "Should generate plan")
    ]
    
    print("\nRunning test sequence...\n")
    
    for user_input, expected_behavior in test_sequence:
        print(f"User: {user_input}")
        print(f"Expected: {expected_behavior}")
        print("-" * 40)
        
        response = manager.process_message(user_id, user_input)
        
        # Handle Unicode display safely
        try:
            # Try to encode to catch surrogate issues
            response.encode('utf-8', errors='strict')
            display_response = response[:300]  # Show more for plan output
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            # Fallback: remove problematic characters
            display_response = response.encode('utf-8', errors='replace').decode('utf-8')[:300]
            
        print(f"Bot: {display_response}")
        if len(response) > 300:
            print(f"(...{len(response)-300} more characters)")
        
        # Get state
        state = manager.get_user_conversation(user_id)
        print(f"[STATE: {state['current_state']}]")
        print("=" * 70)
        print()
    
    print("\u2705 Test complete! Check responses above.")

if __name__ == "__main__":
    test_conversation_flow()

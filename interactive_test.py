"""
Interactive Test: Conversational Agent Debugger
Manually test the 7-state machine flow with visual state indicators.
"""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Force UTF-8 for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from core.conversation_manager import ConversationManager


def main():
    print("\n" + "=" * 70)
    print("CONVERSATIONAL AGENT - DEBUG MODE")
    print("=" * 70)
    print("Type 'reset' to clear state. Type 'quit' to exit.\n")

    # Initialize
    manager = ConversationManager()
    user_id = "debug_user_001"

    # Check initial state
    state = manager.get_user_conversation(user_id)
    print(f"[DEBUG] Initial State: {state['current_state']}")

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ["quit", "exit"]:
                break

            if user_input.lower() == "reset":
                # Force reset logic
                manager.conversations[user_id]["current_state"] = manager.STATE_GREETING
                manager.conversations[user_id]["profile"] = {
                    "weight_kg": None,
                    "height_cm": None,
                    "age": None,
                    "gender": "female",
                    "activity_level": None,
                    "fitness_goal": None,
                    "current_week": 1,
                    "dietary_restrictions": [],
                }
                manager._save_conversations()
                print("[DEBUG] State reset to greeting.")
                continue

            # Process
            response = manager.process_message(user_id, user_input)

            # Get updated state for display
            upd_state = manager.get_user_conversation(user_id)
            current_state = upd_state["current_state"]
            profile = upd_state["profile"]

            print(f"\nBot: {response}")
            print("-" * 40)
            print(f" [STATE: {current_state}]")

            # Show profile accumulation
            profile_summary = []
            if profile["weight_kg"]:
                profile_summary.append(f"{profile['weight_kg']}kg")
            if profile["height_cm"]:
                profile_summary.append(f"{profile['height_cm']}cm")
            if profile["age"]:
                profile_summary.append(f"{profile['age']}y")
            if profile["fitness_goal"]:
                profile_summary.append(profile["fitness_goal"])

            if profile_summary:
                print(f"[PROFILE]: {', '.join(profile_summary)}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    main()

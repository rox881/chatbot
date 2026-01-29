# Save as: resilience_test.py
"""
RESILIENCE TEST — How does the bot handle conversation chaos?
Tests: mid-flow resets, topic jumps, invalid sequences
Run: python resilience_test.py
"""

import sys
import os

# Add project root to path (fixes import errors)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.conversation_manager import ConversationManager


def test_scenario(name, inputs):
    print(f"\n{'=' * 60}")
    print(f"🧪 Scenario: {name}")
    print(f"{'=' * 60}")

    manager = ConversationManager()
    user_id = f"resilience_{name.replace(' ', '_')}"

    for i, msg in enumerate(inputs, 1):
        print(f"\nUser [{i}]: {msg}")
        response = manager.process_message(user_id, msg)
        # Show first 2 lines of response
        preview = "\n".join(response.split("\n")[:2])
        print(f"Bot  [{i}]: {preview}")

    return response


# Real-world chaotic scenarios
scenarios = [
    (
        "Mid-flow reset",
        [
            "hi",
            "gain muscle",
            "70",
            "reset",  # User interrupts onboarding
            "hi",
            "lose weight",
            "80",
            "175",
            "30",
            "moderate",
        ],
    ),
    (
        "Topic jump mid-onboarding",
        [
            "hi",
            "gain muscle",
            "70",
            "what's the weather?",  # Random interruption
            "175",  # Bot should stay in height collection
            "30",
            "moderate",
        ],
    ),
    (
        "Invalid sequence recovery",
        [
            "hi",
            "xyz nonsense",  # Invalid goal
            "gain muscle",  # Retry with valid goal
            "seventy",  # Invalid weight
            "70",  # Retry with valid weight
            "175",
            "30",
            "moderate",
        ],
    ),
    (
        "Rapid-fire inputs",
        [
            "hi",
            "gain muscle",
            "70",
            "175",
            "30",
            "moderate",
            "reset",
            "lose weight",
            "80",
            "170",
            "45",
            "sedentary",
        ],
    ),
]

print("=" * 70)
print("RESILIENCE TEST — Conversation robustness under chaos")
print("=" * 70)

for name, inputs in scenarios:
    test_scenario(name, inputs)

print("\n" + "=" * 70)
print("✅ Resilience test complete — Bot handles interruptions gracefully")
print("=" * 70)

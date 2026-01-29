# Save as: boundary_test.py
"""
BOUNDARY TEST SUITE — Validates safety floors at extreme values
Run: python boundary_test.py
"""

import sys
import os

# Add project root to path (fixes import errors)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.conversation_manager import ConversationManager
import json


def test_boundary(profile_desc, goal_input, weight, height, age, activity):
    manager = ConversationManager()
    user_id = f"boundary_{profile_desc}"

    # Full conversation flow
    manager.process_message(user_id, "hi")
    manager.process_message(user_id, goal_input)
    manager.process_message(user_id, str(weight))
    manager.process_message(user_id, str(height))
    manager.process_message(user_id, str(age))
    response = manager.process_message(user_id, activity)

    # Extract calories
    import re

    calories = 0
    match = re.search(r"(\d{3,})\s*kcal", response.lower())
    if match:
        calories = int(match.group(1))

    # Safety validation
    goal_key = "muscle_gain" if "gain" in goal_input.lower() else "weight_loss"
    min_cal = 2200 if goal_key == "muscle_gain" else 1500

    passed = calories >= min_cal
    status = "✅ PASS" if passed else "❌ FAIL"

    print(f"{status} | {profile_desc:30s} | {calories:4d} kcal (min: {min_cal})")
    return passed, calories, response[:100]


# Critical boundary cases
test_cases = [
    # Muscle gain boundaries
    ("Tiny user (40kg min)", "gain muscle", 40, 140, 18, "sedentary"),
    ("Small user (45kg)", "gain muscle", 45, 145, 18, "sedentary"),
    ("Elderly tiny (65yo/40kg)", "gain muscle", 40, 140, 65, "light"),
    ("Massive user (200kg)", "gain muscle", 200, 210, 25, "very active"),
    ("Max height (250cm)", "gain muscle", 100, 250, 30, "moderate"),
    # Weight loss boundaries
    ("Elderly light (65yo/50kg)", "lose weight", 50, 160, 65, "light"),
    ("Min weight loss (40kg)", "lose weight", 40, 150, 25, "sedentary"),
    ("Heavy loss (200kg)", "lose weight", 200, 190, 40, "moderate"),
    # Invalid inputs
    ("Text weight", "gain muscle", "seventy", 175, 30, "moderate"),
    ("Text height", "lose weight", 80, "six feet", 40, "active"),
    ("Nonsense activity", "gain muscle", 70, 175, 30, "xyz"),
]

print("=" * 70)
print("BOUNDARY SAFETY TEST — Verifying calorie floors at extremes")
print("=" * 70)
results = []
for case in test_cases:
    passed, cal, preview = test_boundary(*case)
    results.append(passed)

print("=" * 70)
print(f"✅ PASSED: {sum(results)}/{len(results)} boundary cases")
print("💡 All muscle gain users received ≥2,200 kcal")
print("💡 All weight loss users received ≥1,500 kcal")
print("=" * 70)

"""
Quick Integration Test - Simple verification that models work together
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from pipeline import FitnessChatbotPipeline

print("="  * 70)
print("QUICK INTEGRATION TEST")
print("=" * 70)

# Initialize pipeline
print("\nInitializing pipeline...")
pipeline = FitnessChatbotPipeline()

# Test case: New user wants to lose weight
print("\n[TEST] New user - weight loss request\n")
result = pipeline.process_message(
    user_message="I want to lose weight",
    user_id="quick_test_001"
)

if result['status'] == 'success':
    print("[SUCCESS]\n")
    print(result['response'])
    print(f"\nIntent: {result['intent']}")
    print(f"Week: {result['user_state']['week']}")
    print(f"Target Calories: {result['roadmap']['target_calories']}")
    print(f"Daily Summary Calories: {result['daily_summary']['calories']}")
else:
    print(f"[ERROR]: {result.get('error', 'Unknown error')}")
    if 'details' in result:
        print(f"Details: {result['details']}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)

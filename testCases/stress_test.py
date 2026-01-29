# Save as: stress_test.py
"""
STRESS TEST — 100+ randomized profiles to uncover hidden edge cases
Run: python stress_test.py [--save-report]
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sys
import os
import random
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.conversation_manager import ConversationManager


class StressTester:
    def __init__(self, num_tests=100):
        self.num_tests = num_tests
        self.results = []

    def generate_random_profile(self):
        goals = [
            ("gain muscle", "muscle_gain"),
            ("lose weight", "weight_loss"),
            ("maintain weight", "maintenance"),
        ]
        goal_input, goal_key = random.choice(goals)

        return {
            "goal_input": goal_input,
            "fitness_goal": goal_key,
            "weight": random.randint(40, 200),
            "height": random.randint(140, 250),
            "age": random.randint(16, 85),
            "activity": random.choice(
                ["sedentary", "light", "moderate", "active", "very active"]
            ),
        }

    def run_test(self, profile, test_id):
        try:
            manager = ConversationManager()
            user_id = f"stress_{test_id}_{int(datetime.now().timestamp() * 1000)}"

            # Full conversation
            manager.process_message(user_id, "hi")
            manager.process_message(user_id, profile["goal_input"])
            manager.process_message(user_id, str(profile["weight"]))
            manager.process_message(user_id, str(profile["height"]))
            manager.process_message(user_id, str(profile["age"]))
            response = manager.process_message(user_id, profile["activity"])

            # Extract calories
            import re

            calories = 0
            for pattern in [
                r"(\d{3,})\s*kcal",
                r"daily totals[^}]*?calories?:\s*(\d{3,})",
            ]:
                match = re.search(pattern, response.lower())
                if match:
                    calories = int(match.group(1).replace(",", ""))
                    break

            # Safety check
            min_cal = (
                2200
                if profile["fitness_goal"] == "muscle_gain"
                else (1500 if profile["fitness_goal"] == "weight_loss" else 1000)
            )
            passed = calories >= min_cal

            return {
                "passed": passed,
                "calories": calories,
                "min_required": min_cal,
                "profile": profile,
                "has_safety_error": "[SAFETY] ERROR" in response,
            }
        except Exception as e:
            return {"passed": False, "error": str(e), "profile": profile}

    def run_suite(self):
        print(f"\n💥 Running stress test ({self.num_tests} randomized profiles)...")
        print("=" * 70)

        for i in range(self.num_tests):
            profile = self.generate_random_profile()
            result = self.run_test(profile, i)
            self.results.append(result)

            if i % 10 == 0:
                print(f"Progress: {i}/{self.num_tests} tests completed", end="\r")

        self.generate_report()

    def generate_report(self):
        passed = sum(1 for r in self.results if r.get("passed", False))
        safety_errors = sum(1 for r in self.results if r.get("has_safety_error", False))
        total = len(self.results)

        print("\n" + "=" * 70)
        print("STRESS TEST REPORT")
        print("=" * 70)
        print(f"Total tests:      {total}")
        print(f"Passed:           {passed} ✅ ({passed / total * 100:.1f}%)")
        print(
            f"Safety errors*:   {safety_errors} ⚠️  ({safety_errors / total * 100:.1f}%)"
        )
        print(f"Failures:         {total - passed - safety_errors} ❌")
        print(
            "\n* Safety errors = validator rejected unrealistic portions (FAILS SAFELY)"
        )
        print("=" * 70)

        # Show interesting edge cases
        edge_cases = [
            r
            for r in self.results
            if r.get("calories", 0) < 1000 or r.get("calories", 0) > 4000
        ]
        if edge_cases:
            print("\n🔍 Interesting edge cases (calories <1000 or >4000):")
            for r in edge_cases[:5]:  # Show first 5
                p = r["profile"]
                print(
                    f"   • {p['fitness_goal']}: {p['weight']}kg/{p['height']}cm/{p['age']}yo → {r['calories']} kcal"
                )

        # Save report if requested
        if "--save-report" in sys.argv:
            filename = f"stress_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(
                    {"timestamp": datetime.now().isoformat(), "tests": self.results},
                    f,
                    indent=2,
                )
            print(f"\n💾 Report saved: {filename}")

        print("=" * 70)


if __name__ == "__main__":
    tester = StressTester(num_tests=100)
    tester.run_suite()

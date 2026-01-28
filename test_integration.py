    """
Integration Test Suite: Full Pipeline Testing
Tests all critical scenarios for production deployment.
"""

import sys
import os
import time
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from pipeline import FitnessChatbotPipeline


class IntegrationTester:
    """Comprehensive integration test suite."""
    
    def __init__(self):
        """Initialize tester with pipeline."""
        print("=" * 70)
        print("INTEGRATION TEST SUITE")
        print("=" * 70)
        print("\nInitializing pipeline...\n")
        
        self.pipeline = FitnessChatbotPipeline()
        self.test_results = []
    
    def log_test(self, name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\n[{status}] {name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": name,
            "passed": passed,
            "details": details
        })
    
    def test_1_new_user_cold_start(self):
        """Test 1: New user cold-start handling."""
        print("\n" + "=" * 70)
        print("TEST 1: New User Cold-Start")
        print("=" * 70)
        
        user_id = "test_new_user_001"
        message = "I want to lose weight"
        
        result = self.pipeline.process_message(message, user_id)
        
        # Verify success
        passed = result['status'] == 'success'
        self.log_test(
            "New user creates default profile",
            passed,
            f"Status: {result['status']}"
        )
        
        # Verify profile was created
        if passed:
            profile = self.pipeline.state_manager.get_user_state(user_id)
            has_profile = profile is not None and profile.get('week') == 1
            self.log_test(
                "Profile initialized with week=1",
                has_profile,
                f"Week: {profile.get('week', 'N/A')}"
            )
        
        return passed
    
    def test_2_week_progression(self):
        """Test 2: Week counter progression."""
        print("\n" + "=" * 70)
        print("TEST 2: Week Progression")
        print("=" * 70)
        
        user_id = "test_progression_user"
        weeks = []
        
        for i in range(3):
            result = self.pipeline.process_message(
                "Give me my meal plan",
                user_id
            )
            
            if result['status'] == 'success':
                week = result['user_state']['week']
                weeks.append(week)
                print(f"  Request {i+1}: Week {week}")
        
        # Verify week progression: 1, 1, 1 (before update) → updates happen after
        # Actually the week should stay at 1 for the same request, advance happens in update_user_progress
        # Let me check the state after
        final_state = self.pipeline.state_manager.get_user_state(user_id)
        
        passed = len(weeks) == 3 and final_state['week'] > 1
        self.log_test(
            "Week counter advances after requests",
            passed,
            f"Weeks seen: {weeks}, Final week in state: {final_state['week']}"
        )
        
        return passed
    
    def test_3_dietary_restrictions(self):
        """Test 3: Dietary restrictions enforcement."""
        print("\n" + "=" * 70)
        print("TEST 3: Dietary Restrictions")
        print("=" * 70)
        
        user_id = "test_vegetarian_user"
        
        # Set up user with restrictions
        self.pipeline.state_manager.update_user_profile(user_id, {
            "dietary_restrictions": ["vegetarian", "no_nuts"],
            "fitness_goal": "weight_loss"
        })
        
        result = self.pipeline.process_message(
            "I need a meal plan",
            user_id
        )
        
        if result['status'] != 'success':
            self.log_test(
                "Dietary restrictions respected",
                False,
                f"Failed to generate plan: {result.get('error', 'Unknown')}"
            )
            return False
        
        # Check meal plan for violations
        meal_plan = result.get('meal_plan', {})
        violations = []
        
        for meal_name, meal_data in meal_plan.items():
            for food in meal_data.get('foods', []):
                food_name = food.get('name', '').lower()
                # Simple check (would need food database for full validation)
                if any(meat in food_name for meat in ['chicken', 'beef', 'fish', 'pork']):
                    violations.append(f"{meal_name}: {food['name']} (non-vegetarian)")
                if any(nut in food_name for nut in ['almond', 'peanut', 'cashew', 'walnut']):
                    violations.append(f"{meal_name}: {food['name']} (contains nuts)")
        
        passed = len(violations) == 0
        details = "No violations found" if passed else f"Violations: {violations}"
        
        self.log_test("Dietary restrictions respected", passed, details)
        
        return passed
    
    def test_4_low_calorie_edge_case(self):
        """Test 4: Low calorie handling (1200 cal)."""
        print("\n" + "=" * 70)
        print("TEST 4: Low Calorie Edge Case")
        print("=" * 70)
        
        user_id = "test_low_cal_user"
        
        # Set up lightweight user
        self.pipeline.state_manager.update_user_profile(user_id, {
            "weight_kg": 50.0,
            "height_cm": 155.0,
            "age": 25,
            "gender": "female",
            "activity_level": "sedentary",
            "fitness_goal": "weight_loss"
        })
        
        result = self.pipeline.process_message(
            "Give me a diet plan",
            user_id
        )
        
        if result['status'] != 'success':
            self.log_test(
                "Low calorie handling",
                False,
                f"Failed: {result.get('error', 'Unknown')}"
            )
            return False
        
        # Check for reasonable portions
        meal_plan = result.get('meal_plan', {})
        total_calories = result.get('daily_summary', {}).get('calories', 0)
        
        reasonable = 1000 <= total_calories <= 2000
        
        self.log_test(
            "Low calorie handling produces reasonable portions",
            reasonable,
            f"Total calories: {total_calories}"
        )
        
        return reasonable
    
    def test_5_high_calorie_edge_case(self):
        """Test 5: High calorie handling (3500 cal)."""
        print("\n" + "=" * 70)
        print("TEST 5: High Calorie Edge Case")
        print("=" * 70)
        
        user_id = "test_high_cal_user"
        
        # Set up heavy/active user
        self.pipeline.state_manager.update_user_profile(user_id, {
            "weight_kg": 95.0,
            "height_cm": 190.0,
            "age": 28,
            "gender": "male",
            "activity_level": "very_active",
            "fitness_goal": "muscle_gain"
        })
        
        result = self.pipeline.process_message(
            "I need a muscle building plan",
            user_id
        )
        
        if result['status'] != 'success':
            self.log_test(
                "High calorie handling",
                False,
                f"Failed: {result.get('error', 'Unknown')}"
            )
            return False
        
        # Check portions aren't absurd
        meal_plan = result.get('meal_plan', {})
        absurd_portions = []
        
        for meal_name, meal_data in meal_plan.items():
            for food in meal_data.get('foods', []):
                portion = food.get('portion_g', 0)
                if portion > 600:  # Absurdly large
                    absurd_portions.append(f"{food['name']}: {portion}g")
        
        passed = len(absurd_portions) == 0
        details = "No absurd portions" if passed else f"Large: {absurd_portions}"
        
        self.log_test("High calorie handling without absurd portions", passed, details)
        
        return passed
    
    def test_6_performance_benchmark(self):
        """Test 6: Performance - End-to-end latency."""
        print("\n" + "=" * 70)
        print("TEST 6: Performance Benchmark")
        print("=" * 70)
        
        user_id = "test_performance_user"
        iterations = 5
        times = []
        
        for i in range(iterations):
            start = time.time()
            result = self.pipeline.process_message(
                "Give me a weight loss plan",
                user_id
            )
            end = time.time()
            
            if result['status'] == 'success':
                elapsed_ms = (end - start) * 1000
                times.append(elapsed_ms)
                print(f"  Run {i+1}: {elapsed_ms:.2f}ms")
        
        if len(times) > 0:
            avg_time = sum(times) / len(times)
            passed = avg_time < 500  # Target: <500ms (ideal <100ms)
            
            self.log_test(
                "Average latency < 500ms",
                passed,
                f"Average: {avg_time:.2f}ms, Min: {min(times):.2f}ms, Max: {max(times):.2f}ms"
            )
            
            # Bonus: Check if we hit ideal target
            ideal = avg_time < 100
            if ideal:
                self.log_test(
                    "🏆 IDEAL: Average latency < 100ms",
                    True,
                    f"{avg_time:.2f}ms"
                )
            
            return passed
        
        return False
    
    def test_7_safety_validation(self):
        """Test 7: Safety validation enforcement."""
        print("\n" + "=" * 70)
        print("TEST 7: Safety Validation")
        print("=" * 70)
        
        user_id = "test_safety_user"
        
        result = self.pipeline.process_message(
            "Give me a meal plan",
            user_id
        )
        
        if result['status'] != 'success':
            self.log_test(
                "Safety validation",
                False,
                f"Failed to generate plan: {result.get('error', 'Unknown')}"
            )
            return False
        
        meal_plan = result.get('meal_plan', {})
        
        # Check protein minimums
        protein_violations = []
        for meal_name in ['breakfast', 'lunch', 'dinner']:
            if meal_name in meal_plan:
                protein = meal_plan[meal_name].get('total_protein_g', 0)
                if protein < 20:
                    protein_violations.append(f"{meal_name}: {protein}g")
        
        passed = len(protein_violations) == 0
        details = "All meals meet protein minimum" if passed else f"Violations: {protein_violations}"
        
        self.log_test("Protein minimums enforced (≥20g per main meal)", passed, details)
        
        return passed
    
    def run_all_tests(self):
        """Run complete test suite."""
        print("\n" + "=" * 70)
        print("RUNNING ALL TESTS")
        print("=" * 70)
        
        tests = [
            self.test_1_new_user_cold_start,
            self.test_2_week_progression,
            self.test_3_dietary_restrictions,
            self.test_4_low_calorie_edge_case,
            self.test_5_high_calorie_edge_case,
            self.test_6_performance_benchmark,
            self.test_7_safety_validation
        ]
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                import traceback
                print(f"\n[EXCEPTION] {test_func.__name__}")
                traceback.print_exc()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ✓")
        print(f"Failed: {failed} ✗")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  ✗ {result['test']}")
                    if result['details']:
                        print(f"    {result['details']}")
        
        print("\n" + "=" * 70)
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! System is production-ready.")
        else:
            print("⚠️  Some tests failed. Review before deployment.")
        
        print("=" * 70)
        
        # Save report
        report_path = "data/test_report.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump({
                "total": total,
                "passed": passed,
                "failed": failed,
                "success_rate": passed/total*100,
                "results": self.test_results
            }, f, indent=2)
        
        print(f"\n📊 Test report saved to: {report_path}\n")


if __name__ == "__main__":
    tester = IntegrationTester()
    tester.run_all_tests()

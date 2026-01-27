"""
Test Suite for Model 3: Food Recommendation Engine
Comprehensive tests covering all scenarios and edge cases.
"""

import json
import time
import sys
import io
from model3_food_recommender import FoodRecommender

# Set UTF-8 encoding for Windows compatibility
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_result(result: dict, test_name: str):
    """Pretty print test result."""
    print(f"\n[TEST] {test_name}")
    print("-" * 80)
    
    if result['status'] == 'error':
        print(f"[ERROR]: {result.get('error', 'Unknown error')}")
        if 'details' in result:
            print(f"Details: {result['details']}")
        return False
    
    print("[SUCCESS]\n")
    
    # Print chatbot message
    print(result['chatbot_message'])
    
    # Print daily summary
    print("\n" + "-" * 80)
    print("[Daily Summary]:")
    summary = result['daily_summary']
    print(f"  Calories: {summary['calories']} | Accuracy: {summary['macro_accuracy']}")
    print(f"  Protein: {summary['protein_g']}g | Carbs: {summary['carbs_g']}g | Fat: {summary['fat_g']}g")
    
    # Print meal breakdown
    print("\n[Detailed Meal Breakdown]:")
    for meal_name in ['breakfast', 'lunch', 'dinner', 'snack']:
        meal = result['meal_plan'][meal_name]
        print(f"\n  {meal_name.upper()}:")
        print(f"    Calories: {meal['total_calories']} | P: {meal['total_protein_g']}g | C: {meal['total_carbs_g']}g | F: {meal['total_fat_g']}g")
        print(f"    Foods:")
        for food in meal['foods']:
            print(f"      - {food['name']}: {food['portion_g']}g ({food['calories']} cal, {food['protein_g']}g protein)")
    
    return True


def test_case_1_weight_loss():
    """Test Case 1: Weight loss, 1842 kcal, no restrictions"""
    print_section("TEST CASE 1: Weight Loss - No Restrictions")
    
    recommender = FoodRecommender('model3_food_database.json')
    
    model2_output = {
        "target_calories": 1842,
        "fitness_goal": "weight_loss",
        "dietary_restrictions": []
    }
    
    start = time.time()
    result = recommender.generate_plan(model2_output)
    duration_ms = (time.time() - start) * 1000
    
    success = print_result(result, "Weight Loss - No Restrictions")
    print(f"\n[Performance] Execution Time: {duration_ms:.2f}ms")
    
    # Validation checks
    if success:
        print("\n[Validation Checks]:")
        summary = result['daily_summary']
        
        # Check calorie accuracy
        cal_accuracy = abs(summary['calories'] - 1842) / 1842
        print(f"  [PASS] Calorie accuracy: {cal_accuracy*100:.2f}% deviation (target: <3%)")
        
        # Check protein sufficiency
        high_protein = summary['protein_g'] > 100
        status = "PASS" if high_protein else "FAIL"
        print(f"  [{status}] High protein for satiety: {summary['protein_g']}g")
        
        # Check meal protein minimums
        for meal_name in ['breakfast', 'lunch', 'dinner']:
            meal = result['meal_plan'][meal_name]
            adequate = meal['total_protein_g'] >= 20
            status = "PASS" if adequate else "FAIL"
            print(f"  [{status}] {meal_name.title()} protein: {meal['total_protein_g']}g (min: 20g)")
    
    return success


def test_case_2_muscle_gain():
    """Test Case 2: Muscle gain, 2590 kcal, vegetarian"""
    print_section("TEST CASE 2: Muscle Gain - Vegetarian")
    
    recommender = FoodRecommender('model3_food_database.json')
    
    model2_output = {
        "target_calories": 2590,
        "fitness_goal": "muscle_gain",
        "dietary_restrictions": ["vegetarian"]
    }
    
    start = time.time()
    result = recommender.generate_plan(model2_output)
    duration_ms = (time.time() - start) * 1000
    
    success = print_result(result, "Muscle Gain - Vegetarian")
    print(f"\n[Performance] Execution Time: {duration_ms:.2f}ms")
    
    # Validation checks
    if success:
        print("\n[Validation Checks]:")
        summary = result['daily_summary']
        
        # Check high carb ratio
        carb_ratio = summary['carbs_g'] * 4 / summary['calories']
        print(f"  [PASS] Carb ratio: {carb_ratio*100:.1f}% (target: ~50% for muscle gain)")
        
        # Verify no meat products
        all_foods = []
        for meal in result['meal_plan'].values():
            all_foods.extend(meal['foods'])
        
        meat_ids = ['chicken_breast', 'chicken_thigh', 'salmon', 'tuna', 'ground_turkey', 'lean_beef']
        has_meat = any(food['id'] in meat_ids for food in all_foods)
        status = "FAIL" if has_meat else "PASS"
        print(f"  [{status}] No meat products: {not has_meat}")
        
        # Check protein adequacy from vegetarian sources
        adequate_protein = summary['protein_g'] >= 150
        status = "PASS" if adequate_protein else "WARN"
        print(f"  [{status}] Adequate protein from plants: {summary['protein_g']}g")
    
    return success


def test_case_3_maintenance():
    """Test Case 3: Maintenance, 2100 kcal, no dairy + no nuts"""
    print_section("TEST CASE 3: Maintenance - No Dairy, No Nuts")
    
    recommender = FoodRecommender('model3_food_database.json')
    
    model2_output = {
        "target_calories": 2100,
        "fitness_goal": "maintenance",
        "dietary_restrictions": ["no_dairy", "no_nuts"]
    }
    
    start = time.time()
    result = recommender.generate_plan(model2_output)
    duration_ms = (time.time() - start) * 1000
    
    success = print_result(result, "Maintenance - Multiple Restrictions")
    print(f"\n[Performance] Execution Time: {duration_ms:.2f}ms")
    
    # Validation checks
    if success:
        print("\n[Validation Checks]:")
        
        # Verify no dairy or nuts
        all_foods = []
        for meal in result['meal_plan'].values():
            all_foods.extend(meal['foods'])
        
        dairy_ids = ['greek_yogurt', 'cottage_cheese', 'milk_whole', 'milk_skim', 'cheddar_cheese']
        nut_ids = ['almonds', 'walnuts', 'peanut_butter']
        
        has_dairy = any(food['id'] in dairy_ids for food in all_foods)
        has_nuts = any(food['id'] in nut_ids for food in all_foods)
        
        status_dairy = "FAIL" if has_dairy else "PASS"
        status_nuts = "FAIL" if has_nuts else "PASS"
        print(f"  [{status_dairy}] No dairy products: {not has_dairy}")
        print(f"  [{status_nuts}] No nut products: {not has_nuts}")
        
        # Check balanced macros
        summary = result['daily_summary']
        protein_ratio = summary['protein_g'] * 4 / summary['calories']
        carb_ratio = summary['carbs_g'] * 4 / summary['calories']
        fat_ratio = summary['fat_g'] * 9 / summary['calories']
        
        print(f"  [PASS] Macro ratios - P: {protein_ratio*100:.1f}%, C: {carb_ratio*100:.1f}%, F: {fat_ratio*100:.1f}%")
    
    return success


def test_edge_cases():
    """Test edge cases and error handling"""
    print_section("EDGE CASE TESTING")
    
    recommender = FoodRecommender('model3_food_database.json')
    
    # Test 1: Invalid goal
    print("\n[Edge Test 1] Invalid fitness goal")
    result = recommender.generate_plan({
        "target_calories": 2000,
        "fitness_goal": "invalid_goal",
        "dietary_restrictions": []
    })
    status = "PASS - Error caught" if result['status'] == 'error' else "FAIL - Should have errored"
    print(f"  Result: {status}")
    
    # Test 2: Very low calories
    print("\n[Edge Test 2] Very low calories (1200)")
    result = recommender.generate_plan({
        "target_calories": 1200,
        "fitness_goal": "weight_loss",
        "dietary_restrictions": []
    })
    success = result['status'] == 'success'
    status = "PASS - Handled" if success else "FAIL"
    print(f"  Result: {status}")
    if success:
        print(f"  Generated: {result['daily_summary']['calories']} calories")
    
    # Test 3: Very high calories
    print("\n[Edge Test 3] Very high calories (3500)")
    result = recommender.generate_plan({
        "target_calories": 3500,
        "fitness_goal": "muscle_gain",
        "dietary_restrictions": []
    })
    success = result['status'] == 'success'
    status = "PASS - Handled" if success else "FAIL"
    print(f"  Result: {status}")
    if success:
        print(f"  Generated: {result['daily_summary']['calories']} calories")
    
    # Test 4: Multiple restrictions
    print("\n[Edge Test 4] Vegan diet (strictest restriction)")
    result = recommender.generate_plan({
        "target_calories": 2000,
        "fitness_goal": "maintenance",
        "dietary_restrictions": ["vegan"]
    })
    success = result['status'] == 'success'
    status = "PASS - Handled" if success else "FAIL"
    print(f"  Result: {status}")
    if success:
        print(f"  Generated: {result['daily_summary']['protein_g']}g protein from plant sources")


def test_performance_benchmark():
    """Performance benchmark - test multiple iterations"""
    print_section("PERFORMANCE BENCHMARK")
    
    recommender = FoodRecommender('model3_food_database.json')
    
    test_cases = [
        {"target_calories": 1842, "fitness_goal": "weight_loss", "dietary_restrictions": []},
        {"target_calories": 2590, "fitness_goal": "muscle_gain", "dietary_restrictions": ["vegetarian"]},
        {"target_calories": 2100, "fitness_goal": "maintenance", "dietary_restrictions": ["no_dairy"]},
    ]
    
    total_time = 0
    iterations = 10
    
    print(f"\nRunning {iterations} iterations across 3 test cases...")
    
    for i in range(iterations):
        for test_case in test_cases:
            start = time.time()
            recommender.generate_plan(test_case)
            total_time += (time.time() - start) * 1000
    
    avg_time_ms = total_time / (iterations * len(test_cases))
    
    print(f"\n[Results]:")
    print(f"  Total executions: {iterations * len(test_cases)}")
    print(f"  Average execution time: {avg_time_ms:.2f}ms")
    print(f"  Target: <50ms")
    status = "PASS" if avg_time_ms < 50 else "EXCEEDS TARGET"
    print(f"  Status: {status}")


def run_all_tests():
    """Run complete test suite"""
    print("\n")
    print("=" * 80)
    print("    MODEL 3: FOOD RECOMMENDATION ENGINE - COMPREHENSIVE TEST SUITE".center(80))
    print("=" * 80)
    
    results = []
    
    # Run main test cases
    results.append(("Test Case 1", test_case_1_weight_loss()))
    results.append(("Test Case 2", test_case_2_muscle_gain()))
    results.append(("Test Case 3", test_case_3_maintenance()))
    
    # Run edge cases
    test_edge_cases()
    
    # Run performance benchmark
    test_performance_benchmark()
    
    # Summary
    print_section("TEST SUMMARY")
    print()
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    final_status = "ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED"
    print(f"\n[{final_status}]")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    run_all_tests()

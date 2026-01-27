"""
Manual Test Script for Model 3 Food Recommendation Engine
Run this to manually test with different inputs
"""

from model3_food_recommender import FoodRecommender
import json


def print_separator():
    print("\n" + "=" * 80 + "\n")


def display_result(result, test_name):
    """Display the meal plan result in a readable format"""
    print(f"TEST: {test_name}")
    print_separator()
    
    if result['status'] == 'error':
        print(f"ERROR: {result['error']}")
        return
    
    # Print chatbot message
    print("CHATBOT MESSAGE:")
    print("-" * 80)
    print(result['chatbot_message'])
    
    # Print detailed breakdown
    print_separator()
    print("DETAILED MEAL PLAN:")
    print("-" * 80)
    
    for meal_name in ['breakfast', 'lunch', 'dinner', 'snack']:
        meal = result['meal_plan'][meal_name]
        print(f"\n{meal_name.upper()}:")
        print(f"  Total: {meal['total_calories']} cal | {meal['total_protein_g']}g protein | {meal['total_carbs_g']}g carbs | {meal['total_fat_g']}g fat")
        print(f"  Foods:")
        for food in meal['foods']:
            print(f"    - {food['name']}: {food['portion_g']}g")
    
    # Print daily summary
    print_separator()
    print("DAILY SUMMARY:")
    print("-" * 80)
    summary = result['daily_summary']
    print(f"  Total Calories: {summary['calories']}")
    print(f"  Total Protein: {summary['protein_g']}g")
    print(f"  Total Carbs: {summary['carbs_g']}g")
    print(f"  Total Fat: {summary['fat_g']}g")
    print(f"  Accuracy: {summary['macro_accuracy']}")
    print_separator()


def main():
    print("\n" + "=" * 80)
    print("  MODEL 3: FOOD RECOMMENDATION ENGINE - MANUAL TEST".center(80))
    print("=" * 80)
    
    # Initialize recommender
    print("\nInitializing Food Recommender...")
    recommender = FoodRecommender('model3_food_database.json')
    print("[OK] Successfully loaded 53 foods from database\n")
    
    # ========================================================================
    # SAMPLE INPUT 1: Weight Loss - No Restrictions
    # ========================================================================
    print("\n" + "#" * 80)
    print("# SAMPLE 1: Weight Loss Goal (1842 calories, no restrictions)")
    print("#" * 80)
    
    input1 = {
        "target_calories": 1842,
        "fitness_goal": "weight_loss",
        "dietary_restrictions": []
    }
    
    print("\nInput:")
    print(json.dumps(input1, indent=2))
    print("\nGenerating meal plan...")
    
    result1 = recommender.generate_plan(input1)
    display_result(result1, "Weight Loss - No Restrictions")
    
    # ========================================================================
    # SAMPLE INPUT 2: Muscle Gain - Vegetarian
    # ========================================================================
    print("\n" + "#" * 80)
    print("# SAMPLE 2: Muscle Gain Goal (2590 calories, vegetarian)")
    print("#" * 80)
    
    input2 = {
        "target_calories": 2590,
        "fitness_goal": "muscle_gain",
        "dietary_restrictions": ["vegetarian"]
    }
    
    print("\nInput:")
    print(json.dumps(input2, indent=2))
    print("\nGenerating meal plan...")
    
    result2 = recommender.generate_plan(input2)
    display_result(result2, "Muscle Gain - Vegetarian")
    
    # ========================================================================
    # SAMPLE INPUT 3: Maintenance - No Dairy, No Nuts
    # ========================================================================
    print("\n" + "#" * 80)
    print("# SAMPLE 3: Maintenance Goal (2100 calories, no dairy & no nuts)")
    print("#" * 80)
    
    input3 = {
        "target_calories": 2100,
        "fitness_goal": "maintenance",
        "dietary_restrictions": ["no_dairy", "no_nuts"]
    }
    
    print("\nInput:")
    print(json.dumps(input3, indent=2))
    print("\nGenerating meal plan...")
    
    result3 = recommender.generate_plan(input3)
    display_result(result3, "Maintenance - Multiple Restrictions")
    
    # ========================================================================
    # SAMPLE INPUT 4: Custom Test
    # ========================================================================
    print("\n" + "#" * 80)
    print("# SAMPLE 4: Your Custom Test")
    print("#" * 80)
    print("\nYou can modify this section to test your own inputs!")
    print("Available fitness goals: 'weight_loss', 'muscle_gain', 'maintenance'")
    print("Available restrictions: 'vegetarian', 'vegan', 'no_dairy', 'no_nuts', 'no_eggs', 'no_fish', 'no_gluten', 'no_soy'")
    
    # MODIFY THIS INPUT TO TEST YOUR OWN SCENARIO
    custom_input = {
        "target_calories": 2000,        # Change this value
        "fitness_goal": "weight_loss",  # Change to: weight_loss, muscle_gain, or maintenance
        "dietary_restrictions": ["vegan"]  # Add your restrictions here
    }
    
    print("\nCustom Input:")
    print(json.dumps(custom_input, indent=2))
    print("\nGenerating meal plan...")
    
    custom_result = recommender.generate_plan(custom_input)
    display_result(custom_result, "Custom Test")
    
    print("\n" + "=" * 80)
    print("  MANUAL TESTING COMPLETE".center(80))
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

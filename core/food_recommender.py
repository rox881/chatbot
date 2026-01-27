"""
Food Recommender Wrapper: Model 3
Wraps the rule-based food recommendation engine.
"""

import sys
import os

# Add model_3_build to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'model_3_build'))

from model3_food_recommender import FoodRecommender as FoodEngine


class FoodRecommender:
    """
    Wrapper for Model 3: Rule-Based Food Recommendation Engine.
    Intentionally rule-based for safety-critical nutrition recommendations.
    """
    
    def __init__(self, database_path: str):
        """
        Initialize Food Recommender.
        
        Args:
            database_path: Path to food database JSON
        """
        self.database_path = database_path
        self.engine = FoodEngine(database_path)
    
    def generate_plan(self, target_calories: int, fitness_goal: str, 
                     dietary_restrictions: list = None) -> dict:
        """
        Generate meal plan from Model 2 output.
        
        Args:
            target_calories: Daily calorie target from Model 2
            fitness_goal: Fitness goal (weight_loss, muscle_gain, maintenance)
            dietary_restrictions: List of dietary restrictions
        
        Returns:
            Complete meal plan with daily summary
        """
        if dietary_restrictions is None:
            dietary_restrictions = []
        
        # Build input for Model 3 engine
        model2_output = {
            "target_calories": target_calories,
            "fitness_goal": fitness_goal,
            "dietary_restrictions": dietary_restrictions
        }
        
        # Generate plan using Model 3 engine
        result = self.engine.generate_plan(model2_output)
        
        return result


# Standalone test
if __name__ == "__main__":
    print("=" * 60)
    print("Food Recommender (Model 3) - Test")
    print("=" * 60)
    
    database_path = "model_3_build/model3_food_database.json"
    
    try:
        recommender = FoodRecommender(database_path)
        
        print("\n[Testing Food Recommendation]\n")
        
        # Test case
        result = recommender.generate_plan(
            target_calories=1800,
            fitness_goal="weight_loss",
            dietary_restrictions=[]
        )
        
        if result['status'] == 'success':
            print("✓ Meal plan generated successfully!\n")
            print(result['chatbot_message'])
            print(f"\nDaily Accuracy: {result['daily_summary']['macro_accuracy']}")
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")
        
        # Test with restrictions
        print("\n[Testing with Dietary Restrictions]\n")
        result2 = recommender.generate_plan(
            target_calories=2000,
            fitness_goal="muscle_gain",
            dietary_restrictions=["vegetarian"]
        )
        
        if result2['status'] == 'success':
            print("✓ Vegetarian meal plan generated successfully!")
        
        print("\n" + "=" * 60)
        print("Model 3 loaded successfully! ✓")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print("Make sure you're running from the chatbot root directory.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

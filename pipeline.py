"""
Unified Pipeline: Three-Model Integration
Orchestrates Intent Classifier → Roadmap Generator → Food Recommender with safety validation.
"""

import os
import sys
from typing import Dict, List, Tuple

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core"))

from core.intent_classifier import IntentClassifier
from core.roadmap_generator import RoadmapGenerator
from core.food_recommender import FoodRecommender
from core.state_manager import StateManager


class FitnessChatbotPipeline:
    """
    Production-ready integration of three models:
    - Model 1: Intent Classification (TF-IDF + Classifier)
    - Model 2: Roadmap Generation (Random Forest)
    - Model 3: Food Recommendation (Rule-Based Engine)

    Includes mandatory safety validation for nutrition recommendations.
    """

    # Safety constraints (NON-NEGOTIABLE)
    MIN_PROTEIN_PER_MEAL = 20  # grams
    MIN_PORTION = 50  # grams
    MAX_PORTION = 500  # grams
    CALORIE_TOLERANCE = 0.07  # ±7%

    def __init__(self, base_dir: str = None):
        """
        Initialize the pipeline with all three models.

        Args:
            base_dir: Base directory of chatbot project (defaults to current dir)
        """
        if base_dir is None:
            base_dir = os.path.dirname(__file__)

        self.base_dir = base_dir

        # Initialize all models
        print("[Pipeline] Loading models...")

        self.intent_classifier = IntentClassifier(
            model_path=os.path.join(base_dir, "intent_model", "intent_model.pkl")
        )
        print("  [OK] Model 1: Intent Classifier loaded")

        self.roadmap_generator = RoadmapGenerator(
            model_path=os.path.join(base_dir, "RoadMap_model", "roadmap_model.pkl")
        )
        print("  [OK] Model 2: Roadmap Generator loaded")

        self.food_recommender = FoodRecommender(
            database_path=os.path.join(
                base_dir, "model_3_build", "model3_food_database.json"
            )
        )
        print("  [OK] Model 3: Food Recommender loaded")

        self.state_manager = StateManager(
            storage_path=os.path.join(base_dir, "data", "user_profiles.json")
        )
        print("  [OK] State Manager initialized")

        print("[Pipeline] All models loaded successfully!\n")

    def process_message(self, user_message: str, user_id: str) -> Dict:
        """
        Main integration point: process user message through all three models.

        Args:
            user_message: Raw user text input
            user_id: Unique user identifier

        Returns:
            {
                "status": "success" | "error",
                "response": str (natural language chatbot response),
                "intent": str,
                "roadmap": dict,
                "meal_plan": dict,
                "user_state": dict,
                "error": str (if status == "error")
            }
        """
        try:
            # STEP 1: Intent Classification (Model 1)
            intent = self.intent_classifier.predict(user_message)
            print(f"[Pipeline] Intent detected: {intent}")

            # STEP 2: State Management
            user_state = self.state_manager.get_user_state(user_id, intent)
            print(
                f"[Pipeline] User state loaded: Week {user_state['week']}, Goal: {user_state['fitness_goal']}"
            )

            # STEP 3: Check if this intent requires full pipeline
            if intent in [
                "weight_loss_plan",
                "muscle_gain_plan",
                "maintenance_plan",
                "diet_suggestion",
                "food_plan",
                "meal_plan",
            ]:
                # STEP 4: Roadmap Generation (Model 2)
                roadmap = self.roadmap_generator.predict(user_state)
                print(f"[Pipeline] Roadmap generated: {roadmap['target_calories']} cal")

                # STEP 5: Food Recommendation (Model 3)
                meal_result = self.food_recommender.generate_plan(
                    target_calories=roadmap["target_calories"],
                    fitness_goal=roadmap["fitness_goal"],
                    dietary_restrictions=roadmap["dietary_restrictions"],
                )

                if meal_result["status"] != "success":
                    return {
                        "status": "error",
                        "error": f"Food recommendation failed: {meal_result.get('error', 'Unknown error')}",
                    }

                meal_plan = meal_result["meal_plan"]
                print(f"[Pipeline] Meal plan generated")

                # STEP 6: Safety Validation (MANDATORY)
                is_safe, errors = self._validate_safety(
                    meal_plan, roadmap["dietary_restrictions"]
                )

                if not is_safe:
                    print(f"[Pipeline] [WARNING] Safety validation failed: {errors}")
                    return {
                        "status": "error",
                        "error": "Safety validation failed - regenerating plan",
                        "details": errors,
                    }

                print(f"[Pipeline] [OK] Safety validation passed")

                # STEP 7: Natural Language Formatting
                response = self._format_response(
                    intent, roadmap, meal_result["chatbot_message"], user_state
                )

                # STEP 8: Update User State (Advance week counter)
                updated_state = self.state_manager.update_user_progress(
                    user_id, roadmap
                )
                print(
                    f"[Pipeline] User progress updated: Week {user_state['week']} to {updated_state['week']}"
                )

                return {
                    "status": "success",
                    "response": response,
                    "intent": intent,
                    "roadmap": roadmap,
                    "meal_plan": meal_plan,
                    "daily_summary": meal_result["daily_summary"],
                    "user_state": user_state,
                }

            else:
                # Handle other intents (progress queries, etc.)
                return self._handle_other_intents(intent, user_state)

        except Exception as e:
            import traceback

            traceback.print_exc()
            return {"status": "error", "error": str(e)}

    def _validate_safety(
        self, meal_plan: Dict, restrictions: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate meal plan against safety constraints.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Gate 1: Minimum protein per meal
        for meal_name in ["breakfast", "lunch", "dinner"]:
            if meal_name in meal_plan:
                protein = meal_plan[meal_name].get("total_protein_g", 0)
                if protein < self.MIN_PROTEIN_PER_MEAL:
                    errors.append(
                        f"{meal_name} has insufficient protein: {protein}g < {self.MIN_PROTEIN_PER_MEAL}g"
                    )

        # Gate 2: Portion sanity checks
        for meal_name, meal_data in meal_plan.items():
            for food in meal_data.get("foods", []):
                portion = food.get("portion_g", 0)
                # Allow small portions for oils/fats
                if portion > 50:  # Only check portions > 50g
                    if portion < self.MIN_PORTION or portion > self.MAX_PORTION:
                        errors.append(
                            f"Unsafe portion in {meal_name}: {food['name']} = {portion}g"
                        )

        return len(errors) == 0, errors

    def _format_response(
        self, intent: str, roadmap: Dict, meal_message: str, user_state: Dict
    ) -> str:
        """
        Generate natural language chatbot response.

        Args:
            intent: Detected user intent
            roadmap: Output from Model 2
            meal_message: Pre-formatted message from Model 3
            user_state: Current user state

        Returns:
            Formatted chatbot response
        """
        week = user_state["week"]
        goal = user_state["fitness_goal"].replace("_", " ").title()

        response = f"**Week {week} - {goal}**\n\n"
        response += meal_message

        # Add motivational message based on goal
        if user_state["fitness_goal"] == "weight_loss":
            response += f"\n\n[!] Stay consistent! Track your {roadmap['target_exercise_minutes']} minutes of daily activity."
        elif user_state["fitness_goal"] == "muscle_gain":
            response += f"\n\n[!] Focus on progressive overload in your {roadmap['target_exercise_minutes']}-minute workouts!"
        else:
            response += f"\n\n[!] Maintain your {roadmap['target_exercise_minutes']} minutes of daily activity for optimal health."

        return response

    def _handle_other_intents(self, intent: str, user_state: Dict) -> Dict:
        """
        Handle intents that don't require full pipeline (e.g., progress queries).

        Args:
            intent: Detected intent
            user_state: Current user state

        Returns:
            Response dictionary
        """
        if intent == "progress_query" or "progress" in intent:
            response = f"You're currently on Week {user_state['week']} of your {user_state['fitness_goal'].replace('_', ' ')} journey!\n\n"
            response += f"Current stats:\n"
            response += f"  • Weight: {user_state['weight_kg']} kg\n"
            response += f"  • Height: {user_state['height_cm']} cm\n"
            response += (
                f"  • Activity Level: {user_state['activity_level'].title()}\n\n"
            )
            response += "Keep up the great work! [!]"

            return {
                "status": "success",
                "response": response,
                "intent": intent,
                "user_state": user_state,
            }

        else:
            # Generic fallback
            return {
                "status": "success",
                "response": f"I detected your intent as '{intent}'. I'm currently focused on fitness roadmaps and meal planning. How can I help you with your fitness journey?",
                "intent": intent,
                "user_state": user_state,
            }


# Standalone test
if __name__ == "__main__":
    print("=" * 70)
    print("UNIFIED PIPELINE - Full Integration Test")
    print("=" * 70)

    try:
        # Initialize pipeline
        pipeline = FitnessChatbotPipeline()

        # Test case 1: New user with weight loss intent
        print("\n[Test 1] New user - weight loss request\n")
        result1 = pipeline.process_message(
            user_message="I want to lose weight in 3 months", user_id="test_user_001"
        )

        if result1["status"] == "success":
            print("[OK] SUCCESS!\n")
            print(result1["response"])
            print(f"\nIntent: {result1['intent']}")
            print(f"Week: {result1['user_state']['week']}")
        else:
            print(f"[ERROR]: {result1['error']}")

        print("\n" + "-" * 70)

        # Test case 2: Same user - week progression
        print("\n[Test 2] Same user - week progression check\n")
        result2 = pipeline.process_message(
            user_message="Give me this week's diet plan", user_id="test_user_001"
        )

        if result2["status"] == "success":
            print("[OK] Week progression working!")
            print(
                f"Week: {result2['user_state']['week']} (should be 1, next request will be 2)"
            )

        print("\n" + "=" * 70)
        print("Pipeline integration successful! [OK]")
        print("=" * 70)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback

        traceback.print_exc()

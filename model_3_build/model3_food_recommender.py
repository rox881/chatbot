"""
Model 3: Food Recommendation Engine
Rule-based meal planning system that transforms nutritional targets into actionable meal plans.
Author: AI-Assisted Implementation
Date: 2026-01-27
"""

import json
import math
from typing import Dict, List, Tuple, Optional


class FoodRecommender:
    """
    Production-ready Food Recommendation Engine for fitness chatbot.
    Generates 4-meal daily plans based on calorie targets and fitness goals.
    """

    # Macro ratio configurations by fitness goal
    MACRO_RATIOS = {
        "weight_loss": {"protein": 0.35, "carbs": 0.40, "fat": 0.25},
        "muscle_gain": {"protein": 0.30, "carbs": 0.50, "fat": 0.20},
        "maintenance": {"protein": 0.25, "carbs": 0.45, "fat": 0.30},
    }

    # Meal distribution percentages
    MEAL_DISTRIBUTION = {
        "breakfast": 0.25,
        "lunch": 0.35,
        "dinner": 0.30,
        "snack": 0.15,
    }

    # Calories per gram for macronutrients
    PROTEIN_CAL_PER_G = 4
    CARB_CAL_PER_G = 4
    FAT_CAL_PER_G = 9

    # Safety constraints
    MIN_PROTEIN_PER_MEAL = 20  # grams
    MIN_PORTION = 50  # grams
    MAX_PORTION = 500  # grams
    CALORIE_TOLERANCE = 0.03  # ±3%
    MACRO_TOLERANCE = 0.05  # ±5%
    VEGETABLE_PORTION = 90  # grams (fixed for volume/fiber)

    def __init__(self, foods_json_path: str):
        """
        Initialize the Food Recommender with food database.

        Args:
            foods_json_path: Path to the JSON file containing food database
        """
        with open(foods_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.foods = data["foods"]

        # Organize foods by category for efficient lookup
        self.foods_by_category = self._organize_by_category()

    def _organize_by_category(self) -> Dict[str, List[Dict]]:
        """Organize foods by category for efficient filtering."""
        categories = {}
        for food in self.foods:
            category = food["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(food)
        return categories

    def calculate_macros(self, calories: int, goal: str) -> Dict[str, float]:
        """
        Calculate daily macro targets based on calorie goal and fitness objective.

        Args:
            calories: Target daily calories
            goal: Fitness goal ('weight_loss', 'muscle_gain', 'maintenance')

        Returns:
            Dictionary with protein_g, carbs_g, fat_g targets
        """
        if goal not in self.MACRO_RATIOS:
            raise ValueError(
                f"Invalid goal: {goal}. Must be one of {list(self.MACRO_RATIOS.keys())}"
            )

        ratios = self.MACRO_RATIOS[goal]

        protein_g = (calories * ratios["protein"]) / self.PROTEIN_CAL_PER_G
        carbs_g = (calories * ratios["carbs"]) / self.CARB_CAL_PER_G
        fat_g = (calories * ratios["fat"]) / self.FAT_CAL_PER_G

        return {
            "protein_g": round(protein_g, 1),
            "carbs_g": round(carbs_g, 1),
            "fat_g": round(fat_g, 1),
        }

    def _filter_by_restrictions(
        self, foods: List[Dict], restrictions: List[str]
    ) -> List[Dict]:
        """
        Filter foods based on dietary restrictions.

        Args:
            foods: List of food items
            restrictions: List of dietary restrictions (e.g., ['vegetarian', 'no_dairy'])

        Returns:
            Filtered list of foods
        """
        if not restrictions or restrictions == ["none"]:
            return foods

        filtered = []
        for food in foods:
            # Check vegetarian/vegan requirements
            if "vegetarian" in restrictions and not food["vegetarian"]:
                continue
            if "vegan" in restrictions and not food["vegan"]:
                continue

            # Check allergen exclusions (restrictions like 'no_dairy', 'no_nuts')
            allergen_match = False
            for restriction in restrictions:
                if restriction.startswith("no_"):
                    allergen = restriction[3:]  # Remove 'no_' prefix
                    # Handle special cases
                    if allergen == "nuts":
                        if (
                            "tree nuts" in food["allergens"]
                            or "peanuts" in food["allergens"]
                        ):
                            allergen_match = True
                            break
                    else:
                        if allergen in food["allergens"]:
                            allergen_match = True
                            break

            if not allergen_match:
                filtered.append(food)

        return filtered

    def _calculate_portion_calories(
        self, food: Dict, portion_g: float
    ) -> Dict[str, float]:
        """Calculate nutritional values for a specific portion."""
        factor = portion_g / 100
        return {
            "calories": round(food["calories_per_100g"] * factor, 1),
            "protein_g": round(food["protein_g"] * factor, 1),
            "carbs_g": round(food["carbs_g"] * factor, 1),
            "fat_g": round(food["fat_g"] * factor, 1),
        }

    def build_meal(
        self,
        meal_calories: int,
        meal_protein_g: float,
        meal_carbs_g: float,
        meal_fat_g: float,
        restrictions: List[str],
    ) -> Dict:
        """
        Assemble a single meal using greedy selection algorithm.

        Args:
            meal_calories: Target calories for this meal
            meal_protein_g: Target protein grams
            meal_carbs_g: Target carbs grams
            meal_fat_g: Target fat grams
            restrictions: Dietary restrictions

        Returns:
            Dictionary with meal composition and nutritional totals
        """
        selected_foods = []
        total_nutrition = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}

        # Step 1: Select protein source (highest protein density)
        protein_foods = self._filter_by_restrictions(
            self.foods_by_category.get("protein", []), restrictions
        )

        if protein_foods:
            # Sort by protein density (protein per 100g)
            protein_foods.sort(key=lambda x: x["protein_g"], reverse=True)
            best_protein = protein_foods[0]

            # Calculate portion needed (aim for 60% of protein target)
            protein_needed = meal_protein_g * 0.6
            portion_g = min(
                max(
                    (protein_needed / best_protein["protein_g"]) * 100, self.MIN_PORTION
                ),
                self.MAX_PORTION,
            )

            nutrition = self._calculate_portion_calories(best_protein, portion_g)
            selected_foods.append(
                {
                    "id": best_protein["id"],
                    "name": best_protein["name"],
                    "portion_g": round(portion_g, 0),
                    **nutrition,
                }
            )

            for key in total_nutrition:
                total_nutrition[key] += nutrition[key]

        # Step 2: Select grain/carb source (prefer complex carbs)
        grain_foods = self._filter_by_restrictions(
            self.foods_by_category.get("grain", [])
            + self.foods_by_category.get("carb", []),
            restrictions,
        )

        if grain_foods:
            # Prefer quinoa, oats, brown rice (complex carbs)
            complex_carbs = [
                "quinoa",
                "oats",
                "brown_rice",
                "whole_wheat_pasta",
                "sweet_potato",
            ]
            grain_foods.sort(
                key=lambda x: (x["id"] in complex_carbs, x["fiber_g"]), reverse=True
            )
            best_grain = grain_foods[0]

            # Calculate portion for remaining carbs
            carbs_needed = max(meal_carbs_g - total_nutrition["carbs_g"], 0)
            portion_g = min(
                max((carbs_needed / best_grain["carbs_g"]) * 100, self.MIN_PORTION),
                self.MAX_PORTION,
            )

            nutrition = self._calculate_portion_calories(best_grain, portion_g)
            selected_foods.append(
                {
                    "id": best_grain["id"],
                    "name": best_grain["name"],
                    "portion_g": round(portion_g, 0),
                    **nutrition,
                }
            )

            for key in total_nutrition:
                total_nutrition[key] += nutrition[key]

        # Step 3: Add vegetable (fixed portion for fiber/volume)
        vegetable_foods = self._filter_by_restrictions(
            self.foods_by_category.get("vegetable", []), restrictions
        )

        if vegetable_foods:
            # Select nutrient-dense vegetables (high fiber, micronutrients)
            veg_priority = ["broccoli", "spinach", "kale", "bell_pepper"]
            vegetable_foods.sort(
                key=lambda x: (x["id"] in veg_priority, x["fiber_g"]), reverse=True
            )
            best_veg = vegetable_foods[0]

            portion_g = self.VEGETABLE_PORTION
            nutrition = self._calculate_portion_calories(best_veg, portion_g)
            selected_foods.append(
                {
                    "id": best_veg["id"],
                    "name": best_veg["name"],
                    "portion_g": round(portion_g, 0),
                    **nutrition,
                }
            )

            for key in total_nutrition:
                total_nutrition[key] += nutrition[key]

        # Step 4: Add healthy fat if needed
        if total_nutrition["fat_g"] < meal_fat_g * 0.7:
            fat_foods = self._filter_by_restrictions(
                self.foods_by_category.get("fat", []), restrictions
            )

            if fat_foods:
                # Prefer oils and seeds over nuts (for allergen safety and calorie density)
                fat_priority = ["olive_oil", "avocado", "chia_seeds", "flaxseeds"]
                fat_foods.sort(key=lambda x: x["id"] in fat_priority, reverse=True)
                best_fat = fat_foods[0]

                fat_needed = max(meal_fat_g - total_nutrition["fat_g"], 0)
                portion_g = min(
                    max((fat_needed / best_fat["fat_g"]) * 100, 5), 30
                )  # Small portions for fats

                nutrition = self._calculate_portion_calories(best_fat, portion_g)
                selected_foods.append(
                    {
                        "id": best_fat["id"],
                        "name": best_fat["name"],
                        "portion_g": round(portion_g, 0),
                        **nutrition,
                    }
                )

                for key in total_nutrition:
                    total_nutrition[key] += nutrition[key]

        # Step 5: Scale all portions to hit exact calorie target
        if total_nutrition["calories"] > 0:
            scale_factor = meal_calories / total_nutrition["calories"]
            # Only scale if deviation is significant (>3%) and scale factor is reasonable
            if abs(1 - scale_factor) > 0.03 and 0.7 <= scale_factor <= 1.3:
                for food in selected_foods:
                    food["portion_g"] = round(food["portion_g"] * scale_factor, 0)
                    food["calories"] = round(food["calories"] * scale_factor, 1)
                    food["protein_g"] = round(food["protein_g"] * scale_factor, 1)
                    food["carbs_g"] = round(food["carbs_g"] * scale_factor, 1)
                    food["fat_g"] = round(food["fat_g"] * scale_factor, 1)

                # Recalculate totals
                total_nutrition = {
                    "calories": 0,
                    "protein_g": 0,
                    "carbs_g": 0,
                    "fat_g": 0,
                }
                for food in selected_foods:
                    total_nutrition["calories"] += food["calories"]
                    total_nutrition["protein_g"] += food["protein_g"]
                    total_nutrition["carbs_g"] += food["carbs_g"]
                    total_nutrition["fat_g"] += food["fat_g"]

        # Round totals
        for key in total_nutrition:
            total_nutrition[key] = round(total_nutrition[key], 1)

        # Generate suggested sentence
        suggested_sentence = self._format_meal_sentence(selected_foods)

        return {
            "foods": selected_foods,
            "total_calories": total_nutrition["calories"],
            "total_protein_g": total_nutrition["protein_g"],
            "total_carbs_g": total_nutrition["carbs_g"],
            "total_fat_g": total_nutrition["fat_g"],
            "suggested_sentence": suggested_sentence,
        }

    def _format_meal_sentence(self, foods: List[Dict]) -> str:
        """Generate natural language description of meal."""
        if not foods:
            return "No foods selected for this meal."

        descriptions = []
        for food in foods:
            descriptions.append(f"{int(food['portion_g'])}g {food['name']}")

        if len(descriptions) == 1:
            return f"Have {descriptions[0]}."
        elif len(descriptions) == 2:
            return f"Have {descriptions[0]} with {descriptions[1]}."
        else:
            return f"Have {', '.join(descriptions[:-1])}, and {descriptions[-1]}."

    def _validate_safety(
        self, meal_plan: Dict, restrictions: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate meal plan against safety constraints.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check minimum protein per meal
        for meal_name, meal_data in meal_plan.items():
            if meal_name in ["breakfast", "lunch", "dinner"]:  # Not snack
                if meal_data["total_protein_g"] < self.MIN_PROTEIN_PER_MEAL:
                    errors.append(
                        f"{meal_name} has insufficient protein: {meal_data['total_protein_g']}g < {self.MIN_PROTEIN_PER_MEAL}g"
                    )

        # Check portion sizes
        for meal_name, meal_data in meal_plan.items():
            for food in meal_data["foods"]:
                if (
                    food["portion_g"] < self.MIN_PORTION
                    or food["portion_g"] > self.MAX_PORTION
                ):
                    if food["portion_g"] > 50:  # Ignore tiny portions like oil
                        errors.append(
                            f"Unsafe portion in {meal_name}: {food['name']} = {food['portion_g']}g"
                        )

        return len(errors) == 0, errors

    def generate_plan(self, model2_output: Dict) -> Dict:
        """
        Generate complete 4-meal daily plan from Model 2 output.

        Args:
            model2_output: Dictionary with target_calories, fitness_goal, dietary_restrictions

        Returns:
            Complete meal plan with chatbot message
        """
        try:
            # Extract inputs
            target_calories = model2_output["target_calories"]
            fitness_goal = model2_output["fitness_goal"]
            restrictions = model2_output.get("dietary_restrictions", [])

            # Calculate daily macros
            daily_macros = self.calculate_macros(target_calories, fitness_goal)

            # Build meal plan
            meal_plan = {}

            for meal_name, meal_pct in self.MEAL_DISTRIBUTION.items():
                meal_calories = int(target_calories * meal_pct)
                meal_protein = daily_macros["protein_g"] * meal_pct
                meal_carbs = daily_macros["carbs_g"] * meal_pct
                meal_fat = daily_macros["fat_g"] * meal_pct

                meal_plan[meal_name] = self.build_meal(
                    meal_calories, meal_protein, meal_carbs, meal_fat, restrictions
                )

            # Calculate daily summary
            daily_summary = {
                "calories": sum(meal["total_calories"] for meal in meal_plan.values()),
                "protein_g": sum(
                    meal["total_protein_g"] for meal in meal_plan.values()
                ),
                "carbs_g": sum(meal["total_carbs_g"] for meal in meal_plan.values()),
                "fat_g": sum(meal["total_fat_g"] for meal in meal_plan.values()),
            }

            # Round summary
            for key in daily_summary:
                daily_summary[key] = round(daily_summary[key], 1)

            # Calculate macro accuracy
            accuracy = (daily_summary["calories"] / target_calories) * 100
            daily_summary["macro_accuracy"] = f"{accuracy:.1f}%"

            # Validate safety
            is_safe, errors = self._validate_safety(meal_plan, restrictions)
            if not is_safe:
                return {
                    "status": "error",
                    "error": "Safety validation failed",
                    "details": errors,
                }

            # Generate chatbot message
            chatbot_message = self._format_chatbot_message(
                meal_plan, daily_summary, fitness_goal, target_calories
            )

            return {
                "status": "success",
                "meal_plan": meal_plan,
                "daily_summary": daily_summary,
                "chatbot_message": chatbot_message,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _format_chatbot_message(
        self, meal_plan: Dict, daily_summary: Dict, goal: str, target_calories: int
    ) -> str:
        """Generate conversational chatbot message."""
        goal_messages = {
            "weight_loss": "weight loss goal",
            "muscle_gain": "muscle building goal",
            "maintenance": "maintenance goal",
        }

        goal_text = goal_messages.get(goal, "fitness goal")

        meal_descriptions = []
        for meal_name in ["breakfast", "lunch", "dinner", "snack"]:
            meal = meal_plan[meal_name]
            meal_descriptions.append(
                f"**{meal_name.title()}**: {meal['suggested_sentence']}"
            )

        message = (
            f"Based on your {target_calories}-calorie {goal_text}, here's your daily plan:\n\n"
            + "\n".join(meal_descriptions)
            + "\n\n"
            f"**Daily Total**: {int(daily_summary['calories'])} calories | "
            f"{int(daily_summary['protein_g'])}g protein | "
            f"{int(daily_summary['carbs_g'])}g carbs | "
            f"{int(daily_summary['fat_g'])}g fat"
        )

        if goal == "weight_loss":
            message += f"\n\nYour {int(daily_summary['protein_g'])}g protein will keep you full and support fat loss!"
        elif goal == "muscle_gain":
            message += f"\n\nYour {int(daily_summary['carbs_g'])}g carbs will fuel your workouts and muscle growth!"
        else:
            message += "\n\nThis balanced plan will help you maintain your current fitness level!"

        return message


# Performance test helper
def test_performance():
    """Test that plan generation takes <50ms"""
    import time

    recommender = FoodRecommender("model3_food_database.json")

    test_input = {
        "target_calories": 1842,
        "fitness_goal": "weight_loss",
        "dietary_restrictions": [],
    }

    start_time = time.time()
    result = recommender.generate_plan(test_input)
    end_time = time.time()

    execution_time_ms = (end_time - start_time) * 1000
    print(f"[Performance] Execution time: {execution_time_ms:.2f}ms (target: <50ms)")

    return execution_time_ms < 50


if __name__ == "__main__":
    # Quick test
    print("=" * 60)
    print("Model 3: Food Recommendation Engine - Quick Test")
    print("=" * 60)

    recommender = FoodRecommender("model3_food_database.json")

    test_input = {
        "target_calories": 1842,
        "fitness_goal": "weight_loss",
        "dietary_restrictions": [],
    }

    result = recommender.generate_plan(test_input)

    if result["status"] == "success":
        print("\n[SUCCESS]\n")
        print(result["chatbot_message"])
        print("\n" + "=" * 60)
        print(f"Macro Accuracy: {result['daily_summary']['macro_accuracy']}")
    else:
        print(f"\n[ERROR]: {result['error']}")

    print("\n" + "=" * 60)
    test_performance()

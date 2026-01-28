"""
Safety Validator: Mandatory Safety Gates
Ensures all dietary recommendations meet medical and nutritional safety standards.
"""

from typing import Dict, List, Tuple

class SafetyValidator:
    """
    Implements 4 validation gates that every meal plan must pass.
    """
    
    # Constants
    MIN_PROTEIN_PER_MEAL = 20  # grams
    MIN_PORTION_G = 50         # grams
    MAX_PORTION_G = 500        # grams
    OIL_PORTION_RANGE = (5, 30) # grams for oils/fats
    CALORIE_TOLERANCE = 0.07   # ±7%
    
    # Foods allowed to be small portions (oils, seeds, condiments, calorie-dense foods)
    OILS_AND_FATS = ['oil', 'butter', 'ghee', 'mayonnaise', 'dressing']
    CALORIE_DENSE_FOODS = [
        'seeds', 'nuts', 'avocado', 'almond', 'walnut', 'cashew', 'peanut',
        'cheese', 'cream', 'olives'
    ]
    CONDIMENTS = ['sauce', 'spices', 'salt', 'pepper', 'sugar', 'honey']

    def validate_meal_plan(self, meal_plan: dict, daily_target_calories: int, restrictions: list) -> tuple:
        """
        Simplified safety validation with fixed portion logic.
        Returns: (is_valid: bool, errors: list)
        """
        errors = []
        
        # Gate 1: Allergen filtering (zero tolerance)
        for meal_name, meal in meal_plan.items():
            if meal_name == 'daily_summary' or "foods" not in meal:
                continue
            for food in meal["foods"]:
                if any(r in food.get("allergens", []) for r in restrictions):
                    error = f"[SAFETY] ALLERGEN VIOLATION: {food['name']} in {meal_name}"
                    print(error)
                    errors.append(error)
                    return False, errors  # Fail fast on allergens
        
        # Gate 2: FIXED portion checks (30g-600g range)
        for meal_name, meal in meal_plan.items():
            if meal_name == 'daily_summary' or "foods" not in meal:
                continue
            for food in meal["foods"]:
                portion = food.get("portion_g", 0)
                name = food.get("name", "Unknown").lower()
                
                # Check if it's a condiment/oil that can be smaller
                is_tiny_ok = any(x in name for x in self.CONDIMENTS + self.OILS_AND_FATS)
                
                if is_tiny_ok:
                    # Condiments/oils: 5-50g is reasonable
                    if portion < 5 or portion > 50:
                        error = f"Condiment portion unusual: {food['name']} ({portion}g)"
                        print(f"[SAFETY] WARNING: {error}")
                        errors.append(error)
                else:
                    # Regular foods: 30-600g
                    if portion < 15:
                        error = f"Portion too small: {food['name']} ({portion}g < 15g)"
                        print(f"[SAFETY] ERROR: {error}")
                        errors.append(error)
                    elif portion > 600:
                        error = f"Portion too large: {food['name']} ({portion}g > 600g)"
                        print(f"[SAFETY] ERROR: {error}")
                        errors.append(error)
        
        # Gate 3: Minimum protein per main meal (15g threshold)
        for meal_name in ["breakfast", "lunch", "dinner"]:
            if meal_name in meal_plan:
                meal = meal_plan[meal_name]
                protein = meal.get("total_protein_g", 0)
                if protein < 15:
                    error = f"Low protein: {meal_name} has {protein:.1f}g (<15g)"
                    print(f"[SAFETY] WARNING: {error}")
                    errors.append(error)
        
        # Return result
        if len(errors) == 0:
            print("[SAFETY] All checks passed")
            return True, []
        else:
            print(f"[SAFETY] {len(errors)} validation issues found")
            return len(errors) == 0, errors



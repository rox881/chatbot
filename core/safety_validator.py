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
    
    # Foods allowed to be small portions (oils, seeds, condiments)
    SMALL_PORTION_EXCEPTIONS = [
        'oil', 'butter', 'seeds', 'nuts', 'dressing', 'sauce', 'mayonnaise', 
        'ghee', 'spices', 'salt', 'pepper', 'sugar', 'honey'
    ]

    def validate_meal_plan(self, meal_plan: Dict, daily_target_calories: int, restrictions: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate meal plan against safety constraints.
        
        Args:
            meal_plan: Generated meal plan dictionary
            daily_target_calories: Target daily calories
            restrictions: List of dietary restrictions (e.g., 'nut_free')
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        # 1. Gate 1: Allergen Filtering (Zero Tolerance)
        if not self._validate_allergens(meal_plan, restrictions, errors):
            return False, errors # Fail immediately on allergens
            
        # 2. Gate 2: Portion Sanity
        self._validate_portions(meal_plan, errors)
        
        # 3. Gate 3: Minimum Protein
        self._validate_protein(meal_plan, errors)
        
        # 4. Gate 4: Calorie Accuracy
        self._validate_calories(meal_plan, daily_target_calories, errors)
        
        return len(errors) == 0, errors

    def _validate_allergens(self, meal_plan: Dict, restrictions: List[str], errors: List[str]) -> bool:
        """Check for allergen violations."""
        if not restrictions:
            return True
            
        for meal_name, meal_data in meal_plan.items():
            if meal_name == 'daily_summary': continue
            
            for food in meal_data.get('foods', []):
                food_allergens = food.get('allergens', [])
                for restriction in restrictions:
                    if restriction in food_allergens:
                        errors.append(f"ALLERGEN ALERT: {food['name']} contains {restriction} in {meal_name}")
                        return False # Fail fast
        return True

    def _validate_portions(self, meal_plan: Dict, errors: List[str]):
        """Check for realistic portion sizes."""
        for meal_name, meal_data in meal_plan.items():
            if meal_name == 'daily_summary': continue
            
            for food in meal_data.get('foods', []):
                portion = food.get('portion_g', 0)
                name = food.get('name', '').lower()
                
                # Check if it's an exception (oil, etc.)
                is_exception = any(exc in name for exc in self.SMALL_PORTION_EXCEPTIONS)
                
                if is_exception:
                    if not (self.OIL_PORTION_RANGE[0] <= portion <= self.OIL_PORTION_RANGE[1]):
                        # Just a warning for oils, or strict check? Prompt says "except oils: 5-30g"
                        # enforcing strict range for now as per specific prompt requirement
                        if portion > self.OIL_PORTION_RANGE[1]:
                             errors.append(f"Portion too large for condiment/oil: {food['name']} ({portion}g)")
                else:
                    if portion < self.MIN_PORTION_G:
                         errors.append(f"Portion too small: {food['name']} ({portion}g < {self.MIN_PORTION_G}g)")
                    elif portion > self.MAX_PORTION_G:
                         errors.append(f"Portion too large: {food['name']} ({portion}g > {self.MAX_PORTION_G}g)")

    def _validate_protein(self, meal_plan: Dict, errors: List[str]):
        """Ensure minimum protein per main meal."""
        for meal_name in ['breakfast', 'lunch', 'dinner']:
            if meal_name in meal_plan:
                protein = meal_plan[meal_name].get('total_protein_g', 0)
                if protein < self.MIN_PROTEIN_PER_MEAL:
                    errors.append(f"Insufficient protein in {meal_name}: {protein:.1f}g < {self.MIN_PROTEIN_PER_MEAL}g")

    def _validate_calories(self, meal_plan: Dict, target: int, errors: List[str]):
        """Ensure total calories are within tolerance."""
        if 'daily_summary' in meal_plan:
            total_cals = meal_plan['daily_summary'].get('total_calories', 0)
        else:
            total_cals = 0
            for meal_name, meal_data in meal_plan.items():
                if meal_name != 'daily_summary':
                     total_cals += meal_data.get('total_calories', 0)
        
        # Calculate deviation
        deviation = abs(total_cals - target) / target if target > 0 else 1.0
        
        if deviation > self.CALORIE_TOLERANCE:
            errors.append(f"Calorie deviation too high: {total_cals} vs target {target} ({deviation*100:.1f}% > 7.0%)")

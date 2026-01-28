"""
Natural Language Generator: Human-First Response Formatter
Transforms technical data into coach-like, empathetic, and scannable responses.
"""

from typing import Dict

class NLGenerator:
    """
    Generates human-friendly, formatted responses for the fitness chatbot.
    """

    def format_plan_response(self, profile: Dict, roadmap: Dict, meal_plan: Dict, week: int) -> str:
        """
        Create a rich, structured response for the generated plan.
        
        Args:
            profile: User profile dict (weight, height, goal, etc.)
            roadmap: Model 2 output (calories, exercise duration)
            meal_plan: Model 3 output (meals)
            week: Current week number
            
        Returns:
            Formatted string response
        """
        # Goal-specific emoji
        goal_emoji = {
            "weight_loss": "\ud83d\udd25",
            "muscle_gain": "\ud83d\udcaa",
            "maintenance": "\u2696\ufe0f"
        }
        emoji = goal_emoji.get(profile.get('fitness_goal'), "\u2728")
        
        goal_display = profile.get('fitness_goal', 'fitness').replace('_', ' ').title()
        weight = profile.get('weight_kg', '??')
        height = profile.get('height_cm', '??')
        
        # Calculate daily totals from meal plan
        daily_cals = 0
        daily_protein = 0
        
        for meal_name in ['breakfast', 'lunch', 'dinner', 'snack']:
            if meal_name in meal_plan:
                meal = meal_plan[meal_name]
                daily_cals += meal.get('total_calories', 0)
                daily_protein += meal.get('total_protein_g', 0)
        
        # Build response
        response = f"{emoji} **Week {week} {goal_display} Plan** (Based on YOUR {weight}kg/{height}cm profile)\n\n"
        
        # Format each meal
        meals_config = [
            ('breakfast', '\ud83c\udf73', 'Breakfast'),
            ('lunch', '\ud83e\udd57', 'Lunch'),
            ('dinner', '\ud83c\udf72', 'Dinner'),
            ('snack', '\ud83c\udf4e', 'Snack')
        ]
        
        for meal_key, emoji_meal, title in meals_config:
            if meal_key in meal_plan:
                meal = meal_plan[meal_key]
                response += f"{emoji_meal} **{title}**\n"
                response += self._format_meal(meal)
                response += "\n\n"
        
        # Daily summary
        target_cals = roadmap.get('target_calories', 0)
        exercise_mins = roadmap.get('target_exercise_minutes', 150)
        
        response += f"\ud83d\udcca **Daily Totals**\n"
        response += f"\u2022 Calories: {daily_cals:.0f} kcal | Protein: {daily_protein:.0f}g\n"
        response += f"\u2022 Exercise: {exercise_mins} mins/day\n\n"
        
        # Pro tip based on goal
        response += "\ud83d\udca1 **Pro Tip**: "
        if profile.get('fitness_goal') == 'weight_loss':
            response += "Drink water 30 mins before meals to feel fuller faster!\n\n"
        elif profile.get('fitness_goal') == 'muscle_gain':
            response += "Don't skip the post-workout meal to fuel muscle growth!\n\n"
        else:
            response += "Consistency is key \u2014 you're doing great!\n\n"
        
        response += "Want to adjust portions or see tomorrow's plan? \ud83d\ude0a"
        
        return response

    def _format_meal(self, meal: Dict) -> str:
        """Format individual meal details."""
        if not meal or "foods" not in meal:
            return "\u2022 *No recommendation*\n"
        
        lines = []
        # Show up to 3 foods, then summarize
        for food in meal["foods"][:3]:
            portion = food.get('portion_g', 0)
            name = food.get('name', 'Unknown')
            lines.append(f"\u2192 {portion:.0f}g {name}")
        
        if len(meal["foods"]) > 3:
            lines.append(f"\u2192 +{len(meal['foods'])-3} more items")
        
        # Meal totals
        meal_cals = meal.get('total_calories', 0)
        meal_protein = meal.get('total_protein_g', 0)
        lines.append(f"_Total: {meal_cals:.0f} kcal | {meal_protein:.0f}g protein_")
        
        return "\n".join(lines)

    def format_onboarding_error(self, error_type: str, context: str) -> str:
        """Format error messages naturally (fallback - specific errors now inline)."""
        if error_type == 'weight':
            return "I need a realistic weight (40-200 kg). What's your weight in kg? (e.g., '70')"
        elif error_type == 'height':
            return "I need a realistic height (100-250 cm). What's your height in cm? (e.g., '170')"
        elif error_type == 'age':
            return "I need a realistic age (13-100 years). How old are you?"
        return f"I didn't understand that. {context}"

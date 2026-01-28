"""
Natural Language Generator: Human-First Response Formatter
Transforms technical data into coach-like, empathetic, and scannable responses.
"""

from typing import Dict, List

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
        goal_display = profile['fitness_goal'].replace('_', ' ').title()
        weight = profile['weight_kg']
        height = profile['height_cm']
        
        # Header
        response = f"🔥 **Week {week} {goal_display} Plan** (Based on YOUR {weight}kg/{height}cm profile)\n\n"
        
        # Daily Targets
        target_cals = roadmap.get('target_calories', 0)
        protein_target = int(target_cals * 0.3 / 4) # Est protein target if not passed
        
        # Meals
        meals_order = ['breakfast', 'lunch', 'dinner', 'snack']
        emojis = {
            'breakfast': '🍳',
            'lunch': '🥗', 
            'dinner': '🍽️',
            'snack': '🍎'
        }
        
        for meal_type in meals_order:
            if meal_type in meal_plan:
                meal = meal_plan[meal_type]
                emoji = emojis.get(meal_type, '🥘')
                meal_title = f"{emoji} **{meal_type.title()}**"
                
                # Check for "Power Bowl" or similar naming opportunity (omitted for strict adherence to list first)
                
                response += f"{meal_title}\n"
                
                for food in meal.get('foods', []):
                    portion = food.get('portion_g', 0)
                    name = food.get('name', 'Unknown')
                    
                    # Add descriptive text for portion context if possible (simplified here)
                    desc = f"{portion}g"
                    if 'chicken' in name.lower() and 100 <= portion <= 150:
                        desc += " (palm-sized)"
                    elif 'pasta' in name.lower() or 'rice' in name.lower():
                        if 50 <= portion <= 70:
                             desc += " (approx ½ cup dry)"
                    
                    response += f"→ {desc} {name}\n"
                
                # Meal Summary
                m_cals = meal.get('total_calories', 0)
                m_pro = meal.get('total_protein_g', 0)
                response += f"_Total: {m_cals} kcal | {m_pro}g protein_\n\n"
        
        # Daily Summary
        day_summary = meal_plan.get('daily_summary', {})
        total_cals = day_summary.get('total_calories', 0)
        total_pro = day_summary.get('total_protein_g', 0)
        
        response += f"📊 **Daily Total**: {total_cals} kcal | {total_pro}g protein\n\n"
        
        # Pro Tip
        response += "💡 **Pro tip**: "
        if profile['fitness_goal'] == 'weight_loss':
            response += "Drink water before meals to feel fuller faster!\n\n"
        elif profile['fitness_goal'] == 'muscle_gain':
            response += "Don't skip the post-workout meal to fuel growth!\n\n"
        else:
            response += "Consistency is key — you're doing great!\n\n"
            
        response += "Shall I show you tomorrow's plan or adjust portions?"
        
        return response

    def format_onboarding_error(self, error_type: str, context: str) -> str:
        """Format error messages naturally."""
        if error_type == 'weight':
            return f"I need a realistic weight (40-200 kg). What's your weight in kg? (e.g., '70')"
        elif error_type == 'height':
            return f"I need a realistic height (100-250 cm). What's your height in cm? (e.g., '170')"
        elif error_type == 'age':
            return f"I need a realistic age (13-100 years). How old are you?"
        elif error_type == 'number':
             return f"I need a number for that. {context}"
        return f"I didn't understand that. {context}"

"""
Conversation Manager: State Machine for Progressive Onboarding
Handles natural conversation flow - collects user profile BEFORE generating plans.
"""

import json
import os
import re
import sys
from typing import Dict, Tuple, Optional, Any
from datetime import datetime, timedelta

# Add core and root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)
sys.path.insert(0, current_dir)

from core.safety_validator import SafetyValidator
from core.nl_generator import NLGenerator
from core.roadmap_generator import RoadmapGenerator
from core.food_recommender import FoodRecommender
# IntentClassifier is not strictly needed for this flow but good to have if we expand
from core.intent_classifier import IntentClassifier

class ConversationManager:
    """
    State machine managing conversation flow.
    """
    
    # Conversation states
    STATE_GREETING = "greeting"
    STATE_ONBOARDING_GOAL = "onboarding_goal"
    STATE_ONBOARDING_WEIGHT = "onboarding_weight"
    STATE_ONBOARDING_HEIGHT = "onboarding_height"
    STATE_ONBOARDING_AGE = "onboarding_age"
    STATE_ONBOARDING_GENDER = "onboarding_gender" # Added for model accuracy
    STATE_ONBOARDING_ACTIVITY = "onboarding_activity"
    STATE_READY_FOR_PLAN = "ready_for_plan"
    STATE_SHOWING_ROADMAP = "showing_roadmap"
    
    # Validation ranges
    MIN_WEIGHT = 40  # kg
    MAX_WEIGHT = 200
    MIN_HEIGHT = 100  # cm
    MAX_HEIGHT = 250
    MIN_AGE = 13
    MAX_AGE = 100
    
    # Activity levels
    ACTIVITY_LEVELS = {
        'sedentary': ['sedentary', 'sitting', 'desk', 'inactive', 'lazy'],
        'light': ['light', 'walking', 'casual'],
        'moderate': ['moderate', 'regular', 'normal', 'active'],
        'active': ['active', 'very active', 'exercise', 'gym', 'workout'],
        'very_active': ['very active', 'athlete', 'intense', 'training']
    }
    
    # Fitness goals
    GOALS = {
        'weight_loss': ['lose', 'loss', 'reduce', 'slim', 'cut', 'shed'],
        'muscle_gain': ['gain', 'build', 'bulk', 'muscle', 'grow', 'mass'],
        'maintenance': ['maintain', 'stay', 'keep', 'stable', 'preserve']
    }

    def __init__(self, storage_path: str = None):
        """
        Initialize conversation manager and models.
        """
        if storage_path:
            self.storage_path = storage_path
        else:
             self.storage_path = os.path.join(root_dir, 'data', 'user_profiles.json')
             
        self.conversations = self._load_conversations()
        
        # Initialize Helpers
        self.nl_generator = NLGenerator()
        self.safety_validator = SafetyValidator()
        
        # Initialize Models
        print("[ConversationManager] Loading models...")
        self.roadmap_generator = RoadmapGenerator(
             model_path=os.path.join(root_dir, 'RoadMap_model', 'roadmap_model.pkl')
        )
        self.food_recommender = FoodRecommender(
             database_path=os.path.join(root_dir, 'model_3_build', 'model3_food_database.json')
        )
        # Intent classifier optional for now as we drive with state machine
        
    def _load_conversations(self) -> Dict:
        """Load conversation states from disk."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_conversations(self):
        """Persist conversation states to disk."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.conversations, f, indent=2)
    
    def get_user_conversation(self, user_id: str) -> Dict:
        """Get or create user conversation state."""
        if user_id not in self.conversations:
            self.conversations[user_id] = {
                "current_state": self.STATE_GREETING,
                "profile": {
                    "weight_kg": None,
                    "height_cm": None,
                    "age": None,
                    "gender": "female", # Defaulting to female if not collected, helps Model 2
                    "activity_level": None,
                    "fitness_goal": None,
                    "current_week": 1,
                    "dietary_restrictions": []
                },
                "last_interaction": datetime.now().isoformat(),
                "message_count": 0
            }
            self._save_conversations()
        
        # Stale check
        last_time = datetime.fromisoformat(self.conversations[user_id]["last_interaction"])
        if datetime.now() - last_time > timedelta(days=7):
            self.conversations[user_id]["current_state"] = self.STATE_GREETING
        
        return self.conversations[user_id]
    
    def _extract_number(self, text: str) -> Optional[float]:
        """Extract numeric value - rejects word numbers like 'seventy'."""
        text = text.strip()
        # Remove units but keep the number
        text_clean = re.sub(r'(kg|kilogram|kilograms|cm|centimeter|centimeters|years?|old)', '', text, flags=re.IGNORECASE)
        # Find first number (int or decimal)
        match = re.search(r'(\d+\.?\d*)', text_clean)
        if match:
            return float(match.group(1))
        # Word numbers like "seventy" will return None -> triggers helpful error
        return None
        
    def adapt_model2_to_model3(self, model2_output: Dict, user_profile: Dict) -> Dict:
        """
        CRITICAL FIX: Adapt Model 2 output for Model 3.
        """
        return {
            "target_calories": model2_output.get("target_calories"),
            # Ensure fitness_goal is passed correctly
            "fitness_goal": user_profile["fitness_goal"],
            "dietary_restrictions": user_profile.get("dietary_restrictions", [])
        }

    def process_message(self, user_id: str, message: str) -> str:
        """Main handler for user messages."""
        conv = self.get_user_conversation(user_id)
        conv["last_interaction"] = datetime.now().isoformat()
        
        response = self._handle_state(conv, message)
        
        self._save_conversations()
        return response

    def _handle_state(self, conv: Dict, message: str) -> str:
        state = conv["current_state"]
        profile = conv["profile"]
        
        # State: Greeting
        if state == self.STATE_GREETING:
            conv["current_state"] = self.STATE_ONBOARDING_GOAL
            return "Hi! I'm your AI fitness coach. 😊 What's your goal today? (lose weight / gain muscle / maintain)"
            
        # State: Goal
        elif state == self.STATE_ONBOARDING_GOAL:
            goal = self._match_keyword(message, self.GOALS)
            if goal:
                profile["fitness_goal"] = goal
                conv["current_state"] = self.STATE_ONBOARDING_WEIGHT
                return "Great goal! 💪 What's your current weight in kg?"
            return "I didn't catch that. Please choose: lose weight, gain muscle, or maintain."

        # State: Weight
        elif state == self.STATE_ONBOARDING_WEIGHT:
            weight = self._extract_number(message)
            if weight and self.MIN_WEIGHT <= weight <= self.MAX_WEIGHT:
                profile["weight_kg"] = weight
                conv["current_state"] = self.STATE_ONBOARDING_HEIGHT
                return f"✅ {weight} kg logged. Height in cm?"
            elif weight is None:
                return "I need a number like '70' (not 'seventy'). What's your weight in kg?"
            else:
                return f"That weight seems unusual ({weight} kg). Please enter a realistic weight (40-200 kg)."

        # State: Height
        elif state == self.STATE_ONBOARDING_HEIGHT:
            height = self._extract_number(message)
            if height and self.MIN_HEIGHT <= height <= self.MAX_HEIGHT:
                profile["height_cm"] = height
                conv["current_state"] = self.STATE_ONBOARDING_AGE
                return f"{height} cm — perfect. How old are you?"
            elif height is None:
                return "I need a number like '170' (not 'one seventy'). What's your height in cm?"
            else:
                return f"That height seems unusual ({height} cm). Please enter a realistic height (100-250 cm)."

        # State: Age
        elif state == self.STATE_ONBOARDING_AGE:
            age = self._extract_number(message)
            if age and self.MIN_AGE <= age <= self.MAX_AGE:
                profile["age"] = int(age)
                # Ensure we have a gender field in profile, even if default
                conv["current_state"] = self.STATE_ONBOARDING_ACTIVITY
                return f"{int(age)} years young! 😊 Activity level? (sedentary/light/moderate/active)"
            elif age is None:
                return "I need a number like '25' (not 'twenty five'). How old are you?"
            else:
                return f"That age seems unusual ({age} years). Please enter a realistic age (13-100 years)."

        # State: Activity (Final Step)
        elif state == self.STATE_ONBOARDING_ACTIVITY:
            activity = self._match_keyword(message, self.ACTIVITY_LEVELS)
            if activity:
                profile["activity_level"] = activity
                conv["current_state"] = self.STATE_READY_FOR_PLAN
                # Trigger generation immediately
                return self._generate_plan(conv)
            return "Please choose: sedentary, light, moderate, or active."
            
        # State: Showing Roadmap (Maintenance mode)
        elif state == self.STATE_SHOWING_ROADMAP:
            # Simple handling for follow-ups or reset
            if any(w in message.lower() for w in ['reset', 'new', 'start over']):
                conv["current_state"] = self.STATE_ONBOARDING_GOAL
                return "Starting fresh! What's your new goal?"
            
            # Assuming user wants next week? Or just chat?
            # For now, simplistic re-generation or guidance
            return "I've designed this plan for you. Type 'reset' to start over or let me know if you need adjustments!"
            
        return "I'm not sure what you mean. Let's stick to the plan! 😊"

    def _match_keyword(self, text: str, mapping: Dict) -> Optional[str]:
        text = text.lower()
        for key, synonyms in mapping.items():
            if any(s in text for s in synonyms):
                return key
        return None

    def _generate_plan(self, conv: Dict) -> str:
        """Orchestrate the pipeline: Model 2 -> Adapter -> Model 3 -> Validator -> NLG."""
        profile = conv["profile"]
        
        # VALIDATION: Ensure complete profile before generation
        required_fields = ["weight_kg", "height_cm", "age", "activity_level", "fitness_goal"]
        missing = [f for f in required_fields if profile.get(f) is None]
        if missing:
            return f"⚠️ Let's complete your profile first! Missing: {', '.join(missing)}"
        
        try:
            # 1. Model 2: Roadmap
            # Ensure all fields are present. Gender is defaulted in get_user_conversation if missing.
            roadmap = self.roadmap_generator.predict(profile)
            
            # 2. Adapter
            model3_input = self.adapt_model2_to_model3(roadmap, profile)
            
            # 3. Model 3: Food
            # Use generate_plan wrapper which returns standardized dict
            meal_result = self.food_recommender.generate_plan(
                target_calories=model3_input['target_calories'],
                fitness_goal=model3_input['fitness_goal'],
                dietary_restrictions=model3_input['dietary_restrictions']
            )
            
            if meal_result['status'] != 'success':
                return f"⚠️ I had trouble generating a meal plan: {meal_result.get('error')}"
            
            meal_plan = meal_result['meal_plan']
            
            # 4. Safety Validation
            is_valid, errors = self.safety_validator.validate_meal_plan(
                meal_plan, 
                model3_input['target_calories'], 
                model3_input['dietary_restrictions']
            )
            
            if not is_valid:
                # In production, we might retry or adjust. For now, report safety issue.
                return f"⚠️ Safety Check Failed: {'; '.join(errors)}. Please adjust your profile."
            
            # 5. NLG
            current_week = profile.get('current_week', 1)
            response = self.nl_generator.format_plan_response(
                profile, roadmap, meal_plan, current_week
            )
            
            conv["current_state"] = self.STATE_SHOWING_ROADMAP
            return response

        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"⚠️ System Error: {str(e)}"

# Self-test if run directly
if __name__ == "__main__":
    cm = ConversationManager(os.path.join(root_dir, 'data', 'test_user_profiles.json'))
    uid = "test_user_123"
    print(cm.process_message(uid, "Hi"))
    print(cm.process_message(uid, "lose weight"))
    print(cm.process_message(uid, "70"))
    print(cm.process_message(uid, "170"))
    print(cm.process_message(uid, "25"))
    print(cm.process_message(uid, "moderate"))

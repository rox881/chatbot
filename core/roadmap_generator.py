"""
Roadmap Generator Wrapper: Model 2
Wraps the pre-trained Random Forest model for personalized roadmap generation.
"""

import pickle
import os
import numpy as np
from typing import Dict


class RoadmapGenerator:
    """
    Wrapper for Model 2: Roadmap Generation using Random Forest.
    Generates personalized fitness roadmaps based on user state.
    """
    
    # Expected features for the model (based on training data)
    FEATURE_COLUMNS = [
        'age', 'weight_kg', 'height_cm', 'bmi', 'gender_encoded', 
        'activity_level_encoded', 'week'
    ]
    
    # Activity level encoding (must match training)
    ACTIVITY_LEVELS = {
        'sedentary': 0,
        'light': 1,
        'moderate': 2,
        'active': 3,
        'very_active': 4
    }
    
    # Gender encoding (must match training)
    GENDER_ENCODING = {
        'male': 0,
        'female': 1,
        'other': 2
    }
    
    def __init__(self, model_path: str):
        """
        Initialize Roadmap Generator.
        
        Args:
            model_path: Path to trained Random Forest model (.pkl)
        """
        self.model_path = model_path
        self.model = self._load_model(model_path)
    
    def _load_model(self, path: str):
        """Load pickled model."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        with open(path, 'rb') as f:
            return pickle.load(f)
    
    def _calculate_bmi(self, weight_kg: float, height_cm: float) -> float:
        """Calculate BMI from weight and height."""
        height_m = height_cm / 100
        return weight_kg / (height_m ** 2)
    
    def _encode_features(self, user_state: Dict) -> np.ndarray:
        """
        Encode user state into feature vector for model.
        
        Args:
            user_state: Dictionary with user profile fields
        
        Returns:
            Numpy array of encoded features
        """
        # Calculate BMI
        bmi = self._calculate_bmi(user_state['weight_kg'], user_state['height_cm'])
        
        # Encode categorical variables
        gender_enc = self.GENDER_ENCODING.get(user_state.get('gender', 'other'), 2)
        activity_enc = self.ACTIVITY_LEVELS.get(user_state.get('activity_level', 'moderate'), 2)
        
        # Build feature vector (order must match FEATURE_COLUMNS)
        features = [
            user_state.get('age', 30),
            user_state['weight_kg'],
            user_state['height_cm'],
            bmi,
            gender_enc,
            activity_enc,
            user_state.get('week', 1)
        ]
        
        return np.array([features])
    
    def predict(self, user_state: Dict) -> Dict:
        """
        Generate personalized roadmap for user.
        
        Args:
            user_state: Dictionary with user profile
                Required: weight_kg, height_cm
                Optional: age, gender, activity_level, week
        
        Returns:
            Dictionary with:
                - target_weight_kg: Recommended weight for this week
                - target_calories: Daily calorie target
                - target_exercise_minutes: Daily exercise minutes
                - fitness_goal: Extracted from user state
                - dietary_restrictions: Extracted from user state
        """
        # Encode features
        features = self._encode_features(user_state)
        
        # Predict
        prediction = self.model.predict(features)[0]
        
        # Model outputs: [target_weight, target_calories, target_exercise_minutes]
        # (Assuming this is the output format - adjust based on actual model)
        
        if len(prediction) == 3:
            target_weight, target_calories, target_exercise = prediction
        elif hasattr(prediction, '__iter__') and len(prediction) >= 2:
            # Flexible handling for different output formats
            target_weight = prediction[0] if len(prediction) > 0 else user_state['weight_kg']
            target_calories = prediction[1] if len(prediction) > 1 else 2000
            target_exercise = prediction[2] if len(prediction) > 2 else 30
        else:
            # Single output - treat as calories
            target_weight = user_state['weight_kg'] * 0.99  # 1% reduction
            target_calories = float(prediction)
            target_exercise = 30
        
        return {
            "target_weight_kg": round(float(target_weight), 1),
            "target_calories": int(target_calories),
            "target_exercise_minutes": int(target_exercise),
            "fitness_goal": user_state.get('fitness_goal', 'weight_loss'),
            "dietary_restrictions": user_state.get('dietary_restrictions', [])
        }


# Standalone test
if __name__ == "__main__":
    print("=" * 60)
    print("Roadmap Generator (Model 2) - Test")
    print("=" * 60)
    
    model_path = "RoadMap_model/roadmap_model.pkl"
    
    try:
        generator = RoadmapGenerator(model_path)
        
        # Test user state
        test_user = {
            "age": 28,
            "gender": "male",
            "weight_kg": 82.0,
            "height_cm": 175.0,
            "activity_level": "moderate",
            "week": 1,
            "fitness_goal": "weight_loss",
            "dietary_restrictions": []
        }
        
        print("\n[Testing Roadmap Generation]\n")
        print(f"Input State:")
        print(f"  Age: {test_user['age']}")
        print(f"  Weight: {test_user['weight_kg']} kg")
        print(f"  Height: {test_user['height_cm']} cm")
        print(f"  Activity: {test_user['activity_level']}")
        print(f"  Week: {test_user['week']}")
        print(f"  Goal: {test_user['fitness_goal']}\n")
        
        roadmap = generator.predict(test_user)
        
        print(f"Generated Roadmap:")
        print(f"  Target Weight: {roadmap['target_weight_kg']} kg")
        print(f"  Target Calories: {roadmap['target_calories']} kcal/day")
        print(f"  Target Exercise: {roadmap['target_exercise_minutes']} min/day")
        
        # Test week progression
        print("\n[Testing Week Progression]\n")
        for week in [1, 2, 3, 4]:
            test_user['week'] = week
            roadmap = generator.predict(test_user)
            print(f"Week {week}: {roadmap['target_calories']} cal, {roadmap['target_weight_kg']} kg")
        
        print("\n" + "=" * 60)
        print("Model 2 loaded successfully! ✓")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print("Make sure you're running from the chatbot root directory.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

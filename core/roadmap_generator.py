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
        "age",
        "weight_kg",
        "height_cm",
        "bmi",
        "gender_encoded",
        "activity_level_encoded",
        "week",
    ]

    # Activity level encoding (must match training)
    ACTIVITY_LEVELS = {
        "sedentary": 0,
        "light": 1,
        "moderate": 2,
        "active": 3,
        "very_active": 4,
    }

    # Gender encoding (must match training)
    GENDER_ENCODING = {"male": 0, "female": 1, "other": 2}

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

        with open(path, "rb") as f:
            loaded = pickle.load(f)

        # Handle different model formats
        if isinstance(loaded, dict):
            # Model is a dictionary with 'models' key
            self.model_dict = loaded
            # Extract the models for predictions
            if "models" in loaded:
                # Assume models is a dict with keys like 'calories', 'weight', 'exercise'
                return loaded["models"]
            else:
                return loaded
        else:
            # Model is a single sklearn model
            self.model_dict = None
            return loaded

    def _calculate_bmi(self, weight_kg: float, height_cm: float) -> float:
        """Calculate BMI from weight and height."""
        height_m = height_cm / 100
        return weight_kg / (height_m**2)

    def _encode_features(self, user_state: Dict) -> np.ndarray:
        """
        Encode user state into feature vector for model.

        Model expects 14 features:
        ['age', 'weight_kg', 'height_cm', 'calorie_intake', 'weekly_exercise_minutes',
         'week', 'gender_male', 'activity_sedentary', 'activity_light',
         'activity_moderate', 'activity_active', 'goal_weight_loss',
         'goal_muscle_gain', 'goal_maintenance']

        Args:
            user_state: Dictionary with user profile fields

        Returns:
            Numpy array of encoded features (1, 14)
        """
        # Base features
        age = user_state.get("age", 30)
        weight_kg = user_state["weight_kg"]
        height_cm = user_state["height_cm"]

        # Estimate initial calorie intake (approximate based on weight and activity)
        calorie_intake = int(weight_kg * 24 * 1.2)  # BMR approximation

        # Estimate initial weekly exercise (based on activity level)
        activity_level = user_state.get("activity_level", "moderate")
        exercise_map = {
            "sedentary": 30,
            "light": 120,
            "moderate": 180,
            "active": 300,
            "very_active": 420,
        }
        weekly_exercise_minutes = exercise_map.get(activity_level, 180)

        week = user_state.get("week", 1)

        # One-hot encode gender (only 'male' is one-hot, others are 0)
        gender = user_state.get("gender", "other")
        gender_male = 1 if gender == "male" else 0

        # One-hot encode activity level
        activity_sedentary = 1 if activity_level == "sedentary" else 0
        activity_light = 1 if activity_level == "light" else 0
        activity_moderate = 1 if activity_level == "moderate" else 0
        activity_active = (
            1 if activity_level == "active" or activity_level == "very_active" else 0
        )

        # One-hot encode fitness goal
        fitness_goal = user_state.get("fitness_goal", "maintenance")
        goal_weight_loss = 1 if fitness_goal == "weight_loss" else 0
        goal_muscle_gain = 1 if fitness_goal == "muscle_gain" else 0
        goal_maintenance = 1 if fitness_goal == "maintenance" else 0

        # Build feature vector in exact order expected by model
        features = [
            age,
            weight_kg,
            height_cm,
            calorie_intake,
            weekly_exercise_minutes,
            week,
            gender_male,
            activity_sedentary,
            activity_light,
            activity_moderate,
            activity_active,
            goal_weight_loss,
            goal_muscle_gain,
            goal_maintenance,
        ]

        return np.array([features])

    def predict(self, user_state: Dict) -> Dict:
        """
        Generate personalized roadmap with safety constraints.
        """
        # Encode features (14 features including goal encoding)
        features = self._encode_features(user_state)

        # Get raw predictions from model
        if isinstance(self.model, dict):
            target_weight = self.model["weight_kg"].predict(features)[0]
            target_calories = self.model["calories"].predict(features)[0]
            target_exercise = self.model["exercise_minutes"].predict(features)[0]
        else:
            prediction = self.model.predict(features)[0]
            if hasattr(prediction, "__len__") and len(prediction) == 3:
                target_weight, target_calories, target_exercise = prediction
            elif hasattr(prediction, "__len__") and len(prediction) >= 2:
                target_weight = (
                    prediction[0] if len(prediction) > 0 else user_state["weight_kg"]
                )
                target_calories = prediction[1] if len(prediction) > 1 else 2000
                target_exercise = prediction[2] if len(prediction) > 2 else 30
            else:
                target_weight = user_state["weight_kg"] * 0.99
                target_calories = float(prediction)
                target_exercise = 30

        # 🔴 CRITICAL SAFETY FIX: Defensive validation for extreme outliers
        # Handles NaN, negative, zero, or unrealistically low values BEFORE safety patch
        if not np.isfinite(target_calories) or target_calories <= 0:
            # Invalid prediction → use conservative baseline
            original_cal = target_calories
            target_calories = 2000
            print(
                f"[SAFETY] WARNING: Invalid calorie prediction (got {original_cal}). Using fallback 2000 kcal."
            )
        elif target_calories < 1000:
            # Extreme outlier → enforce absolute minimum BEFORE goal-specific patch
            original_cal = target_calories
            target_calories = 1500
            print(
                f"[SAFETY] WARNING: Extreme outlier detected ({original_cal} kcal). Enforcing 1500 kcal floor."
            )

        # 🔴 CRITICAL SAFETY FIX: ROBUST GOAL DETECTION (handles spaces/underscores/variations)
        goal_raw = user_state.get("fitness_goal", "weight_loss")
        gender = user_state.get("gender", "female")
        goal_lower = str(goal_raw).lower()

        # Muscle gain detection (catches 'muscle_gain', 'gain muscle', 'muscle gain', etc.)
        is_muscle_gain = (
            any(term in goal_lower for term in ["muscle", "gain"])
            and "loss" not in goal_lower
            and "cut" not in goal_lower
        )

        # Weight loss detection
        is_weight_loss = any(
            term in goal_lower for term in ["loss", "lose", "cut", "shed"]
        )

        # Apply safety constraints (goal-specific floors)
        if is_muscle_gain:
            min_cal = 2700 if gender == "male" else 2400
            if target_calories < min_cal:
                target_calories = min_cal
        elif is_weight_loss:
            min_cal = 1500 if gender == "male" else 1200
            if target_calories < min_cal:
                target_calories = min_cal

        return {
            "target_weight_kg": round(float(target_weight), 1),
            "target_calories": int(target_calories),
            "target_exercise_minutes": int(target_exercise),
            "fitness_goal": goal_raw,  # Preserve original value
            "dietary_restrictions": user_state.get("dietary_restrictions", []),
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
            "dietary_restrictions": [],
        }

        print("\n[Testing Roadmap Generation]\n")
        print("Input State:")
        print(f"  Age: {test_user['age']}")
        print(f"  Weight: {test_user['weight_kg']} kg")
        print(f"  Height: {test_user['height_cm']} cm")
        print(f"  Activity: {test_user['activity_level']}")
        print(f"  Week: {test_user['week']}")
        print(f"  Goal: {test_user['fitness_goal']}\n")

        roadmap = generator.predict(test_user)

        print("Generated Roadmap:")
        print(f"  Target Weight: {roadmap['target_weight_kg']} kg")
        print(f"  Target Calories: {roadmap['target_calories']} kcal/day")
        print(f"  Target Exercise: {roadmap['target_exercise_minutes']} min/day")

        # Test extreme outlier that previously failed (168kg/242cm muscle gain)
        print("\n[Testing Extreme Outlier - 168kg/242cm Muscle Gain]\n")
        outlier_user = {
            "age": 30,
            "gender": "male",
            "weight_kg": 168.0,
            "height_cm": 242.0,
            "activity_level": "moderate",
            "week": 1,
            "fitness_goal": "muscle_gain",
            "dietary_restrictions": [],
        }
        roadmap = generator.predict(outlier_user)
        print(f"  Target Calories: {roadmap['target_calories']} kcal/day")
        print(f"  Expected: >=2500 kcal (male muscle gain floor)")
        if roadmap["target_calories"] >= 2500:
            print("  ✅ PASS: Safety floor enforced correctly")
        else:
            print("  ❌ FAIL: Safety floor NOT enforced")

        # Test week progression
        print("\n[Testing Week Progression]\n")
        for week in [1, 2, 3, 4]:
            test_user["week"] = week
            roadmap = generator.predict(test_user)
            print(
                f"Week {week}: {roadmap['target_calories']} cal, {roadmap['target_weight_kg']} kg"
            )

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

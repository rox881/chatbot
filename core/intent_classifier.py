"""
Intent Classifier Wrapper: Model 1
Wraps the pre-trained TF-IDF + Classifier model for intent classification.
"""

import pickle
import os
from typing import Optional


class IntentClassifier:
    """
    Wrapper for Model 1: Intent Classification using TF-IDF + trained classifier.
    Classifies user messages into predefined intents.
    """
    
    def __init__(self, model_path: str, vectorizer_path: Optional[str] = None):
        """
        Initialize Intent Classifier.
        
        Args:
            model_path: Path to trained classifier model (.pkl)
            vectorizer_path: Path to TF-IDF vectorizer (.pkl). If None, assumes same directory.
        """
        self.model_path = model_path
        
        # Auto-detect vectorizer path if not provided
        if vectorizer_path is None:
            model_dir = os.path.dirname(model_path)
            vectorizer_path = os.path.join(model_dir, "tfidf_vectorizer.pkl")
        
        self.vectorizer_path = vectorizer_path
        
        # Load models
        self.model = self._load_model(model_path)
        self.vectorizer = self._load_model(vectorizer_path)
    
    def _load_model(self, path: str):
        """Load pickled model."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        with open(path, 'rb') as f:
            return pickle.load(f)
    
    def predict(self, user_message: str) -> str:
        """
        Classify user message into intent.
        
        Args:
            user_message: Raw user text input
        
        Returns:
            Predicted intent (e.g., 'weight_loss_plan', 'diet_suggestion')
        """
        # Vectorize input
        features = self.vectorizer.transform([user_message])
        
        # Predict intent
        intent = self.model.predict(features)[0]
        
        return intent
    
    def predict_with_confidence(self, user_message: str) -> tuple:
        """
        Classify with confidence scores (if model supports predict_proba).
        
        Args:
            user_message: Raw user text input
        
        Returns:
            Tuple of (intent, confidence_score)
        """
        features = self.vectorizer.transform([user_message])
        
        # Check if model supports probability prediction
        if hasattr(self.model, 'predict_proba'):
            probs = self.model.predict_proba(features)[0]
            intent = self.model.classes_[probs.argmax()]
            confidence = probs.max()
            return intent, confidence
        else:
            # Fallback to regular prediction
            intent = self.model.predict(features)[0]
            return intent, 1.0


# Standalone test
if __name__ == "__main__":
    print("=" * 60)
    print("Intent Classifier (Model 1) - Test")
    print("=" * 60)
    
    # Paths relative to chatbot root
    model_path = "intent_model/intent_model.pkl"
    
    try:
        classifier = IntentClassifier(model_path)
        
        # Test cases
        test_messages = [
            "I want to lose weight",
            "Give me a diet plan",
            "What should I eat for muscle gain?",
            "Show me my progress",
            "I need a maintenance plan"
        ]
        
        print("\n[Testing Intent Classification]\n")
        for msg in test_messages:
            intent = classifier.predict(msg)
            print(f"Message: \"{msg}\"")
            print(f"Intent:  {intent}")
            
            # Try confidence scoring
            if hasattr(classifier.model, 'predict_proba'):
                intent_conf, confidence = classifier.predict_with_confidence(msg)
                print(f"Confidence: {confidence:.2%}\n")
            else:
                print()
        
        print("=" * 60)
        print("Model 1 loaded successfully! ✓")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print("Make sure you're running from the chatbot root directory.")
    except Exception as e:
        print(f"\n[ERROR] {e}")

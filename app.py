"""
Flask API: Production Chatbot Endpoint
Provides REST API for frontend integration.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from pipeline import FitnessChatbotPipeline

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize pipeline (singleton)
pipeline = None


def get_pipeline():
    """Lazy-load pipeline on first request."""
    global pipeline
    if pipeline is None:
        print("[API] Initializing pipeline...")
        pipeline = FitnessChatbotPipeline()
    return pipeline


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "fitness-chatbot-api",
        "version": "1.0.0"
    }), 200


@app.route('/chat', methods=['POST'])
def chat():
    """
    Main chatbot endpoint.
    
    Request Body:
    {
        "message": str,  # User message
        "user_id": str   # Unique user ID
    }
    
    Response:
    {
        "status": "success" | "error",
        "response": str,  # Natural language response
        "intent": str,
        "roadmap": {...},
        "meal_plan": {...},
        "daily_summary": {...},
        "error": str  # Only if status == "error"
    }
    """
    try:
        # Validate request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "error": "Invalid JSON body"
            }), 400
        
        user_message = data.get('message')
        user_id = data.get('user_id')
        
        if not user_message:
            return jsonify({
                "status": "error",
                "error": "Missing 'message' field"
            }), 400
        
        if not user_id:
            return jsonify({
                "status": "error",
                "error": "Missing 'user_id' field"
            }), 400
        
        # Process through pipeline
        pipe = get_pipeline()
        result = pipe.process_message(user_message, user_id)
        
        # Return result with appropriate status code
        if result['status'] == 'success':
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route('/user/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    """
    Get user profile.
    
    Returns:
        User profile dictionary
    """
    try:
        pipe = get_pipeline()
        user_state = pipe.state_manager.get_user_state(user_id)
        
        return jsonify({
            "status": "success",
            "user": user_state
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route('/user/<user_id>', methods=['PUT'])
def update_user_profile(user_id):
    """
    Update user profile.
    
    Request Body:
    {
        "weight_kg": float,
        "height_cm": float,
        "age": int,
        "gender": str,
        "activity_level": str,
        "dietary_restrictions": list
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "error": "Invalid JSON body"
            }), 400
        
        pipe = get_pipeline()
        updated = pipe.state_manager.update_user_profile(user_id, data)
        
        return jsonify({
            "status": "success",
            "user": updated
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route('/user/<user_id>/reset', methods=['POST'])
def reset_user_week(user_id):
    """Reset user's week counter to 1."""
    try:
        pipe = get_pipeline()
        updated = pipe.state_manager.reset_user_week(user_id)
        
        return jsonify({
            "status": "success",
            "message": "Week counter reset to 1",
            "user": updated
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Starting Fitness Chatbot API")
    print("=" * 70)
    print("\nEndpoints:")
    print("  POST   /chat              - Main chatbot endpoint")
    print("  GET    /user/<id>         - Get user profile")
    print("  PUT    /user/<id>         - Update user profile")
    print("  POST   /user/<id>/reset   - Reset week counter")
    print("  GET    /health            - Health check")
    print("\n" + "=" * 70)
    
    # Run Flask server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

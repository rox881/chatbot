"""
Flask API: Conversational Fitness Agent Endpoint
Production-ready endpoint using state-machine architecture.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from core.conversation_manager import ConversationManager

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Conversation Manager (Singleton)
# Persist data in data/user_profiles.json
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
conversation_manager = ConversationManager(os.path.join(DATA_DIR, 'user_profiles.json'))

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "conversational-fitness-agent",
        "version": "2.0.0"
    }), 200

@app.route('/chat', methods=['POST'])
def chat():
    """
    State-aware chat endpoint.
    Example Body: {"message": "70", "user_id": "user_123"}
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
            
        message = data.get('message')
        user_id = data.get('user_id')
        
        if not message or not user_id:
            return jsonify({"error": "Missing message or user_id"}), 400
            
        # Process message through state machine
        response_text = conversation_manager.process_message(user_id, message)
        
        # Get current state for debugging/frontend context
        user_state = conversation_manager.get_user_conversation(user_id)
        
        return jsonify({
            "status": "success",
            "response": response_text,
            "state": user_state["current_state"],
            "week": user_state["profile"].get("current_week", 1)
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    """Reset user state."""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        if not user_id: return jsonify({"error": "Missing user_id"}), 400
        
        # Manually reset
        if user_id in conversation_manager.conversations:
            conversation_manager.conversations[user_id]["current_state"] = conversation_manager.STATE_GREETING
            conversation_manager.conversations[user_id]["profile"] = {
                "weight_kg": None, "height_cm": None, "age": None, "gender": "female",
                "activity_level": None, "fitness_goal": None, "current_week": 1,
                "dietary_restrictions": []
            }
            conversation_manager._save_conversations()
            
        return jsonify({"status": "success", "message": "Conversation reset"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 70)
    print("Conversational Agent API Starting [START]")
    print("=" * 70)
    app.run(host='0.0.0.0', port=5000, debug=True)

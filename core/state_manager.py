"""
State Manager: Persistent User Profile Management
Handles user state tracking, week progression, and cold-start scenarios.
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional
from threading import Lock


class StateManager:
    """
    Manages persistent user state with week tracking for Model 2.
    Thread-safe JSON-based storage with cold-start handling.
    """
    
    # Default profile for new users (cold-start)
    DEFAULT_PROFILE = {
        "age": 30,
        "gender": "other",
        "weight_kg": 70.0,
        "height_cm": 170.0,
        "activity_level": "moderate",
        "week": 1,
        "fitness_goal": "maintenance",
        "dietary_restrictions": []
    }
    
    def __init__(self, storage_path: str):
        """
        Initialize State Manager.
        
        Args:
            storage_path: Path to JSON file for persistent storage
        """
        self.storage_path = storage_path
        self.lock = Lock()  # Thread-safe file access
        
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        # Initialize storage file if it doesn't exist
        if not os.path.exists(self.storage_path):
            self._write_storage({})
    
    def _read_storage(self) -> Dict:
        """Thread-safe read from JSON storage."""
        with self.lock:
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                # Corrupted or missing file - reinitialize
                return {}
    
    def _write_storage(self, data: Dict) -> None:
        """Thread-safe atomic write to JSON storage."""
        with self.lock:
            # Atomic write: write to temp file, then rename
            temp_path = self.storage_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename (overwrites existing file)
            os.replace(temp_path, self.storage_path)
    
    def get_user_state(self, user_id: str, intent: Optional[str] = None) -> Dict:
        """
        Get user state, creating default profile if new user (cold-start).
        
        Args:
            user_id: Unique user identifier
            intent: Optional intent to extract fitness goal
        
        Returns:
            User state dictionary with all required fields
        """
        storage = self._read_storage()
        
        if user_id in storage:
            # Existing user
            return storage[user_id].copy()
        else:
            # New user - cold-start handling
            profile = self.DEFAULT_PROFILE.copy()
            profile['user_id'] = user_id
            profile['created_at'] = datetime.now().isoformat()
            profile['last_updated'] = datetime.now().isoformat()
            
            # Extract fitness goal from intent if available
            if intent:
                if 'weight_loss' in intent.lower():
                    profile['fitness_goal'] = 'weight_loss'
                elif 'muscle_gain' in intent.lower() or 'muscle' in intent.lower():
                    profile['fitness_goal'] = 'muscle_gain'
                elif 'maintenance' in intent.lower():
                    profile['fitness_goal'] = 'maintenance'
            
            # Save new profile
            storage[user_id] = profile
            self._write_storage(storage)
            
            return profile.copy()
    
    def update_user_profile(self, user_id: str, updates: Dict) -> Dict:
        """
        Update user profile with new information.
        
        Args:
            user_id: Unique user identifier
            updates: Dictionary of fields to update
        
        Returns:
            Updated user profile
        """
        storage = self._read_storage()
        
        if user_id not in storage:
            # Create new profile if doesn't exist
            storage[user_id] = self.DEFAULT_PROFILE.copy()
            storage[user_id]['user_id'] = user_id
            storage[user_id]['created_at'] = datetime.now().isoformat()
        
        # Update fields
        storage[user_id].update(updates)
        storage[user_id]['last_updated'] = datetime.now().isoformat()
        
        self._write_storage(storage)
        return storage[user_id].copy()
    
    def update_user_progress(self, user_id: str, roadmap: Dict) -> Dict:
        """
        Update user progress after generating roadmap.
        Increments week counter for Model 2's sequential predictions.
        
        Args:
            user_id: Unique user identifier
            roadmap: Roadmap output from Model 2
        
        Returns:
            Updated user profile
        """
        storage = self._read_storage()
        
        if user_id not in storage:
            # Should not happen, but handle gracefully
            storage[user_id] = self.DEFAULT_PROFILE.copy()
            storage[user_id]['user_id'] = user_id
            storage[user_id]['created_at'] = datetime.now().isoformat()
        
        # Increment week counter (critical for Model 2)
        current_week = storage[user_id].get('week', 1)
        storage[user_id]['week'] = current_week + 1
        
        # Update weight if provided in roadmap
        if 'target_weight_kg' in roadmap:
            storage[user_id]['weight_kg'] = roadmap['target_weight_kg']
        
        storage[user_id]['last_updated'] = datetime.now().isoformat()
        
        self._write_storage(storage)
        return storage[user_id].copy()
    
    def set_user_restrictions(self, user_id: str, restrictions: list) -> Dict:
        """
        Set dietary restrictions for user.
        
        Args:
            user_id: Unique user identifier
            restrictions: List of dietary restrictions
        
        Returns:
            Updated user profile
        """
        return self.update_user_profile(user_id, {'dietary_restrictions': restrictions})
    
    def reset_user_week(self, user_id: str) -> Dict:
        """
        Reset user's week counter to 1.
        
        Args:
            user_id: Unique user identifier
        
        Returns:
            Updated user profile
        """
        return self.update_user_profile(user_id, {'week': 1})
    
    def get_all_users(self) -> Dict:
        """
        Get all user profiles (for admin/debugging).
        
        Returns:
            Dictionary of all user profiles
        """
        return self._read_storage()
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user profile.
        
        Args:
            user_id: Unique user identifier
        
        Returns:
            True if deleted, False if user didn't exist
        """
        storage = self._read_storage()
        
        if user_id in storage:
            del storage[user_id]
            self._write_storage(storage)
            return True
        
        return False


# Standalone test
if __name__ == "__main__":
    print("=" * 60)
    print("State Manager - Test Suite")
    print("=" * 60)
    
    # Test with temporary file
    test_storage = "data/test_user_profiles.json"
    manager = StateManager(test_storage)
    
    # Test 1: Cold-start (new user)
    print("\n[Test 1] Cold-start for new user")
    state1 = manager.get_user_state("user_001", intent="weight_loss_plan")
    print(f"✓ Created profile for user_001")
    print(f"  Week: {state1['week']}, Goal: {state1['fitness_goal']}")
    
    # Test 2: Retrieve existing user
    print("\n[Test 2] Retrieve existing user")
    state2 = manager.get_user_state("user_001")
    print(f"✓ Retrieved existing profile")
    print(f"  Week: {state2['week']}")
    
    # Test 3: Update progress (week increment)
    print("\n[Test 3] Update progress - week increment")
    roadmap = {"target_weight_kg": 68.5, "target_calories": 1800}
    updated = manager.update_user_progress("user_001", roadmap)
    print(f"✓ Progress updated")
    print(f"  Week: {updated['week']} (should be 2)")
    print(f"  Weight: {updated['weight_kg']} kg")
    
    # Test 4: Set dietary restrictions
    print("\n[Test 4] Set dietary restrictions")
    restricted = manager.set_user_restrictions("user_001", ["vegetarian", "no_nuts"])
    print(f"✓ Restrictions set: {restricted['dietary_restrictions']}")
    
    # Test 5: Multiple users
    print("\n[Test 5] Multiple users")
    state3 = manager.get_user_state("user_002", intent="muscle_gain_plan")
    all_users = manager.get_all_users()
    print(f"✓ Total users: {len(all_users)}")
    
    # Cleanup
    if os.path.exists(test_storage):
        os.remove(test_storage)
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)

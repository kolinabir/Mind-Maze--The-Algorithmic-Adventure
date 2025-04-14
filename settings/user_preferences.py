import json
import os

class UserPreferences:
    def __init__(self):
        # Default settings
        self.settings = {
            "sound_enabled": True,
            "music_volume": 0.7,
            "sfx_volume": 0.8,
            "difficulty": "medium",
            "controls": {
                "up": "UP",
                "down": "DOWN",
                "left": "LEFT",
                "right": "RIGHT",
                "action": "SPACE",
                "back": "ESCAPE"
            },
            "accessibility": {
                "high_contrast": False,
                "text_size": "medium",
                "color_blind_mode": False
            },
            "unlocked_levels": [0],  # Only first level unlocked by default
            "completed_levels": []
        }
        
        # Path to save preferences
        self.save_path = os.path.join("data", "preferences.json")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        
        # Load existing preferences if available
        self.load_preferences()
    
    def load_preferences(self):
        """Load user preferences from file"""
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, 'r') as file:
                    loaded_settings = json.load(file)
                    
                    # Update settings with loaded values, preserving defaults for missing keys
                    for key, value in loaded_settings.items():
                        if key in self.settings:
                            if isinstance(value, dict) and isinstance(self.settings[key], dict):
                                # For nested dictionaries, update individual keys
                                for subkey, subvalue in value.items():
                                    if subkey in self.settings[key]:
                                        self.settings[key][subkey] = subvalue
                            else:
                                self.settings[key] = value
                                
                print("User preferences loaded successfully")
        except Exception as e:
            print(f"Error loading preferences: {e}")
    
    def save_preferences(self):
        """Save user preferences to file"""
        try:
            with open(self.save_path, 'w') as file:
                json.dump(self.settings, file, indent=4)
            print("User preferences saved successfully")
            return True
        except Exception as e:
            print(f"Error saving preferences: {e}")
            return False
    
    def get_setting(self, key, subkey=None):
        """Get a setting value"""
        if subkey is not None and key in self.settings and isinstance(self.settings[key], dict):
            return self.settings[key].get(subkey)
        return self.settings.get(key)
    
    def set_setting(self, key, value, subkey=None):
        """Set a setting value"""
        if subkey is not None:
            if key not in self.settings:
                self.settings[key] = {}
            self.settings[key][subkey] = value
        else:
            self.settings[key] = value
    
    def is_level_unlocked(self, level_index):
        """Check if a level is unlocked"""
        return level_index in self.settings["unlocked_levels"]
    
    def unlock_level(self, level_index):
        """Unlock a level"""
        if level_index not in self.settings["unlocked_levels"]:
            self.settings["unlocked_levels"].append(level_index)
            self.settings["unlocked_levels"].sort()
            self.save_preferences()
    
    def set_level_completed(self, level_index):
        """Mark a level as completed"""
        if level_index not in self.settings["completed_levels"]:
            self.settings["completed_levels"].append(level_index)
            self.settings["completed_levels"].sort()
            
            # Unlock the next level if it exists (assuming sequential unlocking)
            if level_index + 1 not in self.settings["unlocked_levels"]:
                self.unlock_level(level_index + 1)
            
            self.save_preferences()

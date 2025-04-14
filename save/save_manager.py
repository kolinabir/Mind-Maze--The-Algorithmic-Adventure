import os
import json
import datetime
from settings import DATA_DIR


class SaveManager:
    """
    Manages saving and loading game progress and settings
    """

    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.save_dir = os.path.join(DATA_DIR, "saves")
        self.current_profile = "default"

        # Create save directory if it doesn't exist
        os.makedirs(self.save_dir, exist_ok=True)

        # Default save data structure
        self.default_save_data = {
            "profile_name": "Default Profile",
            "created_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_played": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_play_time": 0,  # In seconds
            "session_start": datetime.datetime.now().timestamp(),
            "completed_levels": [],
            "unlocked_levels": [0],  # Start with first level unlocked
            "high_scores": {},
            "settings": {
                "sound_volume": 0.7,
                "music_volume": 0.5,
                "fullscreen": False,
                "show_hints": True,
                "difficulty": "normal",
            },
            "achievements": {},
            "tutorial_completed": False,
            "current_level": None,
        }

        self.save_data = self.default_save_data.copy()

    def create_new_profile(self, profile_name):
        """Create a new save profile"""
        profile_id = self._generate_profile_id(profile_name)

        # Create new save data
        new_save_data = self.default_save_data.copy()
        new_save_data["profile_name"] = profile_name
        new_save_data["created_date"] = datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        new_save_data["session_start"] = datetime.datetime.now().timestamp()

        # Save to file
        self._save_to_file(profile_id, new_save_data)

        # Set as current profile
        self.current_profile = profile_id
        self.save_data = new_save_data

        return profile_id

    def load_profile(self, profile_id):
        """Load a save profile"""
        save_file = os.path.join(self.save_dir, f"{profile_id}.json")

        if os.path.exists(save_file):
            try:
                with open(save_file, "r") as f:
                    self.save_data = json.load(f)

                self.current_profile = profile_id

                # Update session start time
                self.save_data["session_start"] = datetime.datetime.now().timestamp()
                self.save_data["last_played"] = datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                # Apply settings from save data
                self._apply_settings()

                return True
            except Exception as e:
                print(f"Error loading save file: {e}")
                return False
        else:
            print(f"Save file not found: {save_file}")
            return False

    def save_game(self):
        """Save current game state"""
        if not self.current_profile:
            # Create default profile if none exists
            self.current_profile = self._generate_profile_id("Default Profile")

        # Update play time
        current_time = datetime.datetime.now().timestamp()
        session_time = current_time - self.save_data["session_start"]
        self.save_data["total_play_time"] += session_time
        self.save_data["session_start"] = current_time
        self.save_data["last_played"] = datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Save current game state
        self._update_game_state()

        # Save to file
        return self._save_to_file(self.current_profile, self.save_data)

    def get_all_profiles(self):
        """Get list of all save profiles"""
        profiles = []

        for filename in os.listdir(self.save_dir):
            if filename.endswith(".json"):
                profile_id = filename[:-5]  # Remove .json extension

                try:
                    with open(os.path.join(self.save_dir, filename), "r") as f:
                        save_data = json.load(f)

                        profiles.append(
                            {
                                "id": profile_id,
                                "name": save_data.get("profile_name", "Unknown"),
                                "last_played": save_data.get("last_played", "Never"),
                                "completed_levels": len(
                                    save_data.get("completed_levels", [])
                                ),
                                "play_time": save_data.get("total_play_time", 0),
                            }
                        )
                except Exception as e:
                    print(f"Error reading save file {filename}: {e}")

        # Sort by last played date (most recent first)
        profiles.sort(key=lambda x: x["last_played"], reverse=True)
        return profiles

    def delete_profile(self, profile_id):
        """Delete a save profile"""
        save_file = os.path.join(self.save_dir, f"{profile_id}.json")

        if os.path.exists(save_file):
            try:
                os.remove(save_file)

                # Reset current profile if deleted
                if self.current_profile == profile_id:
                    self.current_profile = None
                    self.save_data = self.default_save_data.copy()

                return True
            except Exception as e:
                print(f"Error deleting save file: {e}")
                return False
        else:
            print(f"Save file not found: {save_file}")
            return False

    def get_completed_levels(self):
        """Get list of completed levels"""
        return self.save_data.get("completed_levels", [])

    def get_unlocked_levels(self):
        """Get list of unlocked levels"""
        return self.save_data.get("unlocked_levels", [0])  # Default to first level

    def mark_level_completed(self, level_id):
        """Mark a level as completed"""
        completed_levels = self.save_data.get("completed_levels", [])

        if level_id not in completed_levels:
            completed_levels.append(level_id)
            self.save_data["completed_levels"] = completed_levels

            # Unlock next level
            unlocked_levels = self.save_data.get("unlocked_levels", [0])
            next_level = level_id + 1

            if next_level not in unlocked_levels:
                unlocked_levels.append(next_level)
                self.save_data["unlocked_levels"] = unlocked_levels

            # Save immediately
            self.save_game()

    def update_high_score(self, level_id, score):
        """Update high score for a level"""
        high_scores = self.save_data.get("high_scores", {})

        # Convert to string key for JSON compatibility
        level_key = str(level_id)

        # Update if higher than current high score
        if level_key not in high_scores or score > high_scores[level_key]:
            high_scores[level_key] = score
            self.save_data["high_scores"] = high_scores

            # Save immediately
            self.save_game()
            return True

        return False

    def get_high_score(self, level_id):
        """Get high score for a level"""
        high_scores = self.save_data.get("high_scores", {})
        return high_scores.get(str(level_id), 0)

    def set_tutorial_completed(self, completed=True):
        """Mark tutorial as completed"""
        self.save_data["tutorial_completed"] = completed
        self.save_game()

    def is_tutorial_completed(self):
        """Check if tutorial has been completed"""
        return self.save_data.get("tutorial_completed", False)

    def _generate_profile_id(self, profile_name):
        """Generate a unique profile ID"""
        # Use timestamp for uniqueness
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # Clean the profile name for file naming
        clean_name = "".join(c for c in profile_name if c.isalnum() or c == "_")

        return f"{clean_name}_{timestamp}"

    def _save_to_file(self, profile_id, save_data):
        """Save data to file"""
        save_file = os.path.join(self.save_dir, f"{profile_id}.json")

        try:
            with open(save_file, "w") as f:
                json.dump(save_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def _update_game_state(self):
        """Update save data with current game state"""
        # Get current game state from game engine
        current_state = self.game_engine.state_manager.current_state

        # Store current level if in play state
        if current_state == "play_state":
            play_state = self.game_engine.state_manager.states.get("play_state")
            if play_state and hasattr(play_state, "level_type"):
                self.save_data["current_level"] = play_state.level_type

    def _apply_settings(self):
        """Apply settings from save data"""
        settings = self.save_data.get("settings", {})

        # Apply sound settings
        if hasattr(self.game_engine, "audio_manager"):
            self.game_engine.audio_manager.set_sound_volume(
                settings.get("sound_volume", 0.7)
            )
            self.game_engine.audio_manager.set_music_volume(
                settings.get("music_volume", 0.5)
            )

        # Apply other settings like fullscreen, etc.
        # This would typically interface with your existing settings system

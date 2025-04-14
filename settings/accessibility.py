import pygame
import json
import os
from settings import DATA_DIR


class AccessibilitySettings:
    """
    Manages accessibility settings for the game
    """

    def __init__(self):
        self.settings = {
            # Visual settings
            "high_contrast": False,  # Enhances contrast for better visibility
            "reduced_motion": False,  # Reduces or disables animations
            "larger_text": False,  # Increases text size
            "colorblind_mode": "None",  # Options: None, Protanopia, Deuteranopia, Tritanopia
            "screen_flash": True,  # Screen flash effects
            # Control settings
            "key_repeat": True,  # Enable key repetition
            "key_repeat_delay": 500,  # Delay before key repeat starts (ms)
            "key_repeat_interval": 100,  # Interval between key repeats (ms)
            "click_assist": False,  # Makes clicking easier
            # Audio settings
            "screen_reader": False,  # Enable/disable screen reader support
            "visual_cues": True,  # Visual indicators for audio cues
            # Gameplay settings
            "game_speed": 1.0,  # Game speed multiplier (0.5 - 1.5)
            "auto_aim": False,  # Assists with targeting
            "extended_time_limits": False,  # Extends time limits for puzzles
        }

        # Load settings from file
        self.settings_file = os.path.join(DATA_DIR, "accessibility.json")
        self.load_settings()

        # Apply settings
        self._apply_settings()

    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    loaded_settings = json.load(f)
                    # Update settings while preserving defaults for new settings
                    for key, value in loaded_settings.items():
                        if key in self.settings:
                            self.settings[key] = value
        except Exception as e:
            print(f"Error loading accessibility settings: {e}")

    def save_settings(self):
        """Save settings to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)

            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving accessibility settings: {e}")

    def update_setting(self, setting, value):
        """Update a specific setting"""
        if setting in self.settings:
            self.settings[setting] = value
            self._apply_settings()
            self.save_settings()
            return True
        return False

    def toggle_setting(self, setting):
        """Toggle a boolean setting"""
        if setting in self.settings and isinstance(self.settings[setting], bool):
            self.settings[setting] = not self.settings[setting]
            self._apply_settings()
            self.save_settings()
            return True
        return False

    def _apply_settings(self):
        """Apply settings to the game environment"""
        # Apply key repeat settings
        (
            pygame.key.set_repeat(
                self.settings["key_repeat_delay"], self.settings["key_repeat_interval"]
            )
            if self.settings["key_repeat"]
            else pygame.key.set_repeat(0)
        )

    def get_adjusted_text_size(self, base_size):
        """Get text size adjusted for accessibility settings"""
        if self.settings["larger_text"]:
            return int(base_size * 1.3)
        return base_size

    def get_color_adjusted(self, color):
        """Adjust colors for colorblind modes"""
        if self.settings["colorblind_mode"] == "None":
            return color

        r, g, b = color[:3]

        # Apply color transformations
        if self.settings["colorblind_mode"] == "Protanopia":
            # Red-blind
            r2 = 0.567 * r + 0.433 * g + 0.0 * b
            g2 = 0.558 * r + 0.442 * g + 0.0 * b
            b2 = 0.0 * r + 0.242 * g + 0.758 * b
            return (int(r2), int(g2), int(b2))
        elif self.settings["colorblind_mode"] == "Deuteranopia":
            # Green-blind
            r2 = 0.625 * r + 0.375 * g + 0.0 * b
            g2 = 0.7 * r + 0.3 * g + 0.0 * b
            b2 = 0.0 * r + 0.3 * g + 0.7 * b
            return (int(r2), int(g2), int(b2))
        elif self.settings["colorblind_mode"] == "Tritanopia":
            # Blue-blind
            r2 = 0.95 * r + 0.05 * g + 0.0 * b
            g2 = 0.0 * r + 0.433 * g + 0.567 * b
            b2 = 0.0 * r + 0.475 * g + 0.525 * b
            return (int(r2), int(g2), int(b2))

        return color

    def should_render_animation(self):
        """Determine if animations should be rendered"""
        return not self.settings["reduced_motion"]

    def get_game_speed(self):
        """Get adjusted game speed"""
        return self.settings["game_speed"]

import pygame
from settings import SOUND_DIR

class SoundManager:
    """
    Handles sound effects for the game
    """
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Sound effects dictionary
        self.sounds = {}
        
        # Sound categories for volume control
        self.categories = {
            'ui': 1.0,       # UI interaction sounds
            'effects': 1.0,  # Game effect sounds
            'ambient': 1.0,  # Ambient sounds
        }
        
        # Master volume
        self.master_volume = 1.0
        
        # Sound enabled flag
        self.sound_enabled = True
    
    def load_sound(self, name, filepath, category='effects'):
        """Load a sound effect and store it"""
        try:
            sound = pygame.mixer.Sound(filepath)
            self.sounds[name] = {
                'sound': sound,
                'category': category
            }
            return True
        except pygame.error:
            print(f"Could not load sound: {filepath}")
            return False
    
    def play(self, name, loops=0, volume=None):
        """Play a sound effect"""
        if not self.sound_enabled or name not in self.sounds:
            return None
        
        sound_data = self.sounds[name]
        sound = sound_data['sound']
        category = sound_data['category']
        
        # Calculate volume
        if volume is None:
            volume = self.master_volume * self.categories.get(category, 1.0)
        else:
            volume = volume * self.master_volume * self.categories.get(category, 1.0)
        
        sound.set_volume(volume)
        return sound.play(loops)
    
    def stop_all(self):
        """Stop all playing sounds"""
        pygame.mixer.stop()
    
    def set_master_volume(self, volume):
        """Set master volume (0.0 to 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        
        # Update volume for any currently playing sounds
        for sound_data in self.sounds.values():
            category = sound_data['category']
            sound_data['sound'].set_volume(self.master_volume * self.categories.get(category, 1.0))
    
    def set_category_volume(self, category, volume):
        """Set volume for a specific category of sounds"""
        if category in self.categories:
            self.categories[category] = max(0.0, min(1.0, volume))
            
            # Update volume for sounds in this category
            for sound_data in self.sounds.values():
                if sound_data['category'] == category:
                    sound_data['sound'].set_volume(self.master_volume * self.categories[category])
    
    def toggle_sound(self, enabled=None):
        """Toggle sound on/off"""
        if enabled is not None:
            self.sound_enabled = enabled
        else:
            self.sound_enabled = not self.sound_enabled
        
        # Pause/unpause sounds based on enabled state
        if not self.sound_enabled:
            pygame.mixer.pause()
        else:
            pygame.mixer.unpause()

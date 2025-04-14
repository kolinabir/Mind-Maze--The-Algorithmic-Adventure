import pygame

class BaseLevel:
    def __init__(self, game_engine, asset_manager):
        self.game_engine = game_engine
        self.assets = asset_manager
        self.completed = False
    
    def handle_event(self, event):
        """Handle pygame events"""
        pass
    
    def update(self, dt):
        """Update level logic"""
        pass
    
    def render(self, screen):
        """Render the level"""
        pass
    
    def reset(self):
        """Reset the level to its initial state"""
        self.completed = False

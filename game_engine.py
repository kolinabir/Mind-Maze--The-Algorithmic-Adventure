import pygame
from game_states import GameStateManager
from assets_manager import AssetManager
from settings import MENU_STATE

class GameEngine:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        
        # Initialize asset manager
        self.assets = AssetManager()
        
        # Initialize state manager with reference to this engine and assets
        self.state_manager = GameStateManager(self, self.assets)
        
        # Set initial state to menu
        self.state_manager.change_state(MENU_STATE)
    
    def handle_event(self, event):
        """Pass events to the current game state"""
        self.state_manager.handle_event(event)
    
    def update(self, dt):
        """Update the current game state"""
        self.state_manager.update(dt)
    
    def render(self):
        """Render the current game state"""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render current state
        self.state_manager.render(self.screen)

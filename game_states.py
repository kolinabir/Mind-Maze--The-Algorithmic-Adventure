import pygame
from settings import MENU_STATE, PLAY_STATE, SETTINGS_STATE, CREDITS_STATE
from menu import MainMenu

class GameState:
    def __init__(self, game_engine, asset_manager):
        self.game_engine = game_engine
        self.assets = asset_manager
    
    def enter(self):
        """Called when this state becomes active"""
        pass
    
    def exit(self):
        """Called when this state is no longer active"""
        pass
    
    def handle_event(self, event):
        """Handle pygame events"""
        pass
    
    def update(self, dt):
        """Update game logic"""
        pass
    
    def render(self, screen):
        """Render the state"""
        pass

class MenuState(GameState):
    def __init__(self, game_engine, asset_manager):
        super().__init__(game_engine, asset_manager)
        self.menu = MainMenu(game_engine, asset_manager)
    
    def enter(self):
        # Initialize menu
        pass
    
    def handle_event(self, event):
        self.menu.handle_event(event)
    
    def update(self, dt):
        self.menu.update(dt)
    
    def render(self, screen):
        self.menu.render(screen)

class PlayState(GameState):
    def __init__(self, game_engine, asset_manager):
        super().__init__(game_engine, asset_manager)
    
    def enter(self):
        print("Entering play state")
    
    def handle_event(self, event):
        # Placeholder for handling events in the play state
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_engine.state_manager.change_state(MENU_STATE)
    
    def update(self, dt):
        # Placeholder for game update logic
        pass
    
    def render(self, screen):
        # Placeholder for game rendering
        font = pygame.font.SysFont(None, 36)
        text = font.render('Game Screen (Press ESC to return to menu)', True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen.get_width()/2, screen.get_height()/2))
        screen.blit(text, text_rect)

class SettingsState(GameState):
    def __init__(self, game_engine, asset_manager):
        super().__init__(game_engine, asset_manager)
    
    def enter(self):
        print("Entering settings state")
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_engine.state_manager.change_state(MENU_STATE)
    
    def render(self, screen):
        font = pygame.font.SysFont(None, 36)
        text = font.render('Settings Screen (Press ESC to return to menu)', True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen.get_width()/2, screen.get_height()/2))
        screen.blit(text, text_rect)

class CreditsState(GameState):
    def __init__(self, game_engine, asset_manager):
        super().__init__(game_engine, asset_manager)
    
    def enter(self):
        print("Entering credits state")
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_engine.state_manager.change_state(MENU_STATE)
    
    def render(self, screen):
        font = pygame.font.SysFont(None, 36)
        text = font.render('Credits Screen (Press ESC to return to menu)', True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen.get_width()/2, screen.get_height()/2))
        screen.blit(text, text_rect)

class GameStateManager:
    def __init__(self, game_engine, asset_manager):
        self.game_engine = game_engine
        self.assets = asset_manager
        self.states = {
            MENU_STATE: MenuState(game_engine, asset_manager),
            PLAY_STATE: PlayState(game_engine, asset_manager),
            SETTINGS_STATE: SettingsState(game_engine, asset_manager),
            CREDITS_STATE: CreditsState(game_engine, asset_manager)
        }
        self.current_state = None
    
    def change_state(self, state_name):
        """Change to a new state"""
        if state_name in self.states:
            if self.current_state:
                self.current_state.exit()
            
            self.current_state = self.states[state_name]
            self.current_state.enter()
        else:
            print(f"Warning: State '{state_name}' does not exist")
    
    def handle_event(self, event):
        """Pass events to the current state"""
        if self.current_state:
            self.current_state.handle_event(event)
    
    def update(self, dt):
        """Update the current state"""
        if self.current_state:
            self.current_state.update(dt)
    
    def render(self, screen):
        """Render the current state"""
        if self.current_state:
            self.current_state.render(screen)

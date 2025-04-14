import pygame
from settings import (
    MENU_STATE, PLAY_STATE, SETTINGS_STATE, CREDITS_STATE, LEVEL_SELECT_STATE,
    MAZE_LEVEL, WATER_JUG_LEVEL, TICTACTOE_LEVEL, STRATEGY_LEVEL, FINAL_LEVEL
)
from screens.home_screen import HomeScreen
from screens.level_select import LevelSelectScreen
from ui.screen_manager import ScreenManager
from levels.maze_level import MazeLevel

class GameState:
    def __init__(self, game_engine, asset_manager):
        self.game_engine = game_engine
        self.assets = asset_manager
    
    def enter(self, **kwargs):
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
        self.home_screen = HomeScreen(game_engine, asset_manager)
    
    def enter(self, **kwargs):
        # Initialize menu
        pass
    
    def handle_event(self, event):
        self.home_screen.handle_event(event)
    
    def update(self, dt):
        self.home_screen.update(dt)
    
    def render(self, screen):
        self.home_screen.render(screen)

class LevelSelectState(GameState):
    def __init__(self, game_engine, asset_manager):
        super().__init__(game_engine, asset_manager)
        self.level_select = LevelSelectScreen(game_engine, asset_manager)
    
    def enter(self, **kwargs):
        pass
    
    def handle_event(self, event):
        self.level_select.handle_event(event)
    
    def update(self, dt):
        self.level_select.update(dt)
    
    def render(self, screen):
        self.level_select.render(screen)

class PlayState(GameState):
    def __init__(self, game_engine, asset_manager):
        super().__init__(game_engine, asset_manager)
        self.current_level = None
        self.level_type = None
        
        # Initialize all level types
        self.levels = {
            MAZE_LEVEL: MazeLevel(game_engine, asset_manager)
            # Other levels will be added later
        }
    
    def enter(self, **kwargs):
        print("Entering play state")
        self.level_type = kwargs.get("level_type", MAZE_LEVEL)
        
        # Set the current level based on type
        if self.level_type in self.levels:
            self.current_level = self.levels[self.level_type]
            # Reset the level each time we enter
            self.current_level.reset()
        else:
            print(f"Warning: Level type {self.level_type} not implemented yet")
    
    def handle_event(self, event):
        # Return to level select with ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_engine.state_manager.change_state(LEVEL_SELECT_STATE)
        
        # Pass events to current level
        if self.current_level:
            self.current_level.handle_event(event)
    
    def update(self, dt):
        if self.current_level:
            self.current_level.update(dt)
            
            # Check for level completion
            if self.current_level.completed:
                # Update user preferences to mark level as completed
                # This will be implemented when we add the user preferences system
                pass
    
    def render(self, screen):
        if self.current_level:
            self.current_level.render(screen)
        else:
            # Fallback for unimplemented levels
            font = pygame.font.SysFont(None, 36)
            level_name = {
                MAZE_LEVEL: "Maze Explorer",
                WATER_JUG_LEVEL: "Water Jug Challenge",
                TICTACTOE_LEVEL: "Tic-Tac-Toe Master",
                STRATEGY_LEVEL: "Strategy Game",
                FINAL_LEVEL: "Final Integration Challenge"
            }.get(self.level_type, "Unknown Level")
            
            text = font.render(f'Level type "{level_name}" not implemented yet', True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width()/2, screen.get_height()/2))
            screen.blit(text, text_rect)
            
            sub_text = font.render('Press ESC to return to level select', True, (255, 255, 255))
            sub_rect = sub_text.get_rect(center=(screen.get_width()/2, screen.get_height()/2 + 50))
            screen.blit(sub_text, sub_rect)

class SettingsState(GameState):
    def __init__(self, game_engine, asset_manager):
        super().__init__(game_engine, asset_manager)
    
    def enter(self, **kwargs):
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
    
    def enter(self, **kwargs):
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
        self.screen_manager = ScreenManager()
        
        # Create states
        self.states = {
            MENU_STATE: MenuState(game_engine, asset_manager),
            PLAY_STATE: PlayState(game_engine, asset_manager),
            SETTINGS_STATE: SettingsState(game_engine, asset_manager),
            CREDITS_STATE: CreditsState(game_engine, asset_manager),
            LEVEL_SELECT_STATE: LevelSelectState(game_engine, asset_manager)
        }
        
        self.current_state = None
        self.next_state = None
        self.next_state_params = {}
        
        # Screen capture for transitions
        self.screen = game_engine.screen
    
    def change_state(self, state_name, transition="fade", **kwargs):
        """Initiate a state change with transition"""
        if state_name in self.states:
            self.next_state = state_name
            self.next_state_params = kwargs
            
            # If we have a current state, start transition
            if self.current_state and not self.screen_manager.is_transitioning():
                # Capture current screen for transition
                current_surface = pygame.Surface(self.screen.get_size())
                current_surface.blit(self.screen, (0, 0))
                
                # Render next state to a surface for transition
                next_surface = pygame.Surface(self.screen.get_size())
                next_surface.fill((0, 0, 0))  # Clear with black
                self.states[state_name].render(next_surface)
                
                # Start the transition
                self.screen_manager.start_transition(current_surface, next_surface, transition)
            else:
                # No current state or already transitioning, change immediately
                self._complete_state_change()
        else:
            print(f"Warning: State '{state_name}' does not exist")
    
    def _complete_state_change(self):
        """Complete the state change after transition"""
        if self.current_state:
            self.states[self.current_state].exit()
            
        self.current_state = self.next_state
        self.states[self.current_state].enter(**self.next_state_params)
        self.next_state = None
    
    def handle_event(self, event):
        """Pass events to the current state"""
        if self.current_state and not self.screen_manager.is_transitioning():
            self.states[self.current_state].handle_event(event)
    
    def update(self, dt):
        """Update the current state or transitions"""
        if self.screen_manager.is_transitioning():
            # Update transition
            transition_complete = self.screen_manager.update(dt)
            if transition_complete:
                self._complete_state_change()
        elif self.current_state:
            # Update current state
            self.states[self.current_state].update(dt)
    
    def render(self, screen):
        """Render the current state or transition"""
        if self.screen_manager.is_transitioning():
            # Render the transition
            self.screen_manager.render(screen)
        elif self.current_state:
            # Render the current state
            self.states[self.current_state].render(screen)

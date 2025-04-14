import pygame
from ui.buttons import TextButton, ImageButton
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GRAY, LIGHT_BLUE, BLACK, BLUE,
    MENU_STATE, PLAY_STATE, MAZE_LEVEL, WATER_JUG_LEVEL, TICTACTOE_LEVEL, STRATEGY_LEVEL, FINAL_LEVEL
)

class Level:
    def __init__(self, name, description, unlocked=False, completed=False, icon_path=None):
        self.name = name
        self.description = description
        self.unlocked = unlocked
        self.completed = completed
        self.icon_path = icon_path
        
class LevelSelectScreen:
    def __init__(self, game_engine, asset_manager):
        self.game_engine = game_engine
        self.assets = asset_manager
        
        # Set up fonts
        self.title_font = pygame.font.SysFont(None, 48)
        self.desc_font = pygame.font.SysFont(None, 24)
        
        # Define levels
        self.levels = [
            Level("Maze Explorer", "Navigate through a maze using BFS or DFS algorithms", True),
            Level("Water Jug Challenge", "Solve the classic water jug problem with algorithmic thinking", True),  # Set to True to unlock
            Level("Tic-Tac-Toe Master", "Play against an AI using the Minimax algorithm", False),
            Level("Strategy Game", "Face a challenging opponent with Alpha-Beta pruning", False),
            Level("Final Integration", "Use all algorithms in the ultimate challenge", False),
        ]
        
        # Level types mapping
        self.level_types = [MAZE_LEVEL, WATER_JUG_LEVEL, TICTACTOE_LEVEL, STRATEGY_LEVEL, FINAL_LEVEL]
        
        # Initially selected level
        self.selected_level = 0 if self.levels[0].unlocked else None
        
        # Button for starting selected level
        self.start_button = TextButton(
            "Start Level", 
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80), 
            (200, 50),
            self.start_selected_level,
            hover_color=LIGHT_BLUE
        )
        
        # Back button
        self.back_button = TextButton(
            "Back", 
            (100, SCREEN_HEIGHT - 40), 
            (100, 40),
            self.go_back,
            hover_color=LIGHT_BLUE
        )
        
        # Create level selection buttons
        self._create_level_buttons()
    
    def _create_level_buttons(self):
        self.level_buttons = []
        button_width, button_height = 140, 140
        spacing = 20
        total_width = (button_width * len(self.levels)) + (spacing * (len(self.levels) - 1))
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        for i, level in enumerate(self.levels):
            x = start_x + (button_width + spacing) * i
            y = SCREEN_HEIGHT // 2 - 50
            
            # Create button for each level
            button = LevelButton(
                level.name,
                (x + button_width // 2, y + button_height // 2),
                (button_width, button_height),
                lambda i=i: self.select_level(i),
                level.unlocked,
                level.completed
            )
            self.level_buttons.append(button)
    
    def select_level(self, level_index):
        if self.levels[level_index].unlocked:
            self.selected_level = level_index
    
    def start_selected_level(self):
        if self.selected_level is not None and self.levels[self.selected_level].unlocked:
            level_type = self.level_types[self.selected_level]
            print(f"Starting level: {level_type}")  # Debug print to verify correct level type
            self.game_engine.state_manager.change_state(PLAY_STATE, level_type=level_type)
    
    def go_back(self):
        self.game_engine.state_manager.change_state(MENU_STATE)
    
    def handle_event(self, event):
        for button in self.level_buttons:
            button.handle_event(event)
        
        self.start_button.handle_event(event)
        self.back_button.handle_event(event)
    
    def update(self, dt):
        for button in self.level_buttons:
            button.update(dt)
        
        self.start_button.update(dt)
        self.back_button.update(dt)
    
    def render(self, screen):
        # Draw background
        screen.fill(BLACK)
        
        # Draw title
        title_surface = self.title_font.render("Select Level", True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_surface, title_rect)
        
        # Draw level buttons
        for i, button in enumerate(self.level_buttons):
            button.render(screen)
            # Highlight selected level
            if i == self.selected_level:
                pygame.draw.rect(screen, BLUE, button.rect, 3)
        
        # Draw description for selected level
        if self.selected_level is not None:
            level = self.levels[self.selected_level]
            desc_surface = self.desc_font.render(level.description, True, WHITE)
            desc_rect = desc_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140))
            screen.blit(desc_surface, desc_rect)
        
        # Draw buttons
        self.start_button.render(screen)
        self.back_button.render(screen)


class LevelButton(TextButton):
    def __init__(self, text, position, size, action, unlocked=True, completed=False):
        super().__init__(text, position, size, action if unlocked else None)
        self.unlocked = unlocked
        self.completed = completed
        self.icon_font = pygame.font.SysFont(None, 32)
    
    def render(self, screen):
        # Draw button background with different colors based on status
        if not self.unlocked:
            color = GRAY  # Locked level
        elif self.completed:
            color = LIGHT_BLUE  # Completed level
        elif self.is_hovered:
            color = (100, 100, 255)  # Hovered level
        else:
            color = BLUE  # Available level
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)  # Button border
        
        # Draw button text
        if not self.unlocked:
            text_surface = self.font.render("?", True, WHITE)
            icon_text = self.icon_font.render("🔒", True, WHITE)
        else:
            text_surface = self.font.render(self.text, True, WHITE)
            icon_text = self.icon_font.render("✓", True, WHITE) if self.completed else None
        
        text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.centery - 10))
        screen.blit(text_surface, text_rect)
        
        # Draw completion status icon
        if icon_text and self.completed:
            icon_rect = icon_text.get_rect(center=(self.rect.centerx, self.rect.centery + 30))
            screen.blit(icon_text, icon_rect)

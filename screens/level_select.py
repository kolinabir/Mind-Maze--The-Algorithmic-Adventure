import pygame
import math
import random
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GRAY, LIGHT_BLUE, BLACK, BLUE,
    MENU_STATE, PLAY_STATE, MAZE_LEVEL, WATER_JUG_LEVEL, TICTACTOE_LEVEL, STRATEGY_LEVEL, FINAL_LEVEL
)
from effects.particles import ParticleSystem

class Level:
    def __init__(self, name, description, unlocked=False, completed=False, icon_path=None):
        self.name = name
        self.description = description
        self.unlocked = unlocked
        self.completed = completed
        self.hover = False
        self.particles = ParticleSystem()
        self.hover_particles_active = False
        self.icon_rotation = 0

class LevelSelectScreen:
    def __init__(self, game_engine, asset_manager):
        self.game_engine = game_engine
        self.assets = asset_manager
        self.font = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 48)
        self.subtitle_font = pygame.font.SysFont(None, 32)
        self.back_button_rect = pygame.Rect(20, 20, 100, 40)
        
        # Setup background
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background.fill((30, 35, 40))
        
        # Create grid patterns on the background
        grid_spacing = 30
        grid_color = (40, 45, 50)
        for x in range(0, SCREEN_WIDTH, grid_spacing):
            pygame.draw.line(self.background, grid_color, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, grid_spacing):
            pygame.draw.line(self.background, grid_color, (0, y), (SCREEN_WIDTH, y))
            
        # Create algorithm-inspired decorative patterns
        for i in range(20):  # Create some random "nodes"
            x = random.randint(grid_spacing, SCREEN_WIDTH - grid_spacing)
            y = random.randint(grid_spacing, SCREEN_HEIGHT - grid_spacing)
            # Snap to grid
            x = (x // grid_spacing) * grid_spacing
            y = (y // grid_spacing) * grid_spacing
            pygame.draw.circle(self.background, (50, 55, 65), (x, y), 5)
            
            # Connect some nodes with lines
            if i > 0 and random.random() > 0.3:
                prev_x = ((random.randint(grid_spacing, SCREEN_WIDTH - grid_spacing)) // grid_spacing) * grid_spacing
                prev_y = ((random.randint(grid_spacing, SCREEN_HEIGHT - grid_spacing)) // grid_spacing) * grid_spacing
                pygame.draw.line(self.background, (40, 45, 60), (x, y), (prev_x, prev_y), 2)
        
        # Define levels - add icons and completion status
        self.levels = [
            Level("Maze Explorer", "Navigate through a maze using BFS or DFS algorithms", True),
            Level("Water Jug Challenge", "Solve the classic water jug problem with algorithmic thinking", True),
            Level("Tic-Tac-Toe Master", "Play against an AI using the Minimax algorithm", True),
            Level("Strategy Game", "Face a challenging opponent with Alpha-Beta pruning", True),
            Level("Final Integration", "Master all algorithms in the ultimate challenge", True)
        ]
        
        # Set up level completion status (would come from save data in a real game)
        self.levels[0].completed = True
        
        # Create level icons
        self.level_icons = []
        icon_colors = [(100, 200, 255), (100, 255, 200), (255, 200, 100), (200, 100, 255), (255, 100, 100)]
        
        for i, level in enumerate(self.levels):
            # Create a unique icon for each level
            icon = pygame.Surface((80, 80), pygame.SRCALPHA)
            base_color = icon_colors[i]
            
            # Draw the base circle
            pygame.draw.circle(icon, base_color, (40, 40), 35)
            
            # Add embellishments based on level type
            if i == 0:  # Maze level
                # Draw a simple maze pattern
                pygame.draw.rect(icon, (30, 30, 40), (20, 15, 40, 10))
                pygame.draw.rect(icon, (30, 30, 40), (20, 35, 40, 10))
                pygame.draw.rect(icon, (30, 30, 40), (20, 55, 40, 10))
                pygame.draw.rect(icon, (30, 30, 40), (15, 20, 10, 40))
                pygame.draw.rect(icon, (30, 30, 40), (55, 20, 10, 40))
            elif i == 1:  # Water jug
                # Draw water jugs
                pygame.draw.rect(icon, (50, 100, 200), (15, 25, 20, 30))
                pygame.draw.rect(icon, (50, 100, 200), (45, 30, 20, 25))
            elif i == 2:  # Tic-tac-toe
                # Draw tic-tac-toe grid
                pygame.draw.line(icon, (30, 30, 40), (25, 15), (25, 65), 4)
                pygame.draw.line(icon, (30, 30, 40), (55, 15), (55, 65), 4)
                pygame.draw.line(icon, (30, 30, 40), (15, 25), (65, 25), 4)
                pygame.draw.line(icon, (30, 30, 40), (15, 55), (65, 55), 4)
            elif i == 3:  # Strategy game
                # Draw strategy pieces
                pygame.draw.polygon(icon, (30, 30, 40), [(40, 15), (15, 50), (65, 50)])
                pygame.draw.circle(icon, (200, 200, 220), (40, 45), 12)
            else:  # Final level
                # Create star pattern
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    pygame.draw.line(icon, (255, 255, 100), 
                                   (40, 40), 
                                   (40 + 30 * math.cos(rad), 40 + 30 * math.sin(rad)), 
                                   3)
            
            # Add border
            pygame.draw.circle(icon, (255, 255, 255), (40, 40), 35, 3)
            
            # Add to level icons list
            self.level_icons.append(icon)
        
        # Create particles for each level
        for level in self.levels:
            if level.unlocked:
                level.particles.create_emitter(
                    "glow", 0, 0, 5, 2, 
                    (200, 200, 255, 100),
                    vel_range=(-5, 5),
                    size_range=(2, 8),
                    life_range=(0.3, 0.8),
                    fade=True
                )
        
        # Setup layout
        self.level_spacing = 200
        self.level_y = SCREEN_HEIGHT * 0.5
        self.selected_level = 0
        self.target_scroll = 0
        self.current_scroll = 0
        self.scroll_speed = 12
        self.scroll_lerp = 0.2
        self.max_scroll = (len(self.levels) - 1) * self.level_spacing
        
        # Animation
        self.animation_offset = 0
        self.animation_direction = 1
        self.pulse = 0
        
        # Description panel
        self.description_panel = pygame.Rect(
            SCREEN_WIDTH // 2 - 300, 
            SCREEN_HEIGHT * 0.7, 
            600, 150
        )
        
        # Particles
        self.particles = ParticleSystem()
        self.particles.create_emitter(
            "ambient", SCREEN_WIDTH // 2, 100, 2, 1, 
            (100, 150, 255, 150),
            vel_range=(-20, 20),
            size_range=(2, 6),
            life_range=(2, 5),
            fade=True
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if back button is clicked
            if self.back_button_rect.collidepoint(event.pos):
                self.game_engine.state_manager.change_state(MENU_STATE)
            
            # Check if any level is clicked
            mouse_x, mouse_y = event.pos
            for i, level in enumerate(self.levels):
                level_x = SCREEN_WIDTH // 2 + i * self.level_spacing - self.current_scroll
                level_y = self.level_y
                level_rect = pygame.Rect(level_x - 50, level_y - 50, 100, 100)
                
                if level_rect.collidepoint(mouse_x, mouse_y) and level.unlocked:
                    # Create click effect
                    self.particles.create_sparkle(mouse_x, mouse_y, 30, (255, 255, 200))
                    
                    # Start level
                    level_types = [MAZE_LEVEL, WATER_JUG_LEVEL, TICTACTOE_LEVEL, STRATEGY_LEVEL, FINAL_LEVEL]
                    self.game_engine.state_manager.change_state(PLAY_STATE, level_type=level_types[i])
        
        elif event.type == pygame.MOUSEMOTION:
            # Check for level hover
            mouse_x, mouse_y = event.pos
            for i, level in enumerate(self.levels):
                level_x = SCREEN_WIDTH // 2 + i * self.level_spacing - self.current_scroll
                level_y = self.level_y
                level_rect = pygame.Rect(level_x - 50, level_y - 50, 100, 100)
                
                if level_rect.collidepoint(mouse_x, mouse_y) and level.unlocked:
                    # Update selected level for detailed view
                    self.selected_level = i
                    level.hover = True
                    
                    # Set target scroll to center on selected level
                    self.target_scroll = i * self.level_spacing
                    
                    if not level.hover_particles_active:
                        level.hover_particles_active = True
                        level.particles.toggle_emitter("glow", True)
                else:
                    level.hover = False
                    if level.hover_particles_active:
                        level.hover_particles_active = False
                        level.particles.toggle_emitter("glow", False)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_engine.state_manager.change_state(MENU_STATE)
            elif event.key == pygame.K_LEFT:
                self.selected_level = max(0, self.selected_level - 1)
                self.target_scroll = self.selected_level * self.level_spacing
                self.particles.create_sparkle(
                    SCREEN_WIDTH // 2 - 100,
                    self.level_y,
                    20, (200, 200, 255)
                )
            elif event.key == pygame.K_RIGHT:
                self.selected_level = min(len(self.levels) - 1, self.selected_level + 1)
                self.target_scroll = self.selected_level * self.level_spacing
                self.particles.create_sparkle(
                    SCREEN_WIDTH // 2 + 100,
                    self.level_y,
                    20, (200, 200, 255)
                )
            elif event.key == pygame.K_RETURN:
                if self.levels[self.selected_level].unlocked:
                    level_types = [MAZE_LEVEL, WATER_JUG_LEVEL, TICTACTOE_LEVEL, STRATEGY_LEVEL, FINAL_LEVEL]
                    self.game_engine.state_manager.change_state(PLAY_STATE, level_type=level_types[self.selected_level])

    def update(self, dt):
        # Update scroll with smooth lerp
        self.current_scroll += (self.target_scroll - self.current_scroll) * self.scroll_lerp
        
        # Update animation
        self.animation_offset += self.animation_direction * 0.5
        if abs(self.animation_offset) > 5:
            self.animation_direction *= -1
        
        # Update pulse
        self.pulse = (self.pulse + dt) % (math.pi * 2)
        
        # Update particles
        self.particles.update(dt)
        
        # Update level-specific particles and animations
        for i, level in enumerate(self.levels):
            level_x = SCREEN_WIDTH // 2 + i * self.level_spacing - self.current_scroll
            level_y = self.level_y
            
            # Update particle positions
            level.particles.set_emitter_position("glow", level_x, level_y)
            level.particles.update(dt)
            
            # Update icon rotation for completed levels
            if level.completed:
                level.icon_rotation += dt * 20  # degrees per second
                level.icon_rotation %= 360

    def render(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))
        
        # Draw particles under everything
        self.particles.draw(screen)
        
        # Draw title
        title_text = self.title_font.render("SELECT LEVEL", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))
        
        # Draw navigation hint
        hint_text = self.font.render("Use arrow keys to navigate, Enter to select", True, (200, 200, 200))
        screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, 80))
        
        # Draw level selector
        for i, level in enumerate(self.levels):
            level_x = SCREEN_WIDTH // 2 + i * self.level_spacing - self.current_scroll
            level_y = self.level_y + (self.animation_offset if i == self.selected_level else 0)
            
            # Skip if off-screen
            if level_x < -100 or level_x > SCREEN_WIDTH + 100:
                continue
            
            # Draw level-specific particles
            level.particles.draw(screen)
            
            # Draw connecting path between levels
            if i > 0:
                prev_x = SCREEN_WIDTH // 2 + (i-1) * self.level_spacing - self.current_scroll
                prev_y = self.level_y
                
                # Draw dotted path
                for j in range(20):
                    dot_x = prev_x + (level_x - prev_x) * (j / 19)
                    dot_y = prev_y + 4 * math.sin(j * math.pi / 5 + self.pulse * 2)
                    
                    # Different colors based on completion status
                    if self.levels[i-1].completed:
                        color = BLUE
                    else:
                        color = GRAY
                        
                    pygame.draw.circle(screen, color, (dot_x, dot_y), 3)
            
            # Draw icon with potential rotation for completed levels
            icon = self.level_icons[i]
            if level.completed:
                # Rotate the icon
                rotated_icon = pygame.transform.rotate(icon, level.icon_rotation)
                # Get the rect to center properly
                icon_rect = rotated_icon.get_rect(center=(level_x, level_y))
                screen.blit(rotated_icon, icon_rect)
            else:
                # No rotation needed
                screen.blit(icon, (level_x - 40, level_y - 40))
            
            # Draw level completion indicators
            if level.completed:
                # Draw checkmark
                pygame.draw.circle(screen, BLUE, (level_x + 30, level_y - 30), 15)
                # Draw checkmark symbol
                pygame.draw.line(screen, WHITE, (level_x + 23, level_y - 30), (level_x + 28, level_y - 25), 3)
                pygame.draw.line(screen, WHITE, (level_x + 28, level_y - 25), (level_x + 37, level_y - 35), 3)
            
            # Draw level lock if not unlocked
            if not level.unlocked:
                lock_rect = pygame.Rect(level_x - 15, level_y - 15, 30, 30)
                pygame.draw.rect(screen, GRAY, lock_rect)
                pygame.draw.rect(screen, WHITE, lock_rect, 2)
                pygame.draw.rect(screen, GRAY, (level_x - 10, level_y - 25, 20, 15))
                pygame.draw.rect(screen, WHITE, (level_x - 10, level_y - 25, 20, 15), 2)
            
            # Draw level number
            num_text = self.subtitle_font.render(str(i + 1), True, WHITE)
            screen.blit(num_text, (level_x - num_text.get_width() // 2, level_y + 55))
        
        # Draw level description panel
        if 0 <= self.selected_level < len(self.levels):
            selected = self.levels[self.selected_level]
            
            # Draw panel background with subtle pulse
            pulse_scale = 1 + 0.02 * math.sin(self.pulse * 3)
            panel_width = int(self.description_panel.width * pulse_scale)
            panel_height = self.description_panel.height
            panel_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - panel_width // 2,
                self.description_panel.y,
                panel_width,
                panel_height
            )
            
            # Create panel with transparent background
            panel = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(panel, (20, 30, 50, 200), (0, 0, panel_rect.width, panel_rect.height))
            pygame.draw.rect(panel, (100, 150, 255, 100), (0, 0, panel_rect.width, panel_rect.height), 3)
            
            # Add visual decorations to the panel
            for i in range(5):
                line_y = i * (panel_rect.height / 5)
                pygame.draw.line(panel, (100, 150, 255, 50), 
                               (0, line_y), (panel_rect.width, line_y), 1)
            
            screen.blit(panel, panel_rect)
            
            # Draw level name
            name_text = self.subtitle_font.render(selected.name, True, WHITE)
            screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, panel_rect.y + 20))
            
            # Draw description
            desc_text = self.font.render(selected.description, True, (200, 200, 200))
            screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, panel_rect.y + 70))
            
            # Draw status
            if not selected.unlocked:
                status_text = self.font.render("LOCKED", True, BLUE)
            elif selected.completed:
                status_text = self.font.render("COMPLETED", True, BLUE)
            else:
                status_text = self.font.render("AVAILABLE", True, BLUE)
            
            screen.blit(status_text, (SCREEN_WIDTH // 2 - status_text.get_width() // 2, panel_rect.y + 100))
            
            # Draw prompt
            if selected.unlocked:
                prompt_text = self.font.render("Press ENTER to play", True, BLUE)
                y_offset = math.sin(self.pulse * 5) * 3  # Make it pulsate
                screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, panel_rect.y + 130 + y_offset))
        
        # Draw back button
        pygame.draw.rect(screen, (50, 50, 70), self.back_button_rect)
        pygame.draw.rect(screen, (100, 100, 150), self.back_button_rect, 2)
        back_text = self.font.render("Back", True, WHITE)
        screen.blit(back_text, (self.back_button_rect.centerx - back_text.get_width() // 2, 
                             self.back_button_rect.centery - back_text.get_height() // 2))

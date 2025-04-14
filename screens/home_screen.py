import pygame
import math
import time
from ui.buttons import ImageButton, TextButton
from ui.animated_background import AnimatedBackground
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    WHITE,
    LIGHT_BLUE,
    MENU_STATE,
    PLAY_STATE,
    SETTINGS_STATE,
    CREDITS_STATE,
    LEVEL_SELECT_STATE,
)


class HomeScreen:
    def __init__(self, game_engine, asset_manager):
        self.game_engine = game_engine
        self.assets = asset_manager

        # Load fonts and create text objects
        self.title_font = pygame.font.SysFont(None, 80)
        self.subtitle_font = pygame.font.SysFont(None, 40)

        # Title text with shadow effect
        self.title_text = "MIND MAZE"
        self.subtitle_text = "The Algorithmic Adventure"

        # Create animated background
        self.background = AnimatedBackground()

        # Logo position and animation
        self.logo_pos = [SCREEN_WIDTH // 2, 120]
        self.logo_scale = 1.0
        self.logo_scale_direction = 1
        self.logo_start_time = time.time()

        # Create buttons
        button_width, button_height = 250, 60
        center_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2
        spacing = 70

        self.buttons = [
            TextButton(
                "Start Game",
                (center_x, start_y),
                (button_width, button_height),
                self.on_start_click,
                hover_color=LIGHT_BLUE,
            ),
            TextButton(
                "Settings",
                (center_x, start_y + spacing),
                (button_width, button_height),
                self.on_settings_click,
                hover_color=LIGHT_BLUE,
            ),
            TextButton(
                "Credits",
                (center_x, start_y + spacing * 2),
                (button_width, button_height),
                self.on_credits_click,
                hover_color=LIGHT_BLUE,
            ),
            TextButton(
                "Exit",
                (center_x, start_y + spacing * 3),
                (button_width, button_height),
                self.on_exit_click,
                hover_color=LIGHT_BLUE,
            ),
        ]

    def on_start_click(self):
        self.game_engine.state_manager.change_state(LEVEL_SELECT_STATE)

    def on_settings_click(self):
        self.game_engine.state_manager.change_state(SETTINGS_STATE)

    def on_credits_click(self):
        self.game_engine.state_manager.change_state(CREDITS_STATE)

    def on_exit_click(self):
        pygame.quit()
        exit()

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt):
        # Update animated background
        self.background.update(dt)

        # Animate logo scaling
        t = time.time() - self.logo_start_time
        self.logo_scale = 1.0 + math.sin(t) * 0.05  # Subtle pulsing effect

        # Update buttons
        for button in self.buttons:
            button.update(dt)

    def render(self, screen):
        # Draw animated background
        self.background.render(screen)

        # Draw logo with pulse effect
        title_surface = self.title_font.render(self.title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(self.logo_pos[0], self.logo_pos[1]))

        # Apply scale to title
        scaled_width = int(title_surface.get_width() * self.logo_scale)
        scaled_height = int(title_surface.get_height() * self.logo_scale)
        scaled_title = pygame.transform.scale(
            title_surface, (scaled_width, scaled_height)
        )
        scaled_rect = scaled_title.get_rect(center=(self.logo_pos[0], self.logo_pos[1]))
        screen.blit(scaled_title, scaled_rect)

        # Draw subtitle
        subtitle_surface = self.subtitle_font.render(
            self.subtitle_text, True, LIGHT_BLUE
        )
        subtitle_rect = subtitle_surface.get_rect(
            center=(self.logo_pos[0], self.logo_pos[1] + 60)
        )
        screen.blit(subtitle_surface, subtitle_rect)

        # Draw buttons
        for button in self.buttons:
            button.render(screen)

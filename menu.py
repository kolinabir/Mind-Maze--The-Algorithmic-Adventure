import pygame
from settings import (
    MENU_BG_COLOR,
    MENU_TEXT_COLOR,
    MENU_HIGHLIGHT_COLOR,
    BUTTON_SIZE,
    PLAY_STATE,
    SETTINGS_STATE,
    CREDITS_STATE,
)


class Button:
    def __init__(self, text, position, size=BUTTON_SIZE, action=None):
        self.text = text
        self.position = position
        self.size = size
        self.action = action
        self.rect = pygame.Rect(
            position[0] - size[0] // 2, position[1] - size[1] // 2, size[0], size[1]
        )
        self.is_hovered = False
        self.font = pygame.font.SysFont(None, 32)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()

    def update(self, dt):
        pass

    def render(self, screen):
        # Draw button background
        color = MENU_HIGHLIGHT_COLOR if self.is_hovered else MENU_BG_COLOR
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, MENU_TEXT_COLOR, self.rect, 2)  # Button border

        # Draw button text
        text_surface = self.font.render(self.text, True, MENU_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class MainMenu:
    def __init__(self, game_engine, asset_manager):
        self.game_engine = game_engine
        self.assets = asset_manager

        # Screen dimensions
        screen_width = self.game_engine.screen.get_width()
        screen_height = self.game_engine.screen.get_height()
        center_x = screen_width // 2

        # Create buttons
        button_spacing = 70
        start_y = screen_height // 2 - 50

        self.buttons = [
            Button("Play", (center_x, start_y), action=self.start_game),
            Button(
                "Settings",
                (center_x, start_y + button_spacing),
                action=self.open_settings,
            ),
            Button(
                "Credits",
                (center_x, start_y + 2 * button_spacing),
                action=self.open_credits,
            ),
            Button(
                "Exit", (center_x, start_y + 3 * button_spacing), action=self.exit_game
            ),
        ]

        # Title text
        self.title_font = pygame.font.SysFont(None, 64)
        self.title_text = "Mind Maze"
        self.subtitle_font = pygame.font.SysFont(None, 36)
        self.subtitle_text = "The Algorithmic Adventure"

    def start_game(self):
        self.game_engine.state_manager.change_state(PLAY_STATE)

    def open_settings(self):
        self.game_engine.state_manager.change_state(SETTINGS_STATE)

    def open_credits(self):
        self.game_engine.state_manager.change_state(CREDITS_STATE)

    def exit_game(self):
        pygame.quit()
        exit()

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt):
        for button in self.buttons:
            button.update(dt)

    def render(self, screen):
        # Draw background
        screen.fill(MENU_BG_COLOR)

        # Draw title
        title_surface = self.title_font.render(self.title_text, True, MENU_TEXT_COLOR)
        title_rect = title_surface.get_rect(centerx=screen.get_width() // 2, top=50)
        screen.blit(title_surface, title_rect)

        # Draw subtitle
        subtitle_surface = self.subtitle_font.render(
            self.subtitle_text, True, MENU_TEXT_COLOR
        )
        subtitle_rect = subtitle_surface.get_rect(
            centerx=screen.get_width() // 2, top=title_rect.bottom + 10
        )
        screen.blit(subtitle_surface, subtitle_rect)

        # Draw buttons
        for button in self.buttons:
            button.render(screen)

import pygame
import os
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    WHITE,
    BLACK,
    LIGHT_BLUE,
    GRAY,
    MENU_STATE,
    MENU_BG_COLOR,
    MENU_TEXT_COLOR,
    MENU_HIGHLIGHT_COLOR,
    DARK_BLUE,
)
from ui.buttons import TextButton
from effects.particles import ParticleSystem


class SettingsScreen:
    def __init__(self, game_engine, asset_manager):
        self.game_engine = game_engine
        self.assets = asset_manager

        # Fonts
        self.title_font = pygame.font.SysFont(None, 48)
        self.subtitle_font = pygame.font.SysFont(None, 36)
        self.font = pygame.font.SysFont(None, 28)

        # Background
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background.fill(DARK_BLUE)

        # Create grid pattern for background
        grid_spacing = 40
        grid_color = (30, 40, 80)
        for x in range(0, SCREEN_WIDTH, grid_spacing):
            pygame.draw.line(self.background, grid_color, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, grid_spacing):
            pygame.draw.line(self.background, grid_color, (0, y), (SCREEN_WIDTH, y))

        # Particles
        self.particles = ParticleSystem()
        self.particles.create_emitter(
            "ambient",
            SCREEN_WIDTH // 2,
            100,
            1,
            1,  # Changed from 0.5 to 1 (integer value)
            (100, 150, 255, 150),
            vel_range=(-20, 20),
            size_range=(2, 5),
            life_range=(2, 4),
            fade=True,
        )

        # Create buttons
        self.create_buttons()

        # Settings variables
        self.music_volume = 0.5
        self.sound_volume = 0.7
        self.fullscreen = False
        self.show_hints = True

        # Load current settings
        self.load_settings()

    def create_buttons(self):
        center_x = SCREEN_WIDTH // 2
        start_y = 180
        spacing = 60
        button_width = 250
        button_height = 50

        # Create slider buttons
        self.music_minus_btn = TextButton(
            "-", (center_x - 100, start_y), (40, 40), self.decrease_music
        )
        self.music_plus_btn = TextButton(
            "+", (center_x + 100, start_y), (40, 40), self.increase_music
        )

        self.sound_minus_btn = TextButton(
            "-", (center_x - 100, start_y + spacing), (40, 40), self.decrease_sound
        )
        self.sound_plus_btn = TextButton(
            "+", (center_x + 100, start_y + spacing), (40, 40), self.increase_sound
        )

        # Toggle buttons
        self.fullscreen_btn = TextButton(
            "Fullscreen: OFF",
            (center_x, start_y + spacing * 2),
            (button_width, button_height),
            self.toggle_fullscreen,
        )

        self.hints_btn = TextButton(
            "Hints: ON",
            (center_x, start_y + spacing * 3),
            (button_width, button_height),
            self.toggle_hints,
        )

        # Action buttons
        self.clear_data_btn = TextButton(
            "Clear Saved Data",
            (center_x, start_y + spacing * 4),
            (button_width, button_height),
            self.clear_data,
        )

        # Back button
        self.back_btn = TextButton(
            "Back to Menu",
            (center_x, SCREEN_HEIGHT - 70),
            (button_width, button_height),
            self.return_to_menu,
        )

        # All buttons for iteration
        self.buttons = [
            self.music_minus_btn,
            self.music_plus_btn,
            self.sound_minus_btn,
            self.sound_plus_btn,
            self.fullscreen_btn,
            self.hints_btn,
            self.clear_data_btn,
            self.back_btn,
        ]

    def load_settings(self):
        # Load settings from save manager
        if hasattr(self.game_engine, "save_manager"):
            save_data = self.game_engine.save_manager.save_data
            settings = save_data.get("settings", {})

            self.music_volume = settings.get("music_volume", 0.5)
            self.sound_volume = settings.get("sound_volume", 0.7)
            self.fullscreen = settings.get("fullscreen", False)
            self.show_hints = settings.get("show_hints", True)

            # Update button text
            self.fullscreen_btn.text = (
                f"Fullscreen: {'ON' if self.fullscreen else 'OFF'}"
            )
            self.hints_btn.text = f"Hints: {'ON' if self.show_hints else 'OFF'}"

    def save_settings(self):
        # Save settings via save manager
        if hasattr(self.game_engine, "save_manager"):
            save_data = self.game_engine.save_manager.save_data

            if "settings" not in save_data:
                save_data["settings"] = {}

            save_data["settings"]["music_volume"] = self.music_volume
            save_data["settings"]["sound_volume"] = self.sound_volume
            save_data["settings"]["fullscreen"] = self.fullscreen
            save_data["settings"]["show_hints"] = self.show_hints

            self.game_engine.save_manager.save_game()

    # Settings actions
    def decrease_music(self):
        self.music_volume = max(0.0, self.music_volume - 0.1)
        self.apply_settings()
        self.particles.create_sparkle(SCREEN_WIDTH // 2 - 100, 180, 10, (200, 200, 255))

    def increase_music(self):
        self.music_volume = min(1.0, self.music_volume + 0.1)
        self.apply_settings()
        self.particles.create_sparkle(SCREEN_WIDTH // 2 + 100, 180, 10, (200, 200, 255))

    def decrease_sound(self):
        self.sound_volume = max(0.0, self.sound_volume - 0.1)
        self.apply_settings()
        self.particles.create_sparkle(SCREEN_WIDTH // 2 - 100, 240, 10, (200, 200, 255))

    def increase_sound(self):
        self.sound_volume = min(1.0, self.sound_volume + 0.1)
        self.apply_settings()
        self.particles.create_sparkle(SCREEN_WIDTH // 2 + 100, 240, 10, (200, 200, 255))

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.fullscreen_btn.text = f"Fullscreen: {'ON' if self.fullscreen else 'OFF'}"
        self.apply_settings()
        self.particles.create_sparkle(SCREEN_WIDTH // 2, 300, 20, (200, 200, 255))

    def toggle_hints(self):
        self.show_hints = not self.show_hints
        self.hints_btn.text = f"Hints: {'ON' if self.show_hints else 'OFF'}"
        self.apply_settings()
        self.particles.create_sparkle(SCREEN_WIDTH // 2, 360, 20, (200, 200, 255))

    def clear_data(self):
        # Create confirmation effect
        self.particles.create_explosion(SCREEN_WIDTH // 2, 420, 30, (255, 100, 100))

        # Delete all save files except current
        if hasattr(self.game_engine, "save_manager"):
            save_dir = self.game_engine.save_manager.save_dir
            current_profile = self.game_engine.save_manager.current_profile

            try:
                for filename in os.listdir(save_dir):
                    if filename.endswith(".json") and not filename.startswith(
                        current_profile
                    ):
                        file_path = os.path.join(save_dir, filename)
                        os.remove(file_path)

                # Reset current save to defaults but keep settings
                save_data = self.game_engine.save_manager.save_data
                settings = save_data.get("settings", {})

                # Create new save with defaults
                self.game_engine.save_manager.save_data = (
                    self.game_engine.save_manager.default_save_data.copy()
                )

                # Keep existing settings
                self.game_engine.save_manager.save_data["settings"] = settings

                # Keep only first level unlocked
                self.game_engine.save_manager.save_data["unlocked_levels"] = [0]
                self.game_engine.save_manager.save_data["completed_levels"] = []

                # Save changes
                self.game_engine.save_manager.save_game()

            except Exception as e:
                print(f"Error clearing saved data: {e}")

    def return_to_menu(self):
        self.save_settings()
        self.game_engine.state_manager.change_state(MENU_STATE)

    def apply_settings(self):
        # Update volume settings in audio manager if it exists
        if hasattr(self.game_engine, "audio_manager"):
            self.game_engine.audio_manager.set_music_volume(self.music_volume)
            self.game_engine.audio_manager.set_sound_volume(self.sound_volume)

        # Update fullscreen mode
        if self.fullscreen:
            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Save settings to file
        self.save_settings()

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.return_to_menu()

    def update(self, dt):
        for button in self.buttons:
            button.update(dt)

        self.particles.update(dt)

    def render(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))

        # Draw particles
        self.particles.draw(screen)

        # Draw title
        title_text = self.title_font.render("SETTINGS", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

        # Draw sliders
        center_x = SCREEN_WIDTH // 2
        start_y = 180
        spacing = 60

        # Music volume
        label = self.subtitle_font.render("Music Volume", True, LIGHT_BLUE)
        screen.blit(label, (center_x - label.get_width() // 2, start_y - 40))

        # Draw music volume slider
        pygame.draw.rect(screen, GRAY, (center_x - 80, start_y, 160, 10))
        pygame.draw.rect(
            screen,
            LIGHT_BLUE,
            (center_x - 80, start_y, int(160 * self.music_volume), 10),
        )
        pygame.draw.circle(
            screen,
            WHITE,
            (center_x - 80 + int(160 * self.music_volume), start_y + 5),
            8,
        )

        # Sound volume
        label = self.subtitle_font.render("Sound Effects", True, LIGHT_BLUE)
        screen.blit(label, (center_x - label.get_width() // 2, start_y + spacing - 40))

        # Draw sound volume slider
        pygame.draw.rect(screen, GRAY, (center_x - 80, start_y + spacing, 160, 10))
        pygame.draw.rect(
            screen,
            LIGHT_BLUE,
            (center_x - 80, start_y + spacing, int(160 * self.sound_volume), 10),
        )
        pygame.draw.circle(
            screen,
            WHITE,
            (center_x - 80 + int(160 * self.sound_volume), start_y + spacing + 5),
            8,
        )

        # Draw buttons
        for button in self.buttons:
            button.render(screen)

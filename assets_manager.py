import os
import pygame
from settings import IMAGE_DIR, SOUND_DIR, FONT_DIR


class AssetManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}

        # Create asset directories if they don't exist
        self._create_asset_directories()

    def _create_asset_directories(self):
        """Create directory structure for assets if it doesn't exist"""
        directories = [IMAGE_DIR, SOUND_DIR, FONT_DIR]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def load_image(self, name, file_path, scale=1.0, convert_alpha=True):
        """Load an image and store it in the images dictionary"""
        try:
            if convert_alpha:
                image = pygame.image.load(file_path).convert_alpha()
            else:
                image = pygame.image.load(file_path).convert()

            if scale != 1.0:
                new_width = int(image.get_width() * scale)
                new_height = int(image.get_height() * scale)
                image = pygame.transform.scale(image, (new_width, new_height))

            self.images[name] = image
            return True
        except pygame.error as e:
            print(f"Failed to load image {file_path}: {e}")
            return False

    def load_sound(self, name, file_path):
        """Load a sound file and store it in the sounds dictionary"""
        try:
            sound = pygame.mixer.Sound(file_path)
            self.sounds[name] = sound
            return True
        except pygame.error as e:
            print(f"Failed to load sound {file_path}: {e}")
            return False

    def load_font(self, name, file_path, size):
        """Load a font and store it in the fonts dictionary"""
        try:
            font = pygame.font.Font(file_path, size)
            # Store with size in the name to allow same font with different sizes
            self.fonts[f"{name}_{size}"] = font
            return True
        except pygame.error as e:
            print(f"Failed to load font {file_path}: {e}")
            return False

    def get_image(self, name):
        """Get an image by name"""
        if name in self.images:
            return self.images[name]
        print(f"Warning: Image '{name}' not found")
        return None

    def get_sound(self, name):
        """Get a sound by name"""
        if name in self.sounds:
            return self.sounds[name]
        print(f"Warning: Sound '{name}' not found")
        return None

    def get_font(self, name, size):
        """Get a font by name and size"""
        font_key = f"{name}_{size}"
        if font_key in self.fonts:
            return self.fonts[font_key]
        print(f"Warning: Font '{font_key}' not found")
        return pygame.font.SysFont("Arial", size)  # Fallback to system font

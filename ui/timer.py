import pygame
from settings import WHITE, BLACK, GREEN, YELLOW, RED


class MoveTimer:
    def __init__(self, time_limit):
        self.time_limit = time_limit
        self.time_left = time_limit
        self.font = pygame.font.SysFont(None, 32)
        self.active = True

    def update(self, dt):
        """
        Update timer and return True if time is up

        Args:
            dt: Time elapsed since last update (in seconds)

        Returns:
            True if time is up, False otherwise
        """
        if not self.active:
            return False

        self.time_left -= dt

        if self.time_left <= 0:
            self.time_left = 0
            return True

        return False

    def reset(self, time_limit=None):
        """Reset the timer"""
        if time_limit is not None:
            self.time_limit = time_limit
        self.time_left = self.time_limit
        self.active = True

    def pause(self):
        """Pause the timer"""
        self.active = False

    def resume(self):
        """Resume the timer"""
        self.active = True

    def add_time(self, additional_seconds):
        """Add time to the timer"""
        self.time_left += additional_seconds

    def render(self, screen, position):
        """
        Render the timer

        Args:
            screen: Pygame surface to draw on
            position: Center position for the timer (x, y)
        """
        # Determine color based on time remaining
        if self.time_left > self.time_limit * 0.7:
            color = GREEN
        elif self.time_left > self.time_limit * 0.3:
            color = YELLOW
        else:
            color = RED

        # Create timer text
        minutes = int(self.time_left) // 60
        seconds = int(self.time_left) % 60
        text = f"Time: {minutes:02d}:{seconds:02d}"

        # Draw timer with background
        text_surface = self.font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=position)

        # Draw background with pulsing effect when time is low
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(screen, BLACK, bg_rect)

        # Draw colored border
        border_width = 2
        if self.time_left < self.time_limit * 0.3:
            # Make border pulse when time is running out
            border_width = 2 + int(abs(pygame.time.get_ticks() % 1000 - 500) / 100)

        pygame.draw.rect(screen, color, bg_rect, border_width)

        # Draw timer text
        screen.blit(text_surface, text_rect)

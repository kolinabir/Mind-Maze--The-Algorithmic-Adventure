import pygame
import math


class Player:
    def __init__(self, position, size=(24, 24), color=(0, 128, 255)):
        self.position = position  # Center position
        self.size = size
        self.color = color
        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.rect.center = position

        # Movement animation
        self.target_position = position
        self.move_speed = 10.0  # Pixels per second
        self.is_moving = False

        # Visual effects
        self.pulse_amount = 0
        self.pulse_speed = 3.0

    def move_to(self, position):
        """Set a new target position for the player"""
        self.target_position = position
        self.is_moving = True

    def update(self, dt):
        """Update player logic"""
        # Move towards target position
        if self.is_moving:
            dx = self.target_position[0] - self.position[0]
            dy = self.target_position[1] - self.position[1]

            distance = (dx**2 + dy**2) ** 0.5

            if distance < 1.0:  # Close enough to target
                self.position = self.target_position
                self.is_moving = False
            else:
                move_step = self.move_speed * dt * 60

                # Normalize direction and scale by move_step
                if distance > 0:
                    self.position = (
                        self.position[0] + dx / distance * move_step,
                        self.position[1] + dy / distance * move_step,
                    )

        # Update rectangle position
        self.rect.center = self.position

        # Update pulse effect
        self.pulse_amount = (self.pulse_amount + self.pulse_speed * dt) % (2 * math.pi)

    def render(self, screen):
        """Render the player"""
        # Calculate pulse effect (slight size oscillation)
        pulse_scale = 1.0 + 0.1 * math.sin(self.pulse_amount)
        pulse_width = int(self.size[0] * pulse_scale)
        pulse_height = int(self.size[1] * pulse_scale)

        pulse_rect = pygame.Rect(0, 0, pulse_width, pulse_height)
        pulse_rect.center = self.position

        # Draw player
        pygame.draw.rect(screen, self.color, pulse_rect)

        # Draw player outline
        pygame.draw.rect(screen, (255, 255, 255), pulse_rect, 2)

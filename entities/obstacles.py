import pygame
import math

class Teleporter:
    def __init__(self, cell_pos, position, color=(255, 0, 255)):
        self.cell_pos = cell_pos  # Grid coordinates
        self.position = position  # Center pixel position
        self.color = color
        self.radius = 10
        self.linked_teleporter = None
        
        # Animation properties
        self.pulse_amount = 0
        self.pulse_speed = 2.0
        self.rotation = 0
        self.rotation_speed = 1.0
    
    def link_teleporter(self, other_teleporter):
        """Link this teleporter to another teleporter"""
        self.linked_teleporter = other_teleporter
    
    def update(self, dt):
        """Update teleporter animations"""
        # Update pulse effect
        self.pulse_amount = (self.pulse_amount + self.pulse_speed * dt) % (2 * 3.14159)
        
        # Update rotation
        self.rotation = (self.rotation + self.rotation_speed * dt) % (2 * 3.14159)
    
    def render(self, screen):
        """Render the teleporter"""
        # Calculate pulse effect
        pulse = 1.0 + 0.2 * math.sin(self.pulse_amount)
        pulse_radius = int(self.radius * pulse)
        
        # Draw main circle
        pygame.draw.circle(screen, self.color, self.position, pulse_radius)
        
        # Draw center pattern
        center_radius = pulse_radius // 2
        pygame.draw.circle(screen, (255, 255, 255), self.position, center_radius)
        
        # Draw rotating elements
        angle1 = self.rotation
        angle2 = self.rotation + 3.14159
        
        # Calculate points for rotating elements
        point1 = (
            self.position[0] + int(math.cos(angle1) * pulse_radius),
            self.position[1] + int(math.sin(angle1) * pulse_radius)
        )
        point2 = (
            self.position[0] + int(math.cos(angle2) * pulse_radius),
            self.position[1] + int(math.sin(angle2) * pulse_radius)
        )
        
        # Draw lines between points through center
        pygame.draw.line(screen, (255, 255, 255), point1, point2, 2)
        
        # Draw outline
        pygame.draw.circle(screen, (255, 255, 255), self.position, pulse_radius, 2)

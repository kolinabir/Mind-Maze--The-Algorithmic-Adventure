import pygame
import random
import math
from settings import WHITE

class PowerUpSystem:
    def __init__(self, board_size, board_state, frequency=0.5):
        self.board_size = board_size
        self.board_state = board_state
        self.power_ups = {}  # Dictionary mapping (row, col) -> power_up_type
        self.frequency = frequency  # Higher value = more power-ups
        
        # Power-up types and colors
        self.power_up_types = [
            ("extra_move", (255, 215, 0)),     # Gold - extra turn
            ("extra_time", (0, 255, 127)),     # Green - time bonus
            ("shield", (70, 130, 180)),        # Steel blue - protection
            ("double_piece", (255, 105, 180))  # Pink - duplicate piece
        ]
        
        # Visual effects
        self.pulse_amount = 0
        self.pulse_speed = 2.0
    
    def initialize(self, board_state):
        """Initialize power-ups on the board"""
        self.board_state = board_state
        self.power_ups = {}
        
        # Generate power-ups in empty cells
        empty_cells = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                if board_state[row][col] is None:
                    empty_cells.append((row, col))
        
        # Calculate number of power-ups to generate
        num_power_ups = int(len(empty_cells) * self.frequency * 0.15)
        
        # Place power-ups randomly
        if empty_cells:
            cells_for_power_ups = random.sample(empty_cells, min(num_power_ups, len(empty_cells)))
            
            for row, col in cells_for_power_ups:
                # Select random power-up type
                power_up_type = random.choice([typ for typ, _ in self.power_up_types])
                self.power_ups[(row, col)] = power_up_type
    
    def update(self, dt):
        """Update animation effects"""
        self.pulse_amount = (self.pulse_amount + self.pulse_speed * dt) % (2 * math.pi)
    
    def render(self, screen, board_offset, cell_size):
        """Render power-ups on the board"""
        # Draw each power-up
        for (row, col), power_up_type in self.power_ups.items():
            # Calculate position
            x = board_offset[0] + col * cell_size + cell_size // 2
            y = board_offset[1] + row * cell_size + cell_size // 2
            
            # Get power-up color
            color = next((clr for typ, clr in self.power_up_types if typ == power_up_type), 
                       (255, 255, 255))
            
            # Draw power-up with pulsing effect
            size = cell_size // 3
            pulse = abs(math.sin(self.pulse_amount)) * 0.3 + 0.7
            size_with_pulse = int(size * pulse)
            
            # Draw outer glow
            pygame.draw.circle(screen, color, (x, y), size_with_pulse + 2)
            
            # Draw power-up symbol
            if power_up_type == "extra_move":
                # Star shape for extra move
                points = []
                for i in range(5):
                    angle = math.pi * 2 * i / 5 - math.pi / 2
                    points.append((
                        x + size_with_pulse * math.cos(angle),
                        y + size_with_pulse * math.sin(angle)
                    ))
                pygame.draw.polygon(screen, WHITE, points)
            
            elif power_up_type == "extra_time":
                # Clock shape for extra time
                pygame.draw.circle(screen, WHITE, (x, y), size_with_pulse * 0.8)
                # Clock hands
                hand_length = size_with_pulse * 0.6
                pygame.draw.line(screen, color, 
                              (x, y), 
                              (x + hand_length * 0.5, y - hand_length * 0.5), 
                              2)
                pygame.draw.line(screen, color, 
                              (x, y), 
                              (x, y - hand_length), 
                              2)
            
            elif power_up_type == "shield":
                # Shield shape
                pygame.draw.circle(screen, WHITE, (x, y), size_with_pulse * 0.8)
                # Cross symbol
                line_length = size_with_pulse * 0.5
                pygame.draw.line(screen, color, 
                             (x - line_length, y), 
                             (x + line_length, y), 
                             3)
                pygame.draw.line(screen, color, 
                             (x, y - line_length), 
                             (x, y + line_length), 
                             3)
            
            elif power_up_type == "double_piece":
                # Double piece symbol (two overlapping circles)
                offset = size_with_pulse * 0.4
                pygame.draw.circle(screen, WHITE, (x - offset, y - offset), size_with_pulse * 0.6)
                pygame.draw.circle(screen, WHITE, (x + offset, y + offset), size_with_pulse * 0.6)
    
    def get_power_up_at(self, row, col):
        """Get power-up type at the specified position, or None if no power-up"""
        return self.power_ups.get((row, col))
    
    def remove_power_up(self, row, col):
        """Remove power-up at the specified position"""
        if (row, col) in self.power_ups:
            del self.power_ups[(row, col)]
    
    def get_power_up_types(self):
        """Get list of power-up types and colors for legend"""
        return self.power_up_types

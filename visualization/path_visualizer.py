import pygame
import math

class PathVisualizer:
    def __init__(self):
        self.animation_timer = 0
        self.animation_speed = 1.0  # Animation cycles per second
    
    def update(self, dt):
        """Update animation timers"""
        self.animation_timer = (self.animation_timer + dt * self.animation_speed) % 1.0
    
    def render_path(self, screen, path, grid_to_pixel_func, color=(100, 100, 255), line_width=3):
        """
        Render a path with animated effect
        
        Args:
            screen: pygame surface to draw on
            path: list of (x, y) tuples representing the path
            grid_to_pixel_func: function to convert grid coordinates to pixel coordinates
            color: RGB color for the path
            line_width: width of the path line
        """
        if not path or len(path) < 2:
            return
        
        # Convert path to pixel coordinates
        pixel_path = [grid_to_pixel_func(x, y) for x, y in path]
        
        # Draw path segments
        for i in range(len(pixel_path) - 1):
            start = pixel_path[i]
            end = pixel_path[i + 1]
            
            # Calculate progress through path for animation
            path_progress = (i + self.animation_timer) / len(pixel_path)
            
            # Modify color based on progress
            r = int(color[0] * (0.7 + 0.3 * math.sin(path_progress * math.pi * 2)))
            g = int(color[1] * (0.7 + 0.3 * math.sin(path_progress * math.pi * 2 + 2)))
            b = int(color[2] * (0.7 + 0.3 * math.sin(path_progress * math.pi * 2 + 4)))
            segment_color = (r, g, b)
            
            # Draw line segment
            pygame.draw.line(screen, segment_color, start, end, line_width)
        
        # Draw nodes at each point
        for point in pixel_path:
            pygame.draw.circle(screen, color, point, line_width + 1)
    
    def render_visited(self, screen, visited, grid_to_pixel_func, base_color=(200, 200, 255)):
        """
        Render visited cells with subtle animation
        
        Args:
            screen: pygame surface to draw on
            visited: set of (x, y) tuples representing visited cells
            grid_to_pixel_func: function to convert grid coordinates to pixel coordinates
            base_color: RGB base color for visited cells
        """
        for x, y in visited:
            pixel_pos = grid_to_pixel_func(x, y)
            
            # Calculate unique animation phase for each cell based on position
            cell_phase = ((x * 0.37) + (y * 0.73) + self.animation_timer) % 1.0
            pulse = 0.7 + 0.3 * math.sin(cell_phase * math.pi * 2)
            
            # Apply pulse to color
            r = int(base_color[0] * pulse)
            g = int(base_color[1] * pulse)
            b = int(base_color[2] * pulse)
            cell_color = (r, g, b)
            
            # Draw a small circle at the cell position
            pygame.draw.circle(screen, cell_color, pixel_pos, 3)

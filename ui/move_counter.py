import pygame

class MoveCounter:
    def __init__(self, max_moves):
        self.max_moves = max_moves
        self.moves_left = max_moves
        self.font = pygame.font.SysFont(None, 32)
    
    def use_move(self):
        """Use a move and update the counter"""
        if self.moves_left > 0:
            self.moves_left -= 1
        return self.moves_left
    
    def reset(self, max_moves=None):
        """Reset move counter, optionally with a new max_moves"""
        if max_moves is not None:
            self.max_moves = max_moves
        self.moves_left = self.max_moves
    
    def render(self, screen, position):
        """Render the move counter"""
        # Draw background rect
        text = self.font.render(f"Moves Left: {self.moves_left}", True, (255, 255, 255))
        
        # Determine color based on moves left
        if self.moves_left > self.max_moves // 2:
            color = (0, 200, 0)  # Green
        elif self.moves_left > self.max_moves // 4:
            color = (255, 165, 0)  # Orange
        else:
            color = (255, 0, 0)  # Red
        
        # Draw move counter text
        rect = text.get_rect(center=position)
        pygame.draw.rect(screen, (50, 50, 50), 
                       (rect.left - 10, rect.top - 5, rect.width + 20, rect.height + 10))
        pygame.draw.rect(screen, color, 
                       (rect.left - 10, rect.top - 5, rect.width + 20, rect.height + 10), 2)
        screen.blit(text, rect)

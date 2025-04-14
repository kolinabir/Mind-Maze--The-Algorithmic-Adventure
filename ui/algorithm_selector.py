import pygame
from settings import WHITE, BLACK, BLUE, RED, GREEN, YELLOW, LIGHT_BLUE

class AlgorithmSelector:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 20)
        self.algorithms = [
            ("bfs", "BFS"),
            ("dfs", "DFS"),
            ("water_jug", "Water Jug"),
            ("minimax", "Minimax"),
            ("alpha_beta", "Alpha-Beta"),
            ("integration", "Integration")
        ]
        self.selected = None
        self.buttons = []
        self.hovered_button = None
    
    def set_active(self, algo_id):
        """Set the currently active algorithm"""
        self.selected = algo_id
    
    def get_selected(self):
        """Get the currently selected algorithm"""
        return self.selected
    
    def handle_event(self, event):
        """Handle interaction events"""
        if event.type == pygame.MOUSEMOTION:
            # Update hovering state
            self.hovered_button = None
            for algo_id, rect in self.buttons:
                if rect.collidepoint(event.pos):
                    self.hovered_button = algo_id
                    break
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Handle button click
            for algo_id, rect in self.buttons:
                if rect.collidepoint(event.pos):
                    if self.selected != algo_id:
                        self.selected = algo_id
                        return True  # Selection changed
                    break
        
        return False  # No change
    
    def render(self, screen, rect):
        """Render the algorithm selector"""
        # Draw background
        pygame.draw.rect(screen, (40, 40, 50), rect)
        pygame.draw.rect(screen, WHITE, rect, 1)
        
        # Draw label
        label = self.font.render("Select Algorithm:", True, WHITE)
        screen.blit(label, (rect.left + 10, rect.top + 5))
        
        # Calculate button layout
        button_width = 80
        button_height = 30
        button_spacing = 10
        total_width = len(self.algorithms) * (button_width + button_spacing) - button_spacing
        start_x = rect.left + (rect.width - total_width) // 2
        button_y = rect.top + rect.height - button_height - 5
        
        # Draw algorithm buttons
        self.buttons = []  # Reset button list
        for i, (algo_id, name) in enumerate(self.algorithms):
            button_x = start_x + i * (button_width + button_spacing)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Determine button color based on selection/hover state
            if algo_id == self.selected:
                color = GREEN
            elif algo_id == self.hovered_button:
                color = LIGHT_BLUE
            else:
                color = BLUE
            
            # Draw button
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, WHITE, button_rect, 1)
            
            # Draw algorithm name
            name_text = self.font.render(name, True, WHITE)
            name_rect = name_text.get_rect(center=button_rect.center)
            screen.blit(name_text, name_rect)
            
            # Store button for interaction handling
            self.buttons.append((algo_id, button_rect))

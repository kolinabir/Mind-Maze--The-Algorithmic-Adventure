import pygame
import math
from settings import WHITE, BLACK, BLUE, RED, GREEN, YELLOW, LIGHT_BLUE

class CompositeVisualizer:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 18)
        self.animation_timer = 0
        self.active_algorithm = None
    
    def update(self, dt, algorithm):
        """Update animation for the active algorithm"""
        self.animation_timer = (self.animation_timer + dt) % 1.0
        self.active_algorithm = algorithm
    
    def render_decision_tree(self, screen, rect, tree_data, algorithm_type):
        """Render minimax or alpha-beta decision tree"""
        # Draw background
        pygame.draw.rect(screen, (30, 30, 45), rect)
        pygame.draw.rect(screen, WHITE, rect, 1)
        
        # Draw title
        title = algorithm_type.upper() + " Decision Tree"
        title_text = self.font.render(title, True, WHITE)
        screen.blit(title_text, (rect.left + 10, rect.top + 5))
        
        # Draw tree nodes
        if tree_data:
            # Draw a simplified representation of the tree
            if algorithm_type == "minimax":
                self._draw_minimax_tree(screen, rect, tree_data)
            else:
                self._draw_alpha_beta_tree(screen, rect, tree_data)
    
    def _draw_minimax_tree(self, screen, rect, tree_data):
        """Draw a simplified minimax decision tree"""
        # Draw root node score
        root_score = tree_data.get('score', 0)
        score_text = self.font.render(f"Root Score: {root_score}", True, WHITE)
        screen.blit(score_text, (rect.left + 10, rect.top + 25))
        
        # Draw children nodes
        children = tree_data.get('children', [])
        if children:
            # Calculate layout
            node_width = 60
            total_width = min(len(children) * node_width, rect.width - 20)
            start_x = rect.left + (rect.width - total_width) // 2
            
            # Draw child nodes
            for i, child in enumerate(children[:int(rect.width // node_width)]):
                node_x = start_x + i * node_width
                node_y = rect.top + 45
                
                # Draw node
                node_color = BLUE if child.get('is_maximizing', False) else RED
                pygame.draw.circle(screen, node_color, (node_x + node_width // 2, node_y), 10)
                
                # Draw score
                score = child.get('score', 0)
                score_text = self.font.render(str(score), True, WHITE)
                screen.blit(score_text, (node_x + node_width // 2 - score_text.get_width() // 2, node_y + 15))
    
    def _draw_alpha_beta_tree(self, screen, rect, tree_data):
        """Draw alpha-beta pruning stats"""
        # Draw stats
        stats = [
            f"Nodes Evaluated: {tree_data.get('total_nodes', 0)}",
            f"Nodes Pruned: {tree_data.get('pruned_nodes', 0)}",
            f"Time Taken: {tree_data.get('time_taken', 0):.3f}s"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.font.render(stat, True, WHITE)
            screen.blit(stat_text, (rect.left + 10, rect.top + 25 + i * 20))
        
        # Draw pruning visualization
        events = tree_data.get('pruning_events', [])
        if events:
            # Show pruning example
            event = events[0]
            
            # Draw alpha-beta range
            range_rect = pygame.Rect(rect.right - 150, rect.top + 25, 130, 20)
            pygame.draw.rect(screen, (50, 50, 50), range_rect)
            
            # Draw alpha marker
            alpha = event.get('alpha', -10)
            alpha_x = range_rect.left + int((alpha + 10) / 20 * range_rect.width)
            pygame.draw.line(screen, RED, (alpha_x, range_rect.top), (alpha_x, range_rect.bottom), 2)
            
            # Draw beta marker
            beta = event.get('beta', 10)
            beta_x = range_rect.left + int((beta + 10) / 20 * range_rect.width)
            pygame.draw.line(screen, BLUE, (beta_x, range_rect.top), (beta_x, range_rect.bottom), 2)
            
            # Draw pruning text
            prune_text = self.font.render("Pruning occurs when α ≥ β", True, YELLOW)
            screen.blit(prune_text, (rect.right - 150, rect.top + 50))
    
    def render_pruning(self, screen, rect, pruning_data):
        """Render alpha-beta pruning visualization"""
        # Draw background
        pygame.draw.rect(screen, (30, 30, 45), rect)
        pygame.draw.rect(screen, WHITE, rect, 1)
        
        # Draw title
        title_text = self.font.render("Alpha-Beta Pruning Statistics", True, WHITE)
        screen.blit(title_text, (rect.left + 10, rect.top + 5))
        
        # Draw statistics
        stats = [
            f"Nodes Evaluated: {pruning_data.get('total_nodes', 0)}",
            f"Nodes Pruned: {pruning_data.get('pruned_nodes', 0)}",
            f"Efficiency: {int(pruning_data.get('pruned_nodes', 0) / max(pruning_data.get('total_nodes', 1), 1) * 100)}%",
            f"Branching Factor: {pruning_data.get('branching_factor', 0):.1f}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.font.render(stat, True, WHITE)
            y_pos = rect.top + 25 + i * 18
            screen.blit(stat_text, (rect.left + 10, y_pos))
        
        # Draw efficiency meter
        efficiency = pruning_data.get('pruned_nodes', 0) / max(pruning_data.get('total_nodes', 1), 1)
        meter_rect = pygame.Rect(rect.right - 150, rect.top + 25, 130, 20)
        pygame.draw.rect(screen, (50, 50, 50), meter_rect)
        pygame.draw.rect(screen, GREEN, (meter_rect.left, meter_rect.top, int(meter_rect.width * efficiency), meter_rect.height))
        pygame.draw.rect(screen, WHITE, meter_rect, 1)
        
        meter_text = self.font.render("Pruning Efficiency", True, WHITE)
        screen.blit(meter_text, (rect.right - 150, rect.top + 50))

import pygame
import math

class DecisionTreeVisualizer:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 14)
        self.animation_timer = 0
        self.animation_speed = 0.5  # Animation speed in cycles per second
        self.max_width = 0
        self.max_height = 0
    
    def update(self, dt):
        """Update animation"""
        self.animation_timer = (self.animation_timer + dt * self.animation_speed) % 1.0
    
    def render(self, screen, rect, decision_tree):
        """
        Render the decision tree visualization
        
        Args:
            screen: Pygame surface to draw on
            rect: Rectangle defining the visualization area
            decision_tree: Decision tree data from Minimax AI
        """
        # Draw background
        pygame.draw.rect(screen, (20, 20, 40), rect)
        pygame.draw.rect(screen, (200, 200, 200), rect, 2)
        
        # Draw title
        title = "Minimax Decision Tree"
        title_font = pygame.font.SysFont(None, 24)
        title_surf = title_font.render(title, True, (255, 255, 255))
        title_rect = title_surf.get_rect(midtop=(rect.centerx, rect.top + 5))
        screen.blit(title_surf, title_rect)
        
        # Calculate layout
        self._calculate_layout(decision_tree, rect)
        
        # Draw tree connections first
        self._draw_connections(screen, decision_tree, rect)
        
        # Then draw nodes on top
        self._draw_nodes(screen, decision_tree, rect)
        
        # Draw explanation
        self._draw_explanation(screen, rect)
    
    def _calculate_layout(self, tree, rect):
        """Calculate positions for each node in the tree"""
        # Get tree depth and number of leaf nodes
        max_depth, leaf_count = self._get_tree_dimensions(tree)
        
        # Reserve space at the top for title
        y_offset = 30
        
        # Calculate available space
        available_width = rect.width - 20  # 10px padding on each side
        available_height = rect.height - y_offset - 10  # 10px padding at bottom
        
        # Calculate spacing
        self.h_spacing = available_width / max(leaf_count, 1)
        self.v_spacing = available_height / max(max_depth, 1)
        
        # Calculate positions for each node
        self._assign_positions(tree, rect.left + 10, rect.top + y_offset, 0, 0, leaf_count)
    
    def _get_tree_dimensions(self, tree, depth=0):
        """Get dimensions of the tree (max depth and leaf count)"""
        if not tree['children']:
            return depth, 1
        
        max_depth = 0
        leaf_count = 0
        
        for child in tree['children']:
            child_depth, child_leaves = self._get_tree_dimensions(child, depth + 1)
            max_depth = max(max_depth, child_depth)
            leaf_count += child_leaves
        
        return max_depth, leaf_count
    
    def _assign_positions(self, node, x_base, y, depth, leaf_offset, total_leaves):
        """Recursively assign positions to tree nodes"""
        if not node['children']:
            # Leaf node - position based on leaf offset
            width_per_leaf = self.h_spacing
            node['x'] = x_base + (leaf_offset + 0.5) * width_per_leaf
            node['y'] = y + depth * self.v_spacing
            return leaf_offset + 1
        
        # Position children first, then position this node above them
        current_leaf_offset = leaf_offset
        child_x_positions = []
        
        for child in node['children']:
            current_leaf_offset = self._assign_positions(
                child, x_base, y, depth + 1, current_leaf_offset, total_leaves)
            child_x_positions.append(child['x'])
        
        # Position this node centered above its children
        if child_x_positions:
            node['x'] = sum(child_x_positions) / len(child_x_positions)
        else:
            node['x'] = x_base + (leaf_offset + 0.5) * self.h_spacing
            
        node['y'] = y + depth * self.v_spacing
        
        return current_leaf_offset
    
    def _draw_nodes(self, screen, tree, rect, depth=0):
        """Draw tree nodes recursively"""
        # Get color based on maximizing/minimizing and score
        if tree['score'] is not None:
            if tree['is_maximizing']:
                # Maximizing nodes (AI) - blue gradient based on score
                score_ratio = min(max((tree['score'] + 10) / 20, 0), 1)  # Normalize to 0-1
                color = (50, 50, 200 + int(score_ratio * 55))
            else:
                # Minimizing nodes (player) - red gradient based on score
                score_ratio = min(max((tree['score'] + 10) / 20, 0), 1)  # Normalize to 0-1
                color = (200 + int((1-score_ratio) * 55), 50, 50)
        else:
            color = (100, 100, 100)  # Neutral gray for nodes with no score
        
        # Highlight the best move at the current level
        is_best = False
        if depth == 0 and tree['children']:
            best_score = max(child['score'] for child in tree['children']) if tree['is_maximizing'] else min(child['score'] for child in tree['children'])
            best_children = [child for child in tree['children'] if child['score'] == best_score]
            for child in best_children:
                child['is_best'] = True
        
        # Draw node
        node_radius = 15
        pygame.draw.circle(screen, color, (tree['x'], tree['y']), node_radius)
        
        # Draw score in node
        if tree['score'] is not None:
            score_text = self.font.render(str(tree['score']), True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(tree['x'], tree['y']))
            screen.blit(score_text, score_rect)
        
        # Draw move label if exists
        if tree['move'] is not None:
            move_text = self.font.render(f"{tree['move'][0]},{tree['move'][1]}", True, (255, 255, 255))
            move_rect = move_text.get_rect(center=(tree['x'], tree['y'] - node_radius - 10))
            screen.blit(move_text, move_rect)
        
        # Draw highlight for best move
        if hasattr(tree, 'is_best') and tree['is_best']:
            # Animated highlight
            highlight_radius = node_radius + 3 + 2 * math.sin(self.animation_timer * 2 * 3.14159)
            pygame.draw.circle(screen, (255, 255, 0), (tree['x'], tree['y']), highlight_radius, 2)
        
        # Recursively draw children
        for child in tree['children']:
            self._draw_nodes(screen, child, rect, depth+1)
    
    def _draw_connections(self, screen, tree, rect, depth=0):
        """Draw connections between nodes"""
        for child in tree['children']:
            # Draw line from this node to child
            pygame.draw.line(
                screen, 
                (150, 150, 150),
                (tree['x'], tree['y']),
                (child['x'], child['y']),
                2
            )
            
            # Recursively draw connections to grandchildren
            self._draw_connections(screen, child, rect, depth+1)
    
    def _draw_explanation(self, screen, rect):
        """Draw textual explanation of the visualization"""
        explanation = [
            "Blue nodes: AI (maximizing)",
            "Red nodes: Player (minimizing)",
            "Numbers: Scores (higher is better for AI)",
            "Yellow border: Best move"
        ]
        
        y_pos = rect.bottom - 60
        for line in explanation:
            text = self.font.render(line, True, (200, 200, 200))
            screen.blit(text, (rect.left + 10, y_pos))
            y_pos += 15

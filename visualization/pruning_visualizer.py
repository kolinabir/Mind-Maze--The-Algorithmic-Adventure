import pygame
import math
from settings import WHITE, BLACK, BLUE, RED, GREEN, GRAY, YELLOW


class PruningVisualizer:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 18)
        self.title_font = pygame.font.SysFont(None, 24)
        self.animation_timer = 0
        self.animation_speed = 0.5  # Animation speed in cycles per second

    def update(self, dt):
        """Update animation"""
        self.animation_timer = (self.animation_timer + dt * self.animation_speed) % 1.0

    def render(self, screen, rect, pruning_data):
        """
        Render visualization of alpha-beta pruning

        Args:
            screen: Pygame surface to draw on
            rect: Rectangle defining the visualization area
            pruning_data: Dictionary with pruning statistics
        """
        # Draw background
        pygame.draw.rect(screen, (20, 30, 40), rect)
        pygame.draw.rect(screen, WHITE, rect, 2)

        # Draw title
        title = "Alpha-Beta Pruning Visualization"
        title_surf = self.title_font.render(title, True, WHITE)
        title_rect = title_surf.get_rect(midtop=(rect.centerx, rect.top + 5))
        screen.blit(title_surf, title_rect)

        # Draw statistics on left side
        self._draw_statistics(screen, rect, pruning_data)

        # Draw pruning events visualization on right side
        self._draw_pruning_events(screen, rect, pruning_data)

        # Draw explanation
        self._draw_explanation(screen, rect)

    def _draw_statistics(self, screen, rect, data):
        """Draw pruning statistics"""
        stats_x = rect.left + 10
        stats_y = rect.top + 35
        line_height = 20

        efficiency = 0
        if data["total_nodes"] > 0:
            efficiency = (data["pruned_nodes"] / data["total_nodes"]) * 100

        stats = [
            f"Total Nodes: {data['total_nodes']}",
            f"Pruned Nodes: {data['pruned_nodes']}",
            f"Pruning Efficiency: {efficiency:.1f}%",
            f"Max Depth Reached: {data['max_depth_reached']}",
            f"Time Taken: {data['time_taken']:.3f}s",
            f"Branching Factor: {data['branching_factor']:.1f}",
        ]

        for i, stat in enumerate(stats):
            text_surf = self.font.render(stat, True, WHITE)
            screen.blit(text_surf, (stats_x, stats_y + i * line_height))

    def _draw_pruning_events(self, screen, rect, data):
        """Draw visual representation of pruning events"""
        events = data.get("pruning_events", [])
        if not events:
            text = self.font.render("No pruning events to display", True, WHITE)
            screen.blit(text, (rect.centerx + 100, rect.centery))
            return

        # Available space for drawing
        viz_rect = pygame.Rect(
            rect.centerx + 20,  # Start from middle of container
            rect.top + 35,  # Same y-position as stats
            rect.right - rect.centerx - 30,  # Width is half of container minus margins
            rect.height - 45,  # Height is container height minus margins
        )

        # Draw pruning visualization title
        viz_title = self.font.render("Pruning Events:", True, WHITE)
        screen.blit(viz_title, (viz_rect.left, viz_rect.top - 5))

        # Draw the pruning events as a tree-like structure
        self._draw_pruning_tree(screen, viz_rect, events)

    def _draw_pruning_tree(self, screen, rect, events):
        """Draw the pruning events as a tree-like structure"""
        # Calculate space per event
        max_height = rect.height - 20
        event_height = max_height / max(len(events), 1)

        # For each pruning event
        for i, event in enumerate(events):
            # Determine position
            y_pos = rect.top + 15 + i * event_height

            # Calculate width of the alpha-beta range bar
            alpha = event["alpha"]
            beta = event["beta"]
            value = event["value"]

            # Normalize values to the visualization range
            bar_width = rect.width - 100  # Leave space for labels

            # Restrict range to reasonable values for visualization
            min_val = -100
            max_val = 100

            # Normalize alpha and beta to [0, 1] for drawing
            norm_alpha = (min(max(alpha, min_val), max_val) - min_val) / (
                max_val - min_val
            )
            norm_beta = (min(max(beta, min_val), max_val) - min_val) / (
                max_val - min_val
            )
            norm_value = (min(max(value, min_val), max_val) - min_val) / (
                max_val - min_val
            )

            # Draw alpha-beta range background
            range_left = rect.left + int(norm_alpha * bar_width)
            range_right = rect.left + int(norm_beta * bar_width)
            range_height = 20

            # Draw range bar
            pygame.draw.rect(screen, GRAY, (rect.left, y_pos, bar_width, range_height))

            # Draw actual alpha-beta range
            if norm_alpha < norm_beta:  # Valid range
                pygame.draw.rect(
                    screen,
                    GREEN if event["is_maximizing"] else BLUE,
                    (range_left, y_pos, range_right - range_left, range_height),
                )
            else:  # Pruning occurred - invalid range
                # Animate the pruning event
                prune_color = RED
                if self.animation_timer > 0.5:
                    # Pulse effect for pruning
                    pulse = (1.0 - 2 * (self.animation_timer - 0.5)) * 0.3
                    r = min(255, int(prune_color[0] * (1 + pulse)))
                    g = min(255, int(prune_color[1] * (1 + pulse)))
                    b = min(255, int(prune_color[2] * (1 + pulse)))
                    prune_color = (r, g, b)

                pygame.draw.rect(
                    screen,
                    prune_color,
                    (range_right, y_pos, range_left - range_right, range_height),
                )

            # Draw alpha marker
            pygame.draw.line(
                screen, RED, (range_left, y_pos), (range_left, y_pos + range_height), 2
            )

            # Draw beta marker
            pygame.draw.line(
                screen,
                BLUE,
                (range_right, y_pos),
                (range_right, y_pos + range_height),
                2,
            )

            # Draw value marker
            value_x = rect.left + int(norm_value * bar_width)
            pygame.draw.line(
                screen,
                WHITE,
                (value_x, y_pos - 3),
                (value_x, y_pos + range_height + 3),
                2,
            )

            # Draw labels
            depth_text = self.font.render(f"Depth: {event['depth']}", True, WHITE)
            screen.blit(depth_text, (rect.left, y_pos - 18))

            alpha_text = self.font.render(f"α:{alpha:.1f}", True, RED)
            screen.blit(alpha_text, (range_left - 15, y_pos + range_height + 3))

            beta_text = self.font.render(f"β:{beta:.1f}", True, BLUE)
            screen.blit(beta_text, (range_right - 15, y_pos + range_height + 3))

            value_text = self.font.render(f"v:{value:.1f}", True, WHITE)
            screen.blit(value_text, (value_x - 15, y_pos - 18))

            # Draw player indicator
            player_text = self.font.render(
                "MAX" if event["is_maximizing"] else "MIN",
                True,
                GREEN if event["is_maximizing"] else BLUE,
            )
            screen.blit(player_text, (rect.left + bar_width + 10, y_pos + 2))

            # Connect events with lines to show tree structure
            if i > 0:
                prev_y = rect.top + 15 + (i - 1) * event_height + range_height / 2
                curr_y = y_pos + range_height / 2
                mid_x = rect.left + bar_width + 30

                # Draw connection lines
                pygame.draw.line(
                    screen,
                    GRAY,
                    (rect.left + bar_width + 5, prev_y),
                    (mid_x, prev_y),
                    1,
                )
                pygame.draw.line(screen, GRAY, (mid_x, prev_y), (mid_x, curr_y), 1)
                pygame.draw.line(
                    screen,
                    GRAY,
                    (mid_x, curr_y),
                    (rect.left + bar_width + 5, curr_y),
                    1,
                )

    def _draw_explanation(self, screen, rect):
        """Draw textual explanation of the visualization"""
        explanation_text = [
            "Alpha-Beta Pruning Visualization:",
            "• RED lines (α): Best score for MAX player",
            "• BLUE lines (β): Best score for MIN player",
            "• WHITE lines (v): Current position value",
            "• GREEN/BLUE area: Valid search range",
            "• RED highlight: Pruning (α ≥ β)",
            "• Tree shows how many branches were eliminated",
        ]

        # Draw explanation panel
        exp_rect = pygame.Rect(rect.left, rect.bottom - 100, rect.width, 90)
        pygame.draw.rect(screen, (40, 40, 40, 150), exp_rect)
        pygame.draw.rect(screen, WHITE, exp_rect, 1)

        # Draw text
        y_offset = exp_rect.top + 5
        for line in explanation_text:
            text = self.font.render(line, True, WHITE)
            screen.blit(text, (exp_rect.left + 10, y_offset))
            y_offset += 20

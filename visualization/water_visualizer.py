import pygame
import math
import random


class WaterVisualizer:
    def __init__(self):
        self.wave_offset = 0
        self.wave_speed = 1.5
        self.wave_height = 3
        self.water_color = (0, 120, 255, 220)
        self.highlights = []
        self.bubbles = []

    def update(self, dt):
        """Update water animation"""
        # Update wave animation
        self.wave_offset = (self.wave_offset + dt * self.wave_speed) % (math.pi * 2)

        # Update bubbles
        self._update_bubbles(dt)

    def draw_jug(
        self,
        screen,
        rect,
        capacity,
        amount,
        pour_progress,
        pour_amount,
        is_source,
        is_target,
        border_color,
        border_width,
    ):
        """
        Draw a water jug with animated water

        Args:
            screen: Pygame surface to draw on
            rect: Rectangle defining the jug position and size
            capacity: Maximum capacity of the jug
            amount: Current amount in the jug
            pour_progress: Animation progress for pouring (0-1)
            pour_amount: Amount being poured in/out
            is_source: Whether this jug is the source of pouring
            is_target: Whether this jug is the target of pouring
            border_color: Color for jug border
            border_width: Width of jug border
        """
        # Draw jug body
        pygame.draw.rect(screen, (50, 50, 50), rect)
        pygame.draw.rect(screen, border_color, rect, border_width)

        # Calculate water level
        water_level = 0
        display_amount = amount
        water_height = 0

        # Adjust amount for animation
        if is_source and pour_progress > 0:
            display_amount = amount - (pour_amount * pour_progress)
        elif is_target and pour_progress > 0:
            display_amount = amount + (pour_amount * pour_progress)

        if capacity > 0:
            fill_ratio = display_amount / capacity
            water_height = int(rect.height * fill_ratio)
            water_level = rect.bottom - water_height

        # Draw water if there is any
        if water_height > 0:
            # Draw water waves
            points = []

            # Bottom left corner
            points.append((rect.left, rect.bottom))

            # Bottom right corner
            points.append((rect.right, rect.bottom))

            # Top right with waves
            points.append((rect.right, water_level))

            # Generate wave points across top of water
            wave_points = 12
            for i in range(wave_points):
                x = rect.right - (i * rect.width / (wave_points - 1))
                # Add wave effect
                wave = math.sin(self.wave_offset + i * 0.5) * self.wave_height
                y = water_level + wave
                points.append((x, y))

            # Top left with waves
            points.append((rect.left, water_level))

            # Draw filled water polygon
            pygame.draw.polygon(screen, self.water_color, points)

            # Draw water line on top
            wave_line = []
            for i in range(wave_points):
                x = rect.left + (i * rect.width / (wave_points - 1))
                wave = math.sin(self.wave_offset + i * 0.5) * self.wave_height
                y = water_level + wave
                wave_line.append((x, y))

            pygame.draw.lines(screen, (255, 255, 255, 80), False, wave_line, 2)

            # Generate random bubbles occasionally
            if (
                random.random() < 0.02 and water_height > 10
            ):  # Only add bubbles if there's enough water
                bubble_x = random.randint(rect.left + 5, rect.right - 5)
                # Fix the empty range error by ensuring valid range
                if water_level + 5 < rect.bottom - 5:
                    bubble_y = random.randint(water_level + 5, rect.bottom - 5)
                    bubble_size = random.randint(2, 4)
                    bubble_speed = random.uniform(15, 25)
                    self.bubbles.append(
                        {
                            "x": bubble_x,
                            "y": bubble_y,
                            "size": bubble_size,
                            "speed": bubble_speed,
                            "jug_rect": rect,
                            "water_level": water_level,
                        }
                    )

            # Draw bubbles
            self._draw_bubbles(screen)

        # Draw pouring animation
        if (is_source or is_target) and pour_progress > 0 and pour_progress < 1:
            if is_source:
                self._draw_pouring(screen, rect, water_level, True, pour_progress)
            elif is_target:
                self._draw_pouring(screen, rect, water_level, False, pour_progress)

    def _draw_pouring(self, screen, rect, water_level, is_out, progress):
        """Draw water pouring in or out animation"""
        if is_out:
            # Pouring out from the jug
            start_x = rect.centerx
            start_y = water_level

            # Stream goes down and to the right
            stream_length = 60
            end_x = start_x + stream_length
            end_y = start_y + stream_length

            # Draw arc for pouring
            rect_size = 80
            pygame.draw.arc(
                screen,
                self.water_color,
                (
                    start_x - rect_size // 2,
                    start_y - rect_size // 2,
                    rect_size,
                    rect_size * 2,
                ),
                math.pi * 1.5,
                math.pi * 2,
                3,
            )

            # Draw stream particles
            for i in range(10):
                particle_progress = (progress + i * 0.1) % 1.0
                x = start_x + (end_x - start_x) * particle_progress
                y = start_y + (end_y - start_y) * particle_progress

                # Particles get smaller at the end
                size = 6 * (1 - particle_progress)

                pygame.draw.circle(
                    screen, self.water_color, (int(x), int(y)), int(size)
                )
        else:
            # Pouring into the jug
            end_x = rect.centerx
            end_y = water_level

            # Stream comes from above
            stream_length = 60
            start_x = end_x - stream_length // 2
            start_y = end_y - stream_length

            # Draw stream particles
            for i in range(10):
                particle_progress = (progress + i * 0.1) % 1.0
                x = start_x + (end_x - start_x) * particle_progress
                y = start_y + (end_y - start_y) * particle_progress

                # Particles get smaller at the beginning
                size = 6 * particle_progress

                pygame.draw.circle(
                    screen, self.water_color, (int(x), int(y)), int(size)
                )

    def _update_bubbles(self, dt):
        """Update bubble positions and remove ones that reach the top"""
        for bubble in self.bubbles[:]:
            bubble["y"] -= bubble["speed"] * dt

            # Remove bubbles that reach the water surface
            if bubble["y"] <= bubble["water_level"] or not bubble[
                "jug_rect"
            ].collidepoint(bubble["x"], bubble["y"]):
                self.bubbles.remove(bubble)

    def _draw_bubbles(self, screen):
        """Draw bubbles in the water"""
        for bubble in self.bubbles:
            pygame.draw.circle(
                screen,
                (255, 255, 255, 128),
                (int(bubble["x"]), int(bubble["y"])),
                bubble["size"],
            )
            # Highlight in bubbles
            pygame.draw.circle(
                screen,
                (255, 255, 255, 180),
                (
                    int(bubble["x"] - bubble["size"] // 3),
                    int(bubble["y"] - bubble["size"] // 3),
                ),
                bubble["size"] // 2,
            )

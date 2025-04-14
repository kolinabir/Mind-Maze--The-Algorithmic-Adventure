import pygame
import math
from levels.base_level import BaseLevel
from algorithms.jug_problem import JugSolver
from visualization.water_visualizer import WaterVisualizer
from ui.move_counter import MoveCounter
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, BLUE, GREEN, RED


class JugLevel(BaseLevel):
    def __init__(self, game_engine, asset_manager):
        super().__init__(game_engine, asset_manager)

        # Default puzzle setup
        self.difficulty = 1

        # Create move counter first
        self.max_moves = 8  # Default value that will be updated in set_difficulty
        self.move_counter = MoveCounter(self.max_moves)

        # Now it's safe to set difficulty which will update max_moves
        self.set_difficulty(self.difficulty)

        # Initialize jugs with empty state
        self.jugs = [0] * len(self.capacities)

        # Visualization
        self.visualizer = WaterVisualizer()

        # Jug selection state
        self.selected_jug = None

        # Animation state
        self.is_pouring = False
        self.pour_source = None
        self.pour_target = None
        self.pour_amount = 0
        self.pour_progress = 0
        self.pour_speed = 2.0  # Speed of pouring animation

        # Button areas for jugs
        self.jug_buttons = []
        self.update_jug_buttons()

        # Action button areas (Fill, Empty, Pour)
        self.action_buttons = []
        self.update_action_buttons()

        # Hint button
        self.hint_button = pygame.Rect(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 50, 100, 40)
        self.hint_active = False
        self.hint_steps = []
        self.hint_index = 0

        # Help text
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 36)

        # Solver for hints
        self.solver = JugSolver()

        # Win/lose state
        self.win = False
        self.lose = False

    def set_difficulty(self, level):
        """Configure puzzle based on difficulty level"""
        self.difficulty = level

        # Difficulty presets
        if level == 1:
            # Classic 3,5 to get 4 liters
            self.capacities = [3, 5]
            self.target_amount = 4
            self.max_moves = 8
        elif level == 2:
            # 3 jugs with medium complexity
            self.capacities = [5, 3, 8]
            self.target_amount = 4
            self.max_moves = 10
        elif level == 3:
            # More complex with 3 jugs
            self.capacities = [8, 5, 3]
            self.target_amount = 7
            self.max_moves = 12
        else:  # level 4 or higher
            # Very challenging
            self.capacities = [12, 7, 5, 3]
            self.target_amount = 10
            self.max_moves = 15

        # Reset state when changing difficulty
        self.jugs = [0] * len(self.capacities)
        self.win = False
        self.lose = False
        self.move_counter.reset(self.max_moves)
        self.selected_jug = None
        self.is_pouring = False
        self.hint_active = False
        self.hint_steps = []

    def update_jug_buttons(self):
        """Update clickable areas for jugs"""
        self.jug_buttons = []

        jug_width = 80
        total_width = len(self.capacities) * (jug_width + 20)
        start_x = (SCREEN_WIDTH - total_width) // 2 + jug_width // 2

        for i in range(len(self.capacities)):
            button_rect = pygame.Rect(
                start_x + i * (jug_width + 20) - jug_width // 2,
                SCREEN_HEIGHT // 2 - 100,
                jug_width,
                180,
            )
            self.jug_buttons.append(button_rect)

    def update_action_buttons(self):
        """Update clickable areas for actions"""
        self.action_buttons = []

        button_width = 100
        button_height = 40
        spacing = 20
        start_y = SCREEN_HEIGHT - 120

        # Fill button
        fill_rect = pygame.Rect(
            (SCREEN_WIDTH - button_width * 3 - spacing * 2) // 2,
            start_y,
            button_width,
            button_height,
        )
        self.action_buttons.append(("Fill", fill_rect))

        # Empty button
        empty_rect = pygame.Rect(
            fill_rect.right + spacing, start_y, button_width, button_height
        )
        self.action_buttons.append(("Empty", empty_rect))

        # Pour button
        pour_rect = pygame.Rect(
            empty_rect.right + spacing, start_y, button_width, button_height
        )
        self.action_buttons.append(("Pour", pour_rect))

    def handle_event(self, event):
        """Handle pygame events"""
        if self.is_pouring or self.win or self.lose:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if a jug was clicked
            for i, rect in enumerate(self.jug_buttons):
                if rect.collidepoint(event.pos):
                    self.selected_jug = i if self.selected_jug != i else None
                    break

            # Check if an action button was clicked
            if self.selected_jug is not None:
                for action, rect in self.action_buttons:
                    if rect.collidepoint(event.pos):
                        self.perform_action(action)
                        break

            # Check if hint button was clicked
            if self.hint_button.collidepoint(event.pos):
                self.toggle_hint()

    def perform_action(self, action):
        """Perform selected action on selected jug"""
        if action == "Fill":
            if self.jugs[self.selected_jug] < self.capacities[self.selected_jug]:
                # Start fill animation
                self.is_pouring = True
                self.pour_source = None  # Fill from "tap"
                self.pour_target = self.selected_jug
                self.pour_amount = (
                    self.capacities[self.selected_jug] - self.jugs[self.selected_jug]
                )
                self.pour_progress = 0

        elif action == "Empty":
            if self.jugs[self.selected_jug] > 0:
                # Start empty animation
                self.is_pouring = True
                self.pour_source = self.selected_jug
                self.pour_target = None  # Empty to "drain"
                self.pour_amount = self.jugs[self.selected_jug]
                self.pour_progress = 0

        elif action == "Pour":
            # Need to select another jug to pour into
            self.select_pour_target()

    def select_pour_target(self):
        """Show UI to select target jug for pouring"""
        # Future implementation: will add UI to select which jug to pour into
        # For now, we'll use simple approach: select next jug that has space
        source = self.selected_jug
        for i in range(len(self.jugs)):
            if i != source and self.jugs[i] < self.capacities[i]:
                self.start_pour(source, i)
                break

    def start_pour(self, source, target):
        """Start pouring from source jug to target jug"""
        if self.jugs[source] > 0:
            # Calculate amount to pour
            space_in_target = self.capacities[target] - self.jugs[target]
            amount = min(self.jugs[source], space_in_target)

            if amount > 0:
                # Start pour animation
                self.is_pouring = True
                self.pour_source = source
                self.pour_target = target
                self.pour_amount = amount
                self.pour_progress = 0

    def complete_action(self):
        """Complete the current pouring action"""
        # Update jug amounts after animation completes
        if self.pour_source is None:
            # Filling from "tap"
            self.jugs[self.pour_target] = self.capacities[self.pour_target]
        elif self.pour_target is None:
            # Emptying to "drain"
            self.jugs[self.pour_source] = 0
        else:
            # Pouring from one jug to another
            self.jugs[self.pour_source] -= self.pour_amount
            self.jugs[self.pour_target] += self.pour_amount

        # Reset animation state
        self.is_pouring = False

        # Count the move
        self.move_counter.use_move()

        # Check win/lose conditions
        self.check_game_state()

    def toggle_hint(self):
        """Toggle hint visibility"""
        if not self.hint_active:
            self.hint_active = True
            # Generate solution steps
            self.hint_steps = self.solver.solve(
                self.capacities, self.jugs.copy(), self.target_amount
            )
            self.hint_index = 0
        else:
            self.hint_active = False

    def check_game_state(self):
        """Check if the player has won or lost"""
        # Check for win condition - any jug contains target amount
        for amount in self.jugs:
            if amount == self.target_amount:
                self.win = True
                self.completed = True
                break

        # Check for lose condition - out of moves
        if self.move_counter.moves_left <= 0 and not self.win:
            self.lose = True

    def update(self, dt):
        """Update game logic"""
        # Update pour animation
        if self.is_pouring:
            self.pour_progress += dt * self.pour_speed
            if self.pour_progress >= 1.0:
                self.pour_progress = 1.0
                self.complete_action()

        # Update visualizer
        self.visualizer.update(dt)

    def render(self, screen):
        """Render the water jug puzzle"""
        # Fill background
        screen.fill((20, 20, 50))  # Dark blue background

        # Draw title and goal
        title = self.title_font.render(
            f"Water Jug Puzzle - Level {self.difficulty}", True, WHITE
        )
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        goal = self.font.render(
            f"Goal: Measure exactly {self.target_amount} liter(s) in any jug",
            True,
            WHITE,
        )
        screen.blit(goal, (SCREEN_WIDTH // 2 - goal.get_width() // 2, 70))

        # Draw move counter
        self.move_counter.render(screen, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))

        # Draw jugs
        self._draw_jugs(screen)

        # Draw action buttons
        self._draw_action_buttons(screen)

        # Draw hint button
        self._draw_hint_button(screen)

        # Draw hints if active
        if self.hint_active:
            self._draw_hints(screen)

        # Draw win/lose message
        if self.win:
            self._draw_completion_message(screen, True)
        elif self.lose:
            self._draw_completion_message(screen, False)

    def _draw_jugs(self, screen):
        """Draw the water jugs"""
        jug_width = 80
        jug_height = 160
        total_width = len(self.capacities) * (jug_width + 20)
        start_x = (SCREEN_WIDTH - total_width) // 2 + jug_width // 2

        for i, (capacity, amount) in enumerate(zip(self.capacities, self.jugs)):
            # Calculate jug position
            jug_x = start_x + i * (jug_width + 20)
            jug_y = SCREEN_HEIGHT // 2 - 20

            # Draw jug outline
            jug_rect = pygame.Rect(
                jug_x - jug_width // 2, jug_y - jug_height, jug_width, jug_height
            )

            # Check if jug is selected
            is_selected = i == self.selected_jug

            # Enhanced selection visual - add glow effect around selected jug
            if is_selected:
                # Draw outer glow
                glow_rect = jug_rect.inflate(12, 12)
                pygame.draw.rect(screen, (255, 255, 0), glow_rect, 0, border_radius=3)

                # Draw selection indicator above the jug
                indicator_height = 10
                indicator_rect = pygame.Rect(
                    jug_x - 15,
                    jug_y - jug_height - indicator_height - 8,
                    30,
                    indicator_height,
                )
                pygame.draw.rect(
                    screen, (255, 255, 0), indicator_rect, 0, border_radius=5
                )

                # Add "Selected" text above jug
                selected_text = self.font.render("Selected", True, (255, 255, 0))
                screen.blit(
                    selected_text,
                    (jug_x - selected_text.get_width() // 2, jug_y - jug_height - 30),
                )

                border_color = (255, 255, 0)  # Bright yellow for selected
                border_width = 3
            else:
                border_color = (200, 200, 200)  # Light gray for unselected
                border_width = 1

            # Let visualizer draw the jug and water
            self.visualizer.draw_jug(
                screen,
                jug_rect,
                capacity,
                amount,
                self.pour_progress if self.is_pouring else 0,
                (
                    self.pour_amount
                    if self.is_pouring
                    and (i == self.pour_source or i == self.pour_target)
                    else 0
                ),
                i == self.pour_source if self.is_pouring else False,
                i == self.pour_target if self.is_pouring else False,
                border_color,
                border_width,
            )

            # Draw jug capacity and current amount
            capacity_text = self.font.render(f"{capacity}L", True, WHITE)
            screen.blit(
                capacity_text,
                (jug_x - capacity_text.get_width() // 2, jug_y - jug_height - 25),
            )

            amount_text = self.font.render(f"{amount}L", True, WHITE)
            screen.blit(amount_text, (jug_x - amount_text.get_width() // 2, jug_y + 10))

            # If not selected, add a hint to click
            if (
                not is_selected
                and not self.is_pouring
                and not self.win
                and not self.lose
            ):
                hint_text = self.font.render("", True, (180, 180, 180))
                hint_rect = hint_text.get_rect(center=(jug_x, jug_y - jug_height - 45))
                screen.blit(hint_text, hint_rect)

    def _draw_action_buttons(self, screen):
        """Draw buttons for Fill, Empty, Pour actions"""
        for action, rect in self.action_buttons:
            # Button is enabled only if a jug is selected
            enabled = self.selected_jug is not None

            # Button color based on enabled status
            color = (100, 100, 255) if enabled else (80, 80, 80)

            # Draw button
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)

            # Draw button text
            text = self.font.render(action, True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

    def _draw_hint_button(self, screen):
        """Draw the hint button"""
        # Button color based on hint active status
        color = (0, 200, 0) if self.hint_active else (200, 0, 200)

        # Draw button
        pygame.draw.rect(screen, color, self.hint_button)
        pygame.draw.rect(screen, WHITE, self.hint_button, 1)

        # Draw button text
        text = self.font.render("Hint", True, WHITE)
        text_rect = text.get_rect(center=self.hint_button.center)
        screen.blit(text, text_rect)

    def _draw_hints(self, screen):
        """Draw hint information"""
        if not self.hint_steps:
            hint_text = "No solution found!"
            text = self.font.render(hint_text, True, WHITE)
            screen.blit(text, (20, 120))
            return

        # Draw hint header
        hint_header = self.font.render("Hint Steps:", True, WHITE)
        screen.blit(hint_header, (20, 120))

        # Show next step
        if self.hint_index < len(self.hint_steps):
            step = self.hint_steps[self.hint_index]
            hint_text = f"Step {self.hint_index + 1}: {step[0]}"
            text = self.font.render(hint_text, True, WHITE)
            screen.blit(text, (20, 150))

        # Draw navigation buttons
        prev_enabled = self.hint_index > 0
        next_enabled = self.hint_index < len(self.hint_steps) - 1

        prev_color = (150, 150, 150) if prev_enabled else (80, 80, 80)
        next_color = (150, 150, 150) if next_enabled else (80, 80, 80)

        prev_btn = pygame.Rect(20, 180, 60, 30)
        next_btn = pygame.Rect(90, 180, 60, 30)

        pygame.draw.rect(screen, prev_color, prev_btn)
        pygame.draw.rect(screen, WHITE, prev_btn, 1)
        pygame.draw.rect(screen, next_color, next_btn)
        pygame.draw.rect(screen, WHITE, next_btn, 1)

        prev_text = self.font.render("Prev", True, WHITE)
        next_text = self.font.render("Next", True, WHITE)

        screen.blit(
            prev_text,
            (
                prev_btn.centerx - prev_text.get_width() // 2,
                prev_btn.centery - prev_text.get_height() // 2,
            ),
        )
        screen.blit(
            next_text,
            (
                next_btn.centerx - next_text.get_width() // 2,
                next_btn.centery - next_text.get_height() // 2,
            ),
        )

        # Handle navigation button clicks
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            if prev_btn.collidepoint(mouse_pos) and prev_enabled:
                self.hint_index = max(0, self.hint_index - 1)
                pygame.time.wait(200)  # Prevent multiple clicks
            elif next_btn.collidepoint(mouse_pos) and next_enabled:
                self.hint_index = min(len(self.hint_steps) - 1, self.hint_index + 1)
                pygame.time.wait(200)  # Prevent multiple clicks

    def _draw_completion_message(self, screen, success):
        """Draw win/lose message overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Message
        if success:
            message = "Puzzle Solved!"
            color = GREEN
        else:
            message = "Out of Moves!"
            color = RED

        # Draw message
        message_font = pygame.font.SysFont(None, 64)
        message_text = message_font.render(message, True, color)
        message_rect = message_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)
        )
        screen.blit(message_text, message_rect)

        # Draw sub-message
        sub_font = pygame.font.SysFont(None, 32)
        sub_message = "Press ESC to return to level select"
        sub_text = sub_font.render(sub_message, True, WHITE)
        sub_rect = sub_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
        )
        screen.blit(sub_text, sub_rect)

        # If not successful, draw try again button
        if not success:
            retry_btn = pygame.Rect(
                SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60, 200, 40
            )
            pygame.draw.rect(screen, (100, 100, 255), retry_btn)
            pygame.draw.rect(screen, WHITE, retry_btn, 2)

            retry_text = sub_font.render("Try Again", True, WHITE)
            retry_rect = retry_text.get_rect(center=retry_btn.center)
            screen.blit(retry_text, retry_rect)

            # Check for retry button click
            mouse_pos = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0] and retry_btn.collidepoint(mouse_pos):
                self.reset()

    def reset(self):
        """Reset the level to initial state"""
        super().reset()
        self.jugs = [0] * len(self.capacities)
        self.win = False
        self.lose = False
        self.move_counter.reset(self.max_moves)
        self.selected_jug = None
        self.is_pouring = False
        self.hint_active = False

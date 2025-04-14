import pygame
import time
import random
from levels.base_level import BaseLevel
from algorithms.alpha_beta import AlphaBetaAI
from visualization.pruning_visualizer import PruningVisualizer
from ui.timer import MoveTimer
from entities.power_ups import PowerUpSystem
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, BLUE, RED, GREEN, GRAY


class StrategyLevel(BaseLevel):
    def __init__(self, game_engine, asset_manager):
        super().__init__(game_engine, asset_manager)

        # Game settings
        self.difficulty = 1
        self.set_difficulty(self.difficulty)

        # Board settings
        self.board_size = 6  # Default size
        self.board_state = [
            [None for _ in range(self.board_size)] for _ in range(self.board_size)
        ]
        self.cell_size = 60
        self.board_offset = (
            (SCREEN_WIDTH - self.board_size * self.cell_size) // 2,
            (SCREEN_HEIGHT - self.board_size * self.cell_size) // 2 + 20,
        )

        # Game pieces
        self.player_piece = 1  # Player is 1, AI is 2
        self.ai_piece = 2
        self.current_turn = self.player_piece  # Player starts

        # Game state
        self.selected_cell = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None

        # AI setup
        self.ai = AlphaBetaAI(self.max_depth)
        self.ai_thinking = False
        self.ai_move_start_time = 0
        self.ai_move_delay = 1.0  # Seconds of "thinking" time

        # Timer for moves
        self.move_timer = MoveTimer(self.time_limit)

        # Visualization
        self.visualizer = PruningVisualizer()
        self.show_visualization = False
        self.pruning_data = None

        # Power-up system
        self.power_ups = PowerUpSystem(self.board_size, self.board_state)

        # UI elements
        self.font = pygame.font.SysFont(None, 28)
        self.large_font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 48)

        # UI controls
        self.viz_button_rect = pygame.Rect(SCREEN_WIDTH - 200, 20, 180, 40)
        self.difficulty_button_rect = pygame.Rect(20, 20, 180, 40)
        self.reset_button_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT - 60, 180, 40
        )

        # Initial setup
        self.initialize_board()

    def set_difficulty(self, level):
        """Configure game based on difficulty level"""
        self.difficulty = level

        # Difficulty presets
        if level == 1:  # Easy
            self.board_size = 5
            self.max_depth = 2
            self.time_limit = 20  # Seconds per move
            self.power_up_frequency = 0.7  # Higher chance of power-ups
        elif level == 2:  # Medium
            self.board_size = 6
            self.max_depth = 3
            self.time_limit = 15
            self.power_up_frequency = 0.5
        elif level == 3:  # Hard
            self.board_size = 6
            self.max_depth = 4
            self.time_limit = 12
            self.power_up_frequency = 0.3
        else:  # Expert
            self.board_size = 7
            self.max_depth = 5
            self.time_limit = 10
            self.power_up_frequency = 0.15

        # Update AI with new max depth
        if hasattr(self, "ai"):
            self.ai.max_depth = self.max_depth

        # Update board size and state
        self.board_state = [
            [None for _ in range(self.board_size)] for _ in range(self.board_size)
        ]

        # Recalculate board layout
        self.cell_size = min(
            60, (min(SCREEN_WIDTH, SCREEN_HEIGHT) - 150) // self.board_size
        )
        self.board_offset = (
            (SCREEN_WIDTH - self.board_size * self.cell_size) // 2,
            (SCREEN_HEIGHT - self.board_size * self.cell_size) // 2 + 20,
        )

        # Reset power-ups
        if hasattr(self, "power_ups"):
            self.power_ups = PowerUpSystem(
                self.board_size, self.board_state, self.power_up_frequency
            )

        # Reset timer
        if hasattr(self, "move_timer"):
            self.move_timer.reset(self.time_limit)

    def initialize_board(self):
        """Set up initial board state"""
        # Clear board
        self.board_state = [
            [None for _ in range(self.board_size)] for _ in range(self.board_size)
        ]

        # Player's starting pieces (bottom rows)
        for row in range(self.board_size - 2, self.board_size):
            for col in range(self.board_size):
                if (row + col) % 2 == 0:  # Alternating pattern
                    self.board_state[row][col] = self.player_piece

        # AI's starting pieces (top rows)
        for row in range(2):
            for col in range(self.board_size):
                if (row + col) % 2 == 0:  # Alternating pattern
                    self.board_state[row][col] = self.ai_piece

        # Reset game state
        self.current_turn = self.player_piece
        self.selected_cell = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.ai_thinking = False

        # Initialize power-ups
        self.power_ups.initialize(self.board_state)

        # Reset timer
        self.move_timer.reset(self.time_limit)

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Get mouse position
            pos = pygame.mouse.get_pos()

            # Check if reset button was clicked
            if self.reset_button_rect.collidepoint(pos):
                self.reset()
                return

            # Check if visualization toggle was clicked
            if self.viz_button_rect.collidepoint(pos):
                self.show_visualization = not self.show_visualization
                return

            # Check if difficulty button was clicked
            if self.difficulty_button_rect.collidepoint(pos):
                self.set_difficulty((self.difficulty % 4) + 1)
                self.initialize_board()
                return

            # Handle board clicks only if it's player's turn and game not over
            if (
                self.current_turn == self.player_piece
                and not self.game_over
                and not self.ai_thinking
            ):
                cell = self.get_cell_at_pos(pos)
                if cell is not None:
                    row, col = cell

                    # If we already have a piece selected
                    if self.selected_cell is not None:
                        # If clicking on a valid move location
                        if (row, col) in self.valid_moves:
                            self.make_move(self.selected_cell, (row, col))
                            self.selected_cell = None
                            self.valid_moves = []
                        else:
                            # Select new piece or deselect current
                            self.handle_selection(row, col)
                    else:
                        # Select a piece
                        self.handle_selection(row, col)

    def handle_selection(self, row, col):
        """Handle selecting a piece"""
        # If clicking own piece, select it
        if self.board_state[row][col] == self.player_piece:
            self.selected_cell = (row, col)
            self.valid_moves = self.get_valid_moves(row, col)
        else:
            self.selected_cell = None
            self.valid_moves = []

    def make_move(self, from_cell, to_cell):
        """Move a piece from one cell to another"""
        from_row, from_col = from_cell
        to_row, to_col = to_cell

        # Move the piece
        self.board_state[to_row][to_col] = self.board_state[from_row][from_col]
        self.board_state[from_row][from_col] = None

        # Check for power-up at destination
        power_up = self.power_ups.get_power_up_at(to_row, to_col)
        if power_up:
            self.apply_power_up(power_up, to_row, to_col)
            self.power_ups.remove_power_up(to_row, to_col)

        # Reset move timer
        self.move_timer.reset(self.time_limit)

        # Check for win conditions
        if self.check_winner():
            self.game_over = True
            return

        # Switch turns
        self.current_turn = self.ai_piece

        # Start AI thinking
        self.ai_thinking = True
        self.ai_move_start_time = time.time()

        # Generate visualization data
        if self.show_visualization:
            self.pruning_data = self.ai.get_pruning_stats(
                self.board_state, self.ai_piece, self.player_piece
            )

    def apply_power_up(self, power_up_type, row, col):
        """Apply effects from collected power-ups"""
        if power_up_type == "extra_move":
            # Player gets another turn
            self.current_turn = self.player_piece
            return True

        elif power_up_type == "extra_time":
            # Add time to the move timer
            self.move_timer.add_time(5)  # Add 5 seconds

        elif power_up_type == "shield":
            # Protect piece from capture temporarily
            self.board_state[row][col] = (
                self.player_piece + 10
            )  # Special state for shielded

        elif power_up_type == "double_piece":
            # Create another piece nearby if possible
            adjacent_cells = [
                (row - 1, col),
                (row + 1, col),
                (row, col - 1),
                (row, col + 1),
            ]
            for adj_row, adj_col in adjacent_cells:
                if (
                    0 <= adj_row < self.board_size
                    and 0 <= adj_col < self.board_size
                    and self.board_state[adj_row][adj_col] is None
                ):
                    self.board_state[adj_row][adj_col] = self.player_piece
                    break

        return False

    def get_valid_moves(self, row, col):
        """Get valid moves for a piece at given position"""
        valid_moves = []

        # Get piece type
        piece = self.board_state[row][col]
        if piece is None:
            return valid_moves

        # Movement directions based on piece type
        directions = []

        if piece == self.player_piece:
            # Player pieces can move up and diagonally up
            directions = [(-1, 0), (-1, -1), (-1, 1)]
        elif piece == self.ai_piece:
            # AI pieces can move down and diagonally down
            directions = [(1, 0), (1, -1), (1, 1)]
        elif piece > 10:  # Special pieces with extra moves
            # Can move in all directions
            directions = [
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1),
                (-1, -1),
                (-1, 1),
                (1, -1),
                (1, 1),
            ]

        # Check each direction
        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col

            # Check if the new position is valid
            if 0 <= new_row < self.board_size and 0 <= new_col < self.board_size:

                # Normal move - empty space
                if self.board_state[new_row][new_col] is None:
                    valid_moves.append((new_row, new_col))

                # Capture move - check if can capture opponent's piece
                elif (
                    piece == self.player_piece
                    and self.board_state[new_row][new_col] == self.ai_piece
                ) or (
                    piece == self.ai_piece
                    and self.board_state[new_row][new_col] == self.player_piece
                ):

                    # Can capture diagonally
                    if abs(d_row) == 1 and abs(d_col) == 1:
                        valid_moves.append((new_row, new_col))

        return valid_moves

    def check_winner(self):
        """Check if there's a winner"""
        # Count pieces
        player_pieces = 0
        ai_pieces = 0

        # Check if player reached opponent's side
        for col in range(self.board_size):
            if self.board_state[0][col] == self.player_piece:
                self.winner = self.player_piece
                self.completed = True
                return True

        # Check if AI reached opponent's side
        for col in range(self.board_size):
            if self.board_state[self.board_size - 1][col] == self.ai_piece:
                self.winner = self.ai_piece
                return True

        # Count pieces
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board_state[row][col] == self.player_piece:
                    player_pieces += 1
                elif self.board_state[row][col] == self.ai_piece:
                    ai_pieces += 1

        # Check if one side has no pieces left
        if player_pieces == 0:
            self.winner = self.ai_piece
            return True
        elif ai_pieces == 0:
            self.winner = self.player_piece
            self.completed = True
            return True

        return False

    def ai_make_move(self):
        """Make a move for the AI"""
        # Get the best move from alpha-beta algorithm
        move = self.ai.get_best_move(self.board_state, self.ai_piece, self.player_piece)

        if move:
            from_pos, to_pos = move
            from_row, from_col = from_pos
            to_row, to_col = to_pos

            # Make the move
            self.board_state[to_row][to_col] = self.board_state[from_row][from_col]
            self.board_state[from_row][from_col] = None

            # Check for power-ups (but AI doesn't get power-ups to keep game fair)
            if self.power_ups.get_power_up_at(to_row, to_col):
                self.power_ups.remove_power_up(to_row, to_col)

            # Check for win conditions
            if self.check_winner():
                self.game_over = True
                return

            # Switch back to player
            self.current_turn = self.player_piece

            # Reset move timer for player
            self.move_timer.reset(self.time_limit)

    def get_cell_at_pos(self, pos):
        """Convert screen position to board cell coordinates"""
        x, y = pos
        board_x, board_y = self.board_offset

        # Check if position is on the board
        if (
            board_x <= x < board_x + self.board_size * self.cell_size
            and board_y <= y < board_y + self.board_size * self.cell_size
        ):

            # Calculate cell coordinates
            col = (x - board_x) // self.cell_size
            row = (y - board_y) // self.cell_size

            return (int(row), int(col))

        return None

    def update(self, dt):
        """Update game logic"""
        # Update power-ups
        self.power_ups.update(dt)

        # Update timer if game is active
        if not self.game_over and not self.ai_thinking:
            time_up = self.move_timer.update(dt)
            if time_up and self.current_turn == self.player_piece:
                # Player ran out of time, AI wins
                self.winner = self.ai_piece
                self.game_over = True

        # Handle AI turn
        if (
            self.current_turn == self.ai_piece
            and self.ai_thinking
            and not self.game_over
        ):
            # Add a delay to make the AI seem like it's "thinking"
            if time.time() - self.ai_move_start_time > self.ai_move_delay:
                self.ai_thinking = False
                self.ai_make_move()

        # Update visualizer
        if self.show_visualization and self.pruning_data:
            self.visualizer.update(dt)

    def render(self, screen):
        """Render the strategy game"""
        # Fill background
        screen.fill((30, 40, 50))  # Dark blue-gray background

        # Draw title
        title = self.title_font.render(
            f"Strategy Game - Level {self.difficulty}", True, WHITE
        )
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 15))

        # Draw board
        self._draw_board(screen)

        # Draw power-ups
        self.power_ups.render(screen, self.board_offset, self.cell_size)

        # Draw UI elements
        self._draw_ui(screen)

        # Draw timer
        self.move_timer.render(screen, (SCREEN_WIDTH // 2, 80))

        # Draw visualization if active
        if self.show_visualization and self.pruning_data and not self.game_over:
            vis_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT - 220, 700, 180
            )
            self.visualizer.render(screen, vis_rect, self.pruning_data)

        # Draw game over message if needed
        if self.game_over:
            self._draw_game_over_message(screen)

        # Draw whose turn it is
        turn_text = self.large_font.render(
            "Your Turn" if self.current_turn == self.player_piece else "AI's Turn",
            True,
            GREEN if self.current_turn == self.player_piece else RED,
        )
        screen.blit(turn_text, (SCREEN_WIDTH // 2 - turn_text.get_width() // 2, 120))

        # Show AI thinking
        if self.ai_thinking:
            thinking_text = self.font.render("AI is thinking...", True, WHITE)
            screen.blit(
                thinking_text, (SCREEN_WIDTH // 2 - thinking_text.get_width() // 2, 150)
            )

    def _draw_board(self, screen):
        """Draw the game board and pieces"""
        # Draw board background
        board_width = self.board_size * self.cell_size
        board_height = self.board_size * self.cell_size
        board_rect = pygame.Rect(
            self.board_offset[0], self.board_offset[1], board_width, board_height
        )
        pygame.draw.rect(screen, (80, 80, 80), board_rect)
        pygame.draw.rect(screen, WHITE, board_rect, 2)

        # Draw cells and pieces
        for row in range(self.board_size):
            for col in range(self.board_size):
                # Calculate cell position
                cell_x = self.board_offset[0] + col * self.cell_size
                cell_y = self.board_offset[1] + row * self.cell_size
                cell_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)

                # Draw checkerboard pattern
                if (row + col) % 2 == 0:
                    pygame.draw.rect(screen, (120, 120, 120), cell_rect)
                else:
                    pygame.draw.rect(screen, (60, 60, 60), cell_rect)

                # Draw cell border
                pygame.draw.rect(screen, (40, 40, 40), cell_rect, 1)

                # Highlight selected cell
                if self.selected_cell and self.selected_cell == (row, col):
                    highlight = pygame.Surface(
                        (self.cell_size, self.cell_size), pygame.SRCALPHA
                    )
                    highlight.fill((255, 255, 0, 100))
                    screen.blit(highlight, cell_rect)

                # Highlight valid moves
                if (row, col) in self.valid_moves:
                    highlight = pygame.Surface(
                        (self.cell_size, self.cell_size), pygame.SRCALPHA
                    )
                    highlight.fill((0, 255, 0, 100))
                    screen.blit(highlight, cell_rect)

                # Draw pieces
                piece = self.board_state[row][col]
                if piece is not None:
                    center_x = cell_x + self.cell_size // 2
                    center_y = cell_y + self.cell_size // 2
                    radius = int(self.cell_size * 0.4)

                    # Draw different colored pieces for player and AI
                    if piece == self.player_piece:
                        pygame.draw.circle(screen, GREEN, (center_x, center_y), radius)
                        pygame.draw.circle(
                            screen, WHITE, (center_x, center_y), radius, 2
                        )
                    elif piece == self.ai_piece:
                        pygame.draw.circle(screen, RED, (center_x, center_y), radius)
                        pygame.draw.circle(
                            screen, WHITE, (center_x, center_y), radius, 2
                        )
                    elif piece > 10:  # Shielded piece
                        pygame.draw.circle(screen, GREEN, (center_x, center_y), radius)
                        pygame.draw.circle(
                            screen, (200, 200, 0), (center_x, center_y), radius, 3
                        )

    def _draw_ui(self, screen):
        """Draw UI elements"""
        # Visualization toggle button
        viz_color = GREEN if self.show_visualization else BLUE
        pygame.draw.rect(screen, viz_color, self.viz_button_rect)
        pygame.draw.rect(screen, WHITE, self.viz_button_rect, 2)

        viz_text = self.font.render("Toggle Pruning Visual", True, WHITE)
        viz_text_rect = viz_text.get_rect(center=self.viz_button_rect.center)
        screen.blit(viz_text, viz_text_rect)

        # Difficulty button
        pygame.draw.rect(screen, BLUE, self.difficulty_button_rect)
        pygame.draw.rect(screen, WHITE, self.difficulty_button_rect, 2)

        diff_text = self.font.render(f"Difficulty: {self.difficulty}", True, WHITE)
        diff_text_rect = diff_text.get_rect(center=self.difficulty_button_rect.center)
        screen.blit(diff_text, diff_text_rect)

        # Reset button
        pygame.draw.rect(screen, RED, self.reset_button_rect)
        pygame.draw.rect(screen, WHITE, self.reset_button_rect, 2)

        reset_text = self.large_font.render("Reset Game", True, WHITE)
        reset_text_rect = reset_text.get_rect(center=self.reset_button_rect.center)
        screen.blit(reset_text, reset_text_rect)

        # Draw power-up legend
        self._draw_power_up_legend(screen)

    def _draw_power_up_legend(self, screen):
        """Draw the power-up legend"""
        legend_x = SCREEN_WIDTH - 180
        legend_y = 70

        legend_title = self.font.render("Power-ups:", True, WHITE)
        screen.blit(legend_title, (legend_x, legend_y))

        legend_y += 25
        for i, (name, color) in enumerate(self.power_ups.get_power_up_types()):
            # Draw color box
            pygame.draw.rect(screen, color, (legend_x, legend_y + i * 20, 15, 15))
            pygame.draw.rect(screen, WHITE, (legend_x, legend_y + i * 20, 15, 15), 1)

            # Draw name
            name_text = self.font.render(name, True, WHITE)
            screen.blit(name_text, (legend_x + 20, legend_y + i * 20))

    def _draw_game_over_message(self, screen):
        """Draw game over message"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Game over message
        if self.winner == self.player_piece:
            message = "You Win!"
            color = GREEN
        else:
            message = "AI Wins!"
            color = RED

        # Draw main message
        game_over_font = pygame.font.SysFont(None, 72)
        message_surface = game_over_font.render(message, True, color)
        message_rect = message_surface.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        )
        screen.blit(message_surface, message_rect)

        # Draw instruction
        instruction = self.large_font.render(
            "Press ESC to return to level select or Reset to play again", True, WHITE
        )
        instruction_rect = instruction.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
        )
        screen.blit(instruction, instruction_rect)

    def reset(self):
        """Reset the level to initial state"""
        super().reset()
        self.initialize_board()

import pygame
import time
import random
from levels.base_level import BaseLevel
from algorithms.minimax import MinimaxAI
from visualization.decision_tree import DecisionTreeVisualizer
from ui.board_ui import GameBoard
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, BLUE, RED, GREEN

class TicTacToeLevel(BaseLevel):
    def __init__(self, game_engine, asset_manager):
        super().__init__(game_engine, asset_manager)
        
        # Game settings
        self.difficulty = 1
        self.set_difficulty(self.difficulty)
        
        # Player symbols
        self.player_symbol = 'X'
        self.ai_symbol = 'O'
        
        # Game state
        self.current_turn = self.player_symbol  # Player goes first
        self.game_over = False
        self.winner = None
        
        # Board setup
        self.board_size = 3  # Default 3x3 board
        self.special_tiles = []  # Coordinates of special tiles (x, y, type)
        
        # Initialize game board
        self.board = GameBoard(
            self.board_size, 
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            self.special_tiles
        )
        
        # AI setup
        self.ai = MinimaxAI(self.max_depth)
        self.ai_thinking = False
        self.ai_move_start_time = 0
        self.ai_move_delay = 0.5  # Seconds of "thinking" time for AI
        self.ai_selected_move = None
        
        # Visualization
        self.visualizer = DecisionTreeVisualizer()
        self.show_visualization = False
        self.visualization_data = None
        
        # UI elements
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 48)
        
        # UI controls
        self.viz_button_rect = pygame.Rect(SCREEN_WIDTH - 200, 20, 180, 40)
        self.difficulty_button_rect = pygame.Rect(20, 20, 180, 40)
        self.reset_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT - 60, 180, 40)
        
        # Special tile types
        self.special_tile_types = {
            'double': {'color': (0, 200, 100), 'name': 'Double Move'},
            'block': {'color': (200, 50, 50), 'name': 'Blocking'},
            'swap': {'color': (200, 200, 0), 'name': 'Symbol Swap'},
            'random': {'color': (150, 100, 200), 'name': 'Random Effect'}
        }
        
        # Initialize the board state
        self.reset_game()
    
    def set_difficulty(self, level):
        """Configure game based on difficulty level"""
        self.difficulty = level
        
        # Difficulty presets
        if level == 1:
            # Easy - shallow search
            self.board_size = 3
            self.max_depth = 1
            self.special_tiles = []
        elif level == 2:
            # Medium - deeper search
            self.board_size = 3
            self.max_depth = 3
            self.special_tiles = [(0, 0, 'double')]
        elif level == 3:
            # Hard - optimal play
            self.board_size = 3
            self.max_depth = 9
            self.special_tiles = [(0, 0, 'double'), (2, 2, 'block')]
        else:  # level 4 or higher
            # Expert - larger board
            self.board_size = 4
            self.max_depth = 4  # Limited depth due to larger board
            self.special_tiles = [
                (0, 0, 'double'),
                (3, 3, 'block'),
                (1, 2, 'swap'),
                (2, 1, 'random')
            ]
        
        # Update AI with new max depth
        if hasattr(self, 'ai'):
            self.ai.max_depth = self.max_depth
        
        # Reset the game with new settings
        if hasattr(self, 'board'):
            self.reset_game()
    
    def reset_game(self):
        """Reset the game to initial state"""
        # Create empty board
        self.board = GameBoard(
            self.board_size, 
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            self.special_tiles
        )
        
        # Reset game state
        self.current_turn = self.player_symbol
        self.game_over = False
        self.winner = None
        self.ai_thinking = False
        self.show_visualization = False
        self.visualization_data = None
        self.completed = False
    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Get mouse position
            pos = pygame.mouse.get_pos()
            
            # Check if reset button was clicked
            if self.reset_button_rect.collidepoint(pos):
                self.reset_game()
                return
            
            # Check if visualization toggle was clicked
            if self.viz_button_rect.collidepoint(pos):
                self.show_visualization = not self.show_visualization
                return
            
            # Check if difficulty button was clicked
            if self.difficulty_button_rect.collidepoint(pos):
                # Cycle through difficulties
                self.set_difficulty((self.difficulty % 4) + 1)
                return
            
            # Handle board clicks only if it's player's turn and game is not over
            if self.current_turn == self.player_symbol and not self.game_over:
                # Get board cell that was clicked
                cell = self.board.get_cell_at_pos(pos)
                if cell is not None:
                    row, col = cell
                    if self.board.is_empty(row, col):
                        # Make the move
                        self.make_move(row, col, self.player_symbol)
    
    def make_move(self, row, col, symbol):
        """Make a move on the board"""
        if self.board.is_empty(row, col) and not self.game_over:
            # Apply special tile effects
            special_type = self.board.get_special_tile_type(row, col)
            
            # Make the move
            self.board.place_symbol(row, col, symbol)
            
            # Check for game end
            if self.check_winner() or self.board.is_full():
                self.game_over = True
                if self.winner == self.player_symbol:
                    self.completed = True  # Player won, mark level as completed
                return
            
            # Handle special tile effects
            extra_move = False
            if special_type:
                extra_move = self.apply_special_tile_effect(special_type, row, col, symbol)
            
            # Switch turns if no extra move
            if not extra_move:
                self.current_turn = self.ai_symbol if symbol == self.player_symbol else self.player_symbol
                
                # Start AI thinking process if it's AI's turn
                if self.current_turn == self.ai_symbol:
                    self.ai_thinking = True
                    self.ai_move_start_time = time.time()
                    
                    # Generate AI decision tree for visualization before making the move
                    board_state = self.board.get_state()
                    
                    # Get the decision tree data for visualization
                    self.visualization_data = self.ai.get_decision_tree(board_state, self.ai_symbol, self.player_symbol)
    
    def apply_special_tile_effect(self, tile_type, row, col, symbol):
        """Apply effect of special tile and return True if player gets an extra move"""
        if tile_type == 'double':
            # Player gets another turn
            return True
            
        elif tile_type == 'block':
            # Block a random empty cell
            empty_cells = self.board.get_empty_cells()
            if empty_cells:
                block_row, block_col = random.choice(empty_cells)
                self.board.block_cell(block_row, block_col)
            
        elif tile_type == 'swap':
            # Swap player and AI symbols temporarily for this turn
            self.player_symbol, self.ai_symbol = self.ai_symbol, self.player_symbol
            
        elif tile_type == 'random':
            # Apply a random effect
            effects = ['double', 'block', 'swap']
            random_effect = random.choice(effects)
            return self.apply_special_tile_effect(random_effect, row, col, symbol)
            
        return False
    
    def check_winner(self):
        """Check if there's a winner on the board"""
        # Check rows, columns and diagonals
        board_state = self.board.get_state()
        
        # Check rows
        for i in range(self.board_size):
            if all(board_state[i][j] == self.player_symbol for j in range(self.board_size)):
                self.winner = self.player_symbol
                return True
            if all(board_state[i][j] == self.ai_symbol for j in range(self.board_size)):
                self.winner = self.ai_symbol
                return True
        
        # Check columns
        for j in range(self.board_size):
            if all(board_state[i][j] == self.player_symbol for i in range(self.board_size)):
                self.winner = self.player_symbol
                return True
            if all(board_state[i][j] == self.ai_symbol for i in range(self.board_size)):
                self.winner = self.ai_symbol
                return True
        
        # Check main diagonal
        if all(board_state[i][i] == self.player_symbol for i in range(self.board_size)):
            self.winner = self.player_symbol
            return True
        if all(board_state[i][i] == self.ai_symbol for i in range(self.board_size)):
            self.winner = self.ai_symbol
            return True
        
        # Check other diagonal
        if all(board_state[i][self.board_size - i - 1] == self.player_symbol for i in range(self.board_size)):
            self.winner = self.player_symbol
            return True
        if all(board_state[i][self.board_size - i - 1] == self.ai_symbol for i in range(self.board_size)):
            self.winner = self.ai_symbol
            return True
        
        return False
    
    def update(self, dt):
        """Update game logic"""
        # Handle AI turn
        if self.current_turn == self.ai_symbol and self.ai_thinking and not self.game_over:
            # Add a delay to make the AI seem like it's "thinking"
            if time.time() - self.ai_move_start_time > self.ai_move_delay:
                self.ai_thinking = False
                
                # Get board state
                board_state = self.board.get_state()
                
                # Get AI move
                best_move = self.ai.get_best_move(board_state, self.ai_symbol, self.player_symbol)
                
                if best_move:
                    row, col = best_move
                    # Make the AI move
                    self.make_move(row, col, self.ai_symbol)
                else:
                    # No valid moves (shouldn't happen in tic-tac-toe unless board is full)
                    self.game_over = True
        
        # Update visualizer if active
        if self.show_visualization and self.visualization_data:
            self.visualizer.update(dt)
    
    def render(self, screen):
        """Render the tic-tac-toe game"""
        # Fill background
        screen.fill((30, 30, 60))  # Dark blue-purple background
        
        # Draw title
        title = self.title_font.render(f"Tic-Tac-Toe - Level {self.difficulty}", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        # Draw board
        self.board.render(screen)
        
        # Draw visualization if active
        if self.show_visualization and self.visualization_data and not self.game_over:
            vis_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT - 250, 500, 200)
            self.visualizer.render(screen, vis_rect, self.visualization_data)
        
        # Draw UI buttons
        self._draw_ui_buttons(screen)
        
        # Draw game status
        self._draw_game_status(screen)
        
        # Draw completion message if game is over
        if self.game_over:
            self._draw_game_over_message(screen)
    
    def _draw_ui_buttons(self, screen):
        """Draw UI buttons"""
        # Visualization toggle button
        viz_color = GREEN if self.show_visualization else BLUE
        pygame.draw.rect(screen, viz_color, self.viz_button_rect)
        pygame.draw.rect(screen, WHITE, self.viz_button_rect, 2)
        
        viz_text = self.small_font.render("Toggle Visualization", True, WHITE)
        viz_text_rect = viz_text.get_rect(center=self.viz_button_rect.center)
        screen.blit(viz_text, viz_text_rect)
        
        # Difficulty button
        pygame.draw.rect(screen, BLUE, self.difficulty_button_rect)
        pygame.draw.rect(screen, WHITE, self.difficulty_button_rect, 2)
        
        diff_text = self.small_font.render(f"Difficulty: {self.difficulty}", True, WHITE)
        diff_text_rect = diff_text.get_rect(center=self.difficulty_button_rect.center)
        screen.blit(diff_text, diff_text_rect)
        
        # Reset button
        pygame.draw.rect(screen, RED, self.reset_button_rect)
        pygame.draw.rect(screen, WHITE, self.reset_button_rect, 2)
        
        reset_text = self.font.render("Reset Game", True, WHITE)
        reset_text_rect = reset_text.get_rect(center=self.reset_button_rect.center)
        screen.blit(reset_text, reset_text_rect)
    
    def _draw_game_status(self, screen):
        """Draw game status information"""
        # Current turn indicator
        turn_text = self.font.render(
            f"Current Turn: {'Player (X)' if self.current_turn == self.player_symbol else 'AI (O)'}", 
            True, 
            WHITE
        )
        screen.blit(turn_text, (50, 80))
        
        # AI thinking indicator
        if self.ai_thinking:
            thinking_text = self.font.render("AI is thinking...", True, WHITE)
            screen.blit(thinking_text, (50, 120))
        
        # Special tile legend
        if self.special_tiles:
            legend_text = self.small_font.render("Special Tiles:", True, WHITE)
            screen.blit(legend_text, (SCREEN_WIDTH - 200, 80))
            
            for i, (tile_type, info) in enumerate(self.special_tile_types.items()):
                # Draw color square
                color_rect = pygame.Rect(SCREEN_WIDTH - 200, 110 + i * 30, 20, 20)
                pygame.draw.rect(screen, info['color'], color_rect)
                pygame.draw.rect(screen, WHITE, color_rect, 1)
                
                # Draw name
                type_text = self.small_font.render(info['name'], True, WHITE)
                screen.blit(type_text, (SCREEN_WIDTH - 170, 110 + i * 30))
    
    def _draw_game_over_message(self, screen):
        """Draw game over message"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Game over message
        if self.winner == self.player_symbol:
            message = "You Win!"
            color = GREEN
        elif self.winner == self.ai_symbol:
            message = "AI Wins!"
            color = RED
        else:
            message = "It's a Draw!"
            color = WHITE
        
        # Draw main message
        game_over_font = pygame.font.SysFont(None, 72)
        message_surface = game_over_font.render(message, True, color)
        message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(message_surface, message_rect)
        
        # Draw instruction
        instruction = self.font.render("Press ESC to return to level select or Reset to play again", True, WHITE)
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        screen.blit(instruction, instruction_rect)
    
    def reset(self):
        """Reset the level to initial state"""
        super().reset()
        self.reset_game()

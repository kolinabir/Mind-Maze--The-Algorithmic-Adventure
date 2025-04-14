import pygame
import random
import time
import math
from levels.base_level import BaseLevel
from algorithms.search_algorithms import BFS, DFS
from algorithms.jug_problem import JugSolver
from algorithms.minimax import MinimaxAI
from algorithms.alpha_beta import AlphaBetaAI
from ui.algorithm_selector import AlgorithmSelector
from visualization.composite_visualizer import CompositeVisualizer
from game_logic.challenge_manager import ChallengeManager
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GREEN, RED, BLUE, YELLOW, LIGHT_BLUE

class IntegrationLevel(BaseLevel):
    def __init__(self, game_engine, asset_manager):
        super().__init__(game_engine, asset_manager)
        
        # Level settings
        self.difficulty = 1
        self.set_difficulty(self.difficulty)
        
        # Initialize component algorithms
        self.bfs = BFS()
        self.dfs = DFS()
        self.jug_solver = JugSolver()
        self.minimax = MinimaxAI(3)  # Depth 3 for minimax
        self.alpha_beta = AlphaBetaAI(4)  # Depth 4 for alpha-beta
        
        # UI elements
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 36)
        self.big_font = pygame.font.SysFont(None, 48)
        
        # Create algorithm selector
        self.algorithm_selector = AlgorithmSelector()
        
        # Create challenge manager
        self.challenge_manager = ChallengeManager(self.difficulty)
        
        # Create composite visualizer
        self.visualizer = CompositeVisualizer()
        
        # Player stats
        self.score = 0
        self.time_remaining = 600  # 10 minutes in seconds
        self.current_algorithm = None
        self.challenge_complete = False
        
        # Timer elements
        self.start_time = time.time()
        self.elapsed_time = 0
        
        # UI elements positions
        self.sidebar_width = 200
        self.main_area_rect = pygame.Rect(
            self.sidebar_width, 0, 
            SCREEN_WIDTH - self.sidebar_width, SCREEN_HEIGHT
        )
        
        # Challenge area
        self.challenge_area_rect = pygame.Rect(
            self.sidebar_width + 20, 80,
            SCREEN_WIDTH - self.sidebar_width - 40, SCREEN_HEIGHT - 160
        )
        
        # Initialize first challenge
        self.start_next_challenge()
    
    def set_difficulty(self, level):
        """Configure game based on difficulty level"""
        self.difficulty = level
        
        # Difficulty presets
        if level == 1:  # Easy
            self.time_per_challenge = 180  # 3 minutes
            self.challenge_count = 3
        elif level == 2:  # Medium
            self.time_per_challenge = 150  # 2.5 minutes
            self.challenge_count = 4
        elif level == 3:  # Hard
            self.time_per_challenge = 120  # 2 minutes
            self.challenge_count = 5
        else:  # Expert
            self.time_per_challenge = 90  # 1.5 minutes
            self.challenge_count = 6
        
        # Reset challenge manager with new difficulty
        if hasattr(self, 'challenge_manager'):
            self.challenge_manager = ChallengeManager(self.difficulty)
    
    def start_next_challenge(self):
        """Initialize the next challenge"""
        challenge = self.challenge_manager.get_next_challenge()
        
        if challenge:
            self.current_challenge = challenge
            self.current_algorithm = challenge.get("required_algorithm")
            self.challenge_description = challenge.get("description")
            self.challenge_complete = False
            self.algorithm_selector.set_active(self.current_algorithm)
            self.start_time = time.time()
        else:
            # No more challenges, player has won!
            self.completed = True
            self.challenge_complete = True
    
    def handle_event(self, event):
        """Handle pygame events"""
        # Handle algorithm selection
        algo_changed = self.algorithm_selector.handle_event(event)
        if algo_changed:
            self.current_algorithm = self.algorithm_selector.get_selected()
        
        # Handle challenge-specific events
        if self.current_challenge and not self.challenge_complete:
            challenge_type = self.current_challenge.get("type")
            
            if challenge_type == "maze":
                self._handle_maze_event(event)
            elif challenge_type == "water_jug":
                self._handle_jug_event(event)
            elif challenge_type == "tictactoe":
                self._handle_tictactoe_event(event)
            elif challenge_type == "strategy":
                self._handle_strategy_event(event)
            elif challenge_type == "integration":
                self._handle_integration_event(event)
        
        # Handle next challenge button if current one is complete
        if self.challenge_complete and event.type == pygame.MOUSEBUTTONDOWN:
            next_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 60, 200, 40)
            if next_button_rect.collidepoint(event.pos):
                self.start_next_challenge()
    
    def _handle_maze_event(self, event):
        """Handle maze challenge events"""
        if event.type == pygame.KEYDOWN:
            # Get current position and target
            current_pos = self.current_challenge.get("current_pos")
            target_pos = self.current_challenge.get("target_pos")
            grid = self.current_challenge.get("grid")
            
            # Calculate potential new position based on key
            new_pos = list(current_pos)
            if event.key == pygame.K_UP:
                new_pos[0] -= 1
            elif event.key == pygame.K_DOWN:
                new_pos[0] += 1
            elif event.key == pygame.K_LEFT:
                new_pos[1] -= 1
            elif event.key == pygame.K_RIGHT:
                new_pos[1] += 1
            
            # Check if move is valid
            if (0 <= new_pos[0] < len(grid) and 
                0 <= new_pos[1] < len(grid[0]) and
                grid[new_pos[0]][new_pos[1]] != 1):  # Not a wall
                
                self.current_challenge["current_pos"] = tuple(new_pos)
                
                # Check for completion
                if tuple(new_pos) == target_pos:
                    self._complete_challenge()
    
    def _handle_jug_event(self, event):
        """Handle water jug challenge events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Get jugs and target
            jugs = self.current_challenge.get("jugs")
            capacities = self.current_challenge.get("capacities")
            target = self.current_challenge.get("target")
            
            # Calculate jug button areas
            jug_width = 80
            total_width = len(jugs) * (jug_width + 20)
            start_x = (self.challenge_area_rect.width - total_width) // 2 + self.challenge_area_rect.left
            
            # Check which jug was clicked
            for i in range(len(jugs)):
                jug_rect = pygame.Rect(
                    start_x + i * (jug_width + 20),
                    self.challenge_area_rect.centery - 100,
                    jug_width, 200
                )
                
                if jug_rect.collidepoint(event.pos):
                    # Toggle jug selection
                    selected_jug = self.current_challenge.get("selected_jug")
                    if selected_jug is None:
                        self.current_challenge["selected_jug"] = i
                    elif selected_jug == i:
                        self.current_challenge["selected_jug"] = None
                    else:
                        # Pour from selected to clicked
                        self._pour_water(selected_jug, i, jugs, capacities)
                        self.current_challenge["selected_jug"] = None
                        
                        # Check for completion
                        if target in jugs:
                            self._complete_challenge()
    
    def _pour_water(self, from_jug, to_jug, jugs, capacities):
        """Helper to pour water between jugs"""
        # Calculate pour amount
        pour_amount = min(jugs[from_jug], capacities[to_jug] - jugs[to_jug])
        
        # Update jugs
        jugs[from_jug] -= pour_amount
        jugs[to_jug] += pour_amount
    
    def _handle_tictactoe_event(self, event):
        """Handle tic-tac-toe challenge events"""
        if event.type == pygame.MOUSEBUTTONDOWN and not self.current_challenge.get("ai_turn"):
            # Get board and current turn
            board = self.current_challenge.get("board")
            size = len(board)
            
            # Calculate board cell areas
            cell_size = min(60, (min(self.challenge_area_rect.width, self.challenge_area_rect.height) - 40) // size)
            board_width = size * cell_size
            start_x = self.challenge_area_rect.centerx - board_width // 2
            start_y = self.challenge_area_rect.centery - board_width // 2
            
            # Check which cell was clicked
            for row in range(size):
                for col in range(size):
                    cell_rect = pygame.Rect(
                        start_x + col * cell_size,
                        start_y + row * cell_size,
                        cell_size, cell_size
                    )
                    
                    if cell_rect.collidepoint(event.pos) and board[row][col] is None:
                        # Player makes a move
                        board[row][col] = 'X'
                        
                        # Check for win
                        if self._check_tictactoe_win(board, 'X'):
                            self._complete_challenge()
                            return
                        
                        # Set AI's turn
                        self.current_challenge["ai_turn"] = True
    
    def _check_tictactoe_win(self, board, player):
        """Check if player has won tic-tac-toe"""
        size = len(board)
        
        # Check rows
        for row in range(size):
            if all(board[row][col] == player for col in range(size)):
                return True
        
        # Check columns
        for col in range(size):
            if all(board[row][col] == player for row in range(size)):
                return True
        
        # Check diagonals
        if all(board[i][i] == player for i in range(size)):
            return True
        if all(board[i][size-1-i] == player for i in range(size)):
            return True
        
        return False
    
    def _handle_strategy_event(self, event):
        """Handle strategy game challenge events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Get board state
            board = self.current_challenge.get("board")
            selected = self.current_challenge.get("selected")
            
            # Calculate board cell areas
            board_size = len(board)
            cell_size = min(40, (min(self.challenge_area_rect.width, self.challenge_area_rect.height) - 40) // board_size)
            board_width = board_size * cell_size
            start_x = self.challenge_area_rect.centerx - board_width // 2
            start_y = self.challenge_area_rect.centery - board_width // 2
            
            # Get clicked cell
            for row in range(board_size):
                for col in range(board_size):
                    cell_rect = pygame.Rect(
                        start_x + col * cell_size,
                        start_y + row * cell_size,
                        cell_size, cell_size
                    )
                    
                    if cell_rect.collidepoint(event.pos):
                        if selected is None:
                            # Select a piece
                            if board[row][col] == 1:  # Player's piece
                                self.current_challenge["selected"] = (row, col)
                        else:
                            # Try to move the selected piece
                            sel_row, sel_col = selected
                            
                            # Check if move is valid (simplified)
                            if (board[row][col] is None or board[row][col] == 2) and abs(row - sel_row) <= 1 and abs(col - sel_col) <= 1:
                                # Move the piece
                                board[row][col] = 1
                                board[sel_row][sel_col] = None
                                self.current_challenge["selected"] = None
                                
                                # Check for win - reaching opponent's side
                                if row == 0:
                                    self._complete_challenge()
    
    def _handle_integration_event(self, event):
        """Handle integration challenge events"""
        # Integration challenge combines multiple algorithm challenges
        # Based on the sub-challenge type, delegate to the appropriate handler
        sub_type = self.current_challenge.get("sub_type")
        
        if sub_type == "maze":
            self._handle_maze_event(event)
        elif sub_type == "water_jug":
            self._handle_jug_event(event)
        elif sub_type == "tictactoe":
            self._handle_tictactoe_event(event)
        elif sub_type == "strategy":
            self._handle_strategy_event(event)
    
    def _complete_challenge(self):
        """Mark current challenge as complete"""
        self.challenge_complete = True
        self.score += int((self.time_per_challenge - (time.time() - self.start_time)) * 10)
        
        # Check if algorithm selection was correct
        if self.algorithm_selector.get_selected() == self.current_challenge.get("required_algorithm"):
            self.score += 100  # Bonus for correct algorithm
    
    def update(self, dt):
        """Update game logic"""
        # Update timer
        if not self.challenge_complete and not self.completed:
            self.elapsed_time = time.time() - self.start_time
            
            # Check for time out
            if self.elapsed_time >= self.time_per_challenge:
                # Failed challenge due to timeout
                self.challenge_complete = True
            
            # Update algorithm visualization
            self.visualizer.update(dt, self.current_algorithm)
            
            # Update AI for tic-tac-toe and strategy challenges
            if self.current_challenge:
                challenge_type = self.current_challenge.get("type")
                
                if challenge_type == "tictactoe" and self.current_challenge.get("ai_turn", False):
                    self._update_tictactoe_ai()
                elif challenge_type == "strategy" and not self.challenge_complete:
                    self._update_strategy_ai()
    
    def _update_tictactoe_ai(self):
        """Make AI move for tic-tac-toe challenge"""
        board = self.current_challenge.get("board")
        
        # Convert board to format expected by minimax
        minimax_board = []
        for row in board:
            minimax_row = []
            for cell in row:
                if cell == 'X':
                    minimax_row.append(1)  # Player
                elif cell == 'O':
                    minimax_row.append(2)  # AI
                else:
                    minimax_row.append(None)  # Empty
            minimax_board.append(minimax_row)
        
        # Use minimax or alpha-beta based on selected algorithm
        if self.current_algorithm == "minimax":
            move = self.minimax.get_best_move(minimax_board, 2, 1)
        else:
            move = self.alpha_beta.get_best_move(minimax_board, 2, 1)
        
        if move:
            row, col = move
            board[row][col] = 'O'
            
            # Check for AI win
            if self._check_tictactoe_win(board, 'O'):
                # AI wins, player loses
                pass
            
            # Back to player's turn
            self.current_challenge["ai_turn"] = False
    
    def _update_strategy_ai(self):
        """Make AI move for strategy challenge"""
        # Only make AI move occasionally to give player time to think
        if random.random() < 0.01:  # 1% chance each update to make a move
            board = self.current_challenge.get("board")
            board_size = len(board)
            
            # Find AI pieces
            ai_pieces = []
            for row in range(board_size):
                for col in range(board_size):
                    if board[row][col] == 2:  # AI piece
                        ai_pieces.append((row, col))
            
            if ai_pieces:
                # Pick random AI piece
                piece = random.choice(ai_pieces)
                row, col = piece
                
                # Try to move down if possible
                if row < board_size - 1:
                    if board[row + 1][col] is None:
                        board[row + 1][col] = 2
                        board[row][col] = None
                    elif (row < board_size - 1 and col < board_size - 1 and 
                          board[row + 1][col + 1] == 1):  # Can capture player piece
                        board[row + 1][col + 1] = 2
                        board[row][col] = None
                    elif (row < board_size - 1 and col > 0 and 
                          board[row + 1][col - 1] == 1):  # Can capture player piece
                        board[row + 1][col - 1] = 2
                        board[row][col] = None
    
    def render(self, screen):
        """Render the integration level"""
        # Fill background
        screen.fill((20, 30, 40))  # Dark blue-gray background
        
        # Draw sidebar
        self._draw_sidebar(screen)
        
        # Draw main area
        pygame.draw.rect(screen, (30, 40, 50), self.main_area_rect)
        
        # Draw title
        title = self.big_font.render("FINAL CHALLENGE", True, WHITE)
        screen.blit(title, (self.main_area_rect.centerx - title.get_width() // 2, 20))
        
        # Draw score and timer
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (self.main_area_rect.right - score_text.get_width() - 20, 20))
        
        time_color = GREEN
        if self.elapsed_time > self.time_per_challenge * 0.7:
            time_color = YELLOW
        elif self.elapsed_time > self.time_per_challenge * 0.9:
            time_color = RED
            
        time_left = max(0, self.time_per_challenge - self.elapsed_time)
        minutes = int(time_left) // 60
        seconds = int(time_left) % 60
        time_text = self.font.render(f"Time: {minutes:02d}:{seconds:02d}", True, time_color)
        screen.blit(time_text, (self.main_area_rect.left + 20, 20))
        
        # Draw challenge area
        pygame.draw.rect(screen, (40, 50, 60), self.challenge_area_rect)
        pygame.draw.rect(screen, WHITE, self.challenge_area_rect, 2)
        
        # Draw challenge content
        if self.current_challenge:
            self._draw_challenge(screen)
        
        # Draw algorithm selector
        self.algorithm_selector.render(screen, pygame.Rect(
            self.sidebar_width + 20, SCREEN_HEIGHT - 70,
            SCREEN_WIDTH - self.sidebar_width - 40, 60
        ))
        
        # Draw challenge completion message
        if self.challenge_complete and not self.completed:
            self._draw_challenge_complete(screen)
        elif self.completed:
            self._draw_game_complete(screen)
    
    def _draw_sidebar(self, screen):
        """Draw the sidebar with algorithm information"""
        # Draw sidebar background
        sidebar_rect = pygame.Rect(0, 0, self.sidebar_width, SCREEN_HEIGHT)
        pygame.draw.rect(screen, (25, 25, 35), sidebar_rect)
        pygame.draw.line(screen, WHITE, (self.sidebar_width, 0), (self.sidebar_width, SCREEN_HEIGHT), 2)
        
        # Draw algorithm information
        title = self.font.render("ALGORITHMS", True, WHITE)
        screen.blit(title, (10, 20))
        
        y_pos = 60
        algorithms = [
            ("BFS/DFS", "Path finding in mazes"),
            ("Water Jug", "State space search"),
            ("Minimax", "Game tree evaluation"),
            ("Alpha-Beta", "Pruned game tree search"),
            ("Integration", "Combined algorithms")
        ]
        
        for name, desc in algorithms:
            # Highlight current algorithm
            if ((name == "BFS/DFS" and self.current_algorithm in ["bfs", "dfs"]) or
                (name == "Water Jug" and self.current_algorithm == "water_jug") or
                (name == "Minimax" and self.current_algorithm == "minimax") or
                (name == "Alpha-Beta" and self.current_algorithm == "alpha_beta") or
                (name == "Integration" and self.current_algorithm == "integration")):
                pygame.draw.rect(screen, (50, 50, 80), (5, y_pos - 5, self.sidebar_width - 10, 50))
            
            # Draw algorithm name and description
            name_text = self.font.render(name, True, WHITE)
            screen.blit(name_text, (15, y_pos))
            
            desc_text = self.font.render(desc, True, LIGHT_BLUE)
            screen.blit(desc_text, (20, y_pos + 25))
            
            y_pos += 60
        
        # Draw challenge info
        if self.current_challenge:
            challenge_type = self.current_challenge.get("type").upper()
            pygame.draw.rect(screen, (40, 40, 60), (5, y_pos + 20, self.sidebar_width - 10, 80))
            
            type_text = self.font.render(f"Challenge: {challenge_type}", True, WHITE)
            screen.blit(type_text, (15, y_pos + 30))
            
            algo_text = self.font.render(f"Best Algorithm:", True, WHITE)
            screen.blit(algo_text, (15, y_pos + 55))
            
            required_algo = self.current_challenge.get("required_algorithm").upper()
            req_text = self.font.render(required_algo, True, GREEN)
            screen.blit(req_text, (15, y_pos + 80))
    
    def _draw_challenge(self, screen):
        """Draw the current challenge"""
        challenge_type = self.current_challenge.get("type")
        
        # Draw challenge description
        desc_text = self.font.render(self.challenge_description, True, WHITE)
        screen.blit(desc_text, (self.challenge_area_rect.centerx - desc_text.get_width() // 2, 
                               self.challenge_area_rect.top + 10))
        
        # Draw challenge based on type
        if challenge_type == "maze":
            self._draw_maze_challenge(screen)
        elif challenge_type == "water_jug":
            self._draw_jug_challenge(screen)
        elif challenge_type == "tictactoe":
            self._draw_tictactoe_challenge(screen)
        elif challenge_type == "strategy":
            self._draw_strategy_challenge(screen)
        elif challenge_type == "integration":
            self._draw_integration_challenge(screen)
    
    def _draw_maze_challenge(self, screen):
        """Draw maze challenge"""
        grid = self.current_challenge.get("grid")
        current_pos = self.current_challenge.get("current_pos")
        target_pos = self.current_challenge.get("target_pos")
        
        # Calculate cell size
        grid_height = len(grid)
        grid_width = len(grid[0])
        cell_size = min(
            (self.challenge_area_rect.width - 20) // grid_width,
            (self.challenge_area_rect.height - 40) // grid_height
        )
        
        # Calculate starting position
        start_x = self.challenge_area_rect.centerx - (grid_width * cell_size) // 2
        start_y = self.challenge_area_rect.top + 40
        
        # Draw grid
        for row in range(grid_height):
            for col in range(grid_width):
                cell_rect = pygame.Rect(
                    start_x + col * cell_size,
                    start_y + row * cell_size,
                    cell_size, cell_size
                )
                
                # Determine cell color
                if grid[row][col] == 1:  # Wall
                    color = BLACK
                else:  # Path
                    color = WHITE
                
                # Draw cell
                pygame.draw.rect(screen, color, cell_rect)
                pygame.draw.rect(screen, (100, 100, 100), cell_rect, 1)
                
                # Draw current position
                if (row, col) == current_pos:
                    pygame.draw.circle(
                        screen, GREEN,
                        (cell_rect.centerx, cell_rect.centery),
                        cell_size // 2 - 2
                    )
                
                # Draw target position
                if (row, col) == target_pos:
                    pygame.draw.circle(
                        screen, RED,
                        (cell_rect.centerx, cell_rect.centery),
                        cell_size // 3
                    )
                    
        # Draw algorithm visualization
        if self.current_algorithm in ["bfs", "dfs"]:
            # Generate path for visualization
            path = []
            visited = []
            
            if self.current_algorithm == "bfs":
                path, visited = self.bfs.find_path(grid, current_pos, target_pos)
            else:
                path, visited = self.dfs.find_path(grid, current_pos, target_pos)
            
            # Draw visited cells
            for row, col in visited:
                cell_rect = pygame.Rect(
                    start_x + col * cell_size,
                    start_y + row * cell_size,
                    cell_size, cell_size
                )
                
                # Skip walls
                if grid[row][col] == 1:
                    continue
                
                # Semi-transparent overlay
                overlay = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                overlay.fill((100, 100, 255, 50))
                screen.blit(overlay, cell_rect)
            
            # Draw path
            for i in range(len(path) - 1):
                r1, c1 = path[i]
                r2, c2 = path[i + 1]
                
                pygame.draw.line(
                    screen, BLUE,
                    (start_x + c1 * cell_size + cell_size // 2,
                     start_y + r1 * cell_size + cell_size // 2),
                    (start_x + c2 * cell_size + cell_size // 2,
                     start_y + r2 * cell_size + cell_size // 2),
                    3
                )
    
    def _draw_jug_challenge(self, screen):
        """Draw water jug challenge"""
        jugs = self.current_challenge.get("jugs")
        capacities = self.current_challenge.get("capacities")
        target = self.current_challenge.get("target")
        selected_jug = self.current_challenge.get("selected_jug")
        
        # Calculate jug dimensions
        jug_width = 80
        jug_height = 160
        total_width = len(jugs) * (jug_width + 20)
        start_x = self.challenge_area_rect.centerx - total_width // 2
        jug_y = self.challenge_area_rect.centery - 50
        
        # Draw jugs
        for i, (amount, capacity) in enumerate(zip(jugs, capacities)):
            # Calculate jug position
            jug_x = start_x + i * (jug_width + 20)
            
            # Draw jug outline
            jug_rect = pygame.Rect(jug_x, jug_y, jug_width, jug_height)
            pygame.draw.rect(screen, (50, 50, 50), jug_rect)
            
            # Highlight selected jug
            border_color = YELLOW if i == selected_jug else WHITE
            border_width = 3 if i == selected_jug else 1
            pygame.draw.rect(screen, border_color, jug_rect, border_width)
            
            # Draw water
            if amount > 0:
                water_height = int(jug_height * (amount / capacity))
                water_rect = pygame.Rect(
                    jug_x, jug_y + jug_height - water_height,
                    jug_width, water_height
                )
                pygame.draw.rect(screen, BLUE, water_rect)
                
                # Draw water surface with wave effect
                wave_points = []
                for x in range(jug_x, jug_x + jug_width + 1, 5):
                    y_offset = math.sin(time.time() * 3 + x * 0.1) * 2
                    wave_points.append((x, jug_y + jug_height - water_height + y_offset))
                
                if len(wave_points) > 1:
                    pygame.draw.lines(screen, (150, 200, 255), False, wave_points, 2)
            
            # Draw capacity and current amount text
            cap_text = self.font.render(f"{capacity}L", True, WHITE)
            screen.blit(cap_text, (jug_x + jug_width // 2 - cap_text.get_width() // 2, jug_y - 25))
            
            amt_text = self.font.render(f"{amount}L", True, WHITE)
            screen.blit(amt_text, (jug_x + jug_width // 2 - amt_text.get_width() // 2, jug_y + jug_height + 5))
        
        # Draw target amount
        target_text = self.font.render(f"Target: {target}L", True, GREEN)
        screen.blit(target_text, (self.challenge_area_rect.centerx - target_text.get_width() // 2, 
                                 jug_y - 60))
        
        # Draw instructions
        instr_text = self.font.render("Click jugs to select/pour", True, WHITE)
        screen.blit(instr_text, (self.challenge_area_rect.centerx - instr_text.get_width() // 2, 
                                jug_y + jug_height + 30))
        
        # Draw water jug algorithm visualization if selected
        if self.current_algorithm == "water_jug":
            # Get solution steps
            steps = self.jug_solver.solve(capacities, [0] * len(capacities), target)
            
            if steps:
                # Draw first few steps
                y_pos = self.challenge_area_rect.bottom - 80
                pygame.draw.rect(screen, (30, 30, 50), (
                    self.challenge_area_rect.left + 10,
                    y_pos - 10,
                    self.challenge_area_rect.width - 20,
                    80
                ))
                
                step_text = self.font.render("Solution Steps:", True, WHITE)
                screen.blit(step_text, (self.challenge_area_rect.left + 20, y_pos))
                
                # Draw up to 3 steps
                for i, step in enumerate(steps[:3]):
                    step_text = self.font.render(f"{i+1}. {step[0]}", True, LIGHT_BLUE)
                    screen.blit(step_text, (self.challenge_area_rect.left + 30, y_pos + 25 + i * 20))
    
    def _draw_tictactoe_challenge(self, screen):
        """Draw tic-tac-toe challenge"""
        board = self.current_challenge.get("board")
        size = len(board)
        ai_turn = self.current_challenge.get("ai_turn", False)
        
        # Calculate board dimensions
        cell_size = min(60, (min(self.challenge_area_rect.width, self.challenge_area_rect.height) - 40) // size)
        board_width = size * cell_size
        start_x = self.challenge_area_rect.centerx - board_width // 2
        start_y = self.challenge_area_rect.centery - board_width // 2
        
        # Draw whose turn it is
        turn_text = self.font.render(
            "AI is thinking..." if ai_turn else "Your turn",
            True,
            RED if ai_turn else GREEN
        )
        screen.blit(turn_text, (self.challenge_area_rect.centerx - turn_text.get_width() // 2, 
                               start_y - 30))
        
        # Draw board
        for row in range(size):
            for col in range(size):
                cell_rect = pygame.Rect(
                    start_x + col * cell_size,
                    start_y + row * cell_size,
                    cell_size, cell_size
                )
                
                # Draw cell background
                pygame.draw.rect(screen, WHITE, cell_rect)
                pygame.draw.rect(screen, BLACK, cell_rect, 1)
                
                # Draw X or O
                if board[row][col] == 'X':
                    # Draw X
                    pygame.draw.line(
                        screen, GREEN,
                        (cell_rect.left + 10, cell_rect.top + 10),
                        (cell_rect.right - 10, cell_rect.bottom - 10),
                        3
                    )
                    pygame.draw.line(
                        screen, GREEN,
                        (cell_rect.right - 10, cell_rect.top + 10),
                        (cell_rect.left + 10, cell_rect.bottom - 10),
                        3
                    )
                elif board[row][col] == 'O':
                    # Draw O
                    pygame.draw.circle(
                        screen, RED,
                        cell_rect.center,
                        cell_size // 2 - 10,
                        3
                    )
        
        # Draw minimax visualization if selected
        if self.current_algorithm in ["minimax", "alpha_beta"] and not ai_turn:
            # Convert board to format expected by minimax
            minimax_board = []
            for row in board:
                minimax_row = []
                for cell in row:
                    if cell == 'X':
                        minimax_row.append(1)  # Player
                    elif cell == 'O':
                        minimax_row.append(2)  # AI
                    else:
                        minimax_row.append(None)  # Empty
                minimax_board.append(minimax_row)
            
            # Get visualization data
            if self.current_algorithm == "minimax":
                tree_data = self.minimax.get_decision_tree(minimax_board, 2, 1)
            else:
                tree_data = self.alpha_beta.get_pruning_stats(minimax_board, 2, 1)
            
            # Draw visualization
            self.visualizer.render_decision_tree(
                screen,
                pygame.Rect(
                    self.challenge_area_rect.left + 20,
                    self.challenge_area_rect.bottom - 100,
                    self.challenge_area_rect.width - 40,
                    80
                ),
                tree_data,
                self.current_algorithm
            )
    
    def _draw_strategy_challenge(self, screen):
        """Draw strategy game challenge"""
        board = self.current_challenge.get("board")
        selected = self.current_challenge.get("selected")
        
        # Calculate board dimensions
        board_size = len(board)
        cell_size = min(40, (min(self.challenge_area_rect.width, self.challenge_area_rect.height) - 40) // board_size)
        board_width = board_size * cell_size
        start_x = self.challenge_area_rect.centerx - board_width // 2
        start_y = self.challenge_area_rect.centery - board_width // 2
        
        # Draw board
        for row in range(board_size):
            for col in range(board_size):
                cell_rect = pygame.Rect(
                    start_x + col * cell_size,
                    start_y + row * cell_size,
                    cell_size, cell_size
                )
                
                # Draw cell background (checkerboard pattern)
                color = (200, 200, 200) if (row + col) % 2 == 0 else (150, 150, 150)
                pygame.draw.rect(screen, color, cell_rect)
                
                # Highlight selected cell
                if selected and selected == (row, col):
                    pygame.draw.rect(screen, YELLOW, cell_rect, 3)
                
                # Draw pieces
                if board[row][col] is not None:
                    piece_color = GREEN if board[row][col] == 1 else RED
                    pygame.draw.circle(
                        screen, piece_color,
                        cell_rect.center,
                        cell_size // 2 - 5
                    )
        
        # Draw instructions
        instr_text = self.font.render("Click your pieces (green) to move", True, WHITE)
        screen.blit(instr_text, (self.challenge_area_rect.centerx - instr_text.get_width() // 2, 
                                start_y - 30))
        
        # Draw alpha-beta visualization if selected
        if self.current_algorithm == "alpha_beta":
            # Get visualization data - simplified for strategy game
            pruning_stats = {
                'total_nodes': random.randint(100, 500),
                'pruned_nodes': random.randint(30, 200),
                'pruning_events': [],
                'time_taken': random.uniform(0.1, 0.5),
                'max_depth_reached': random.randint(3, 6),
                'branching_factor': random.uniform(3.5, 8.0)
            }
            
            # Draw visualization
            self.visualizer.render_pruning(
                screen,
                pygame.Rect(
                    self.challenge_area_rect.left + 20,
                    self.challenge_area_rect.bottom - 100,
                    self.challenge_area_rect.width - 40,
                    80
                ),
                pruning_stats
            )
    
    def _draw_integration_challenge(self, screen):
        """Draw integration challenge (combines multiple challenges)"""
        sub_type = self.current_challenge.get("sub_type")
        
        if sub_type == "maze":
            self._draw_maze_challenge(screen)
        elif sub_type == "water_jug":
            self._draw_jug_challenge(screen)
        elif sub_type == "tictactoe":
            self._draw_tictactoe_challenge(screen)
        elif sub_type == "strategy":
            self._draw_strategy_challenge(screen)
    
    def _draw_challenge_complete(self, screen):
        """Draw challenge completion message"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Draw completion message
        message = self.big_font.render("Challenge Complete!", True, GREEN)
        screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, 
                             SCREEN_HEIGHT // 2 - 50))
        
        # Draw score bonus
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                                SCREEN_HEIGHT // 2))
        
        # Draw next button
        next_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40, 200, 40)
        pygame.draw.rect(screen, BLUE, next_button_rect)
        pygame.draw.rect(screen, WHITE, next_button_rect, 2)
        
        next_text = self.font.render("Next Challenge", True, WHITE)
        next_text_rect = next_text.get_rect(center=next_button_rect.center)
        screen.blit(next_text, next_text_rect)
    
    def _draw_game_complete(self, screen):
        """Draw game completion message"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Draw completion message
        message = self.big_font.render("All Challenges Complete!", True, GREEN)
        screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, 
                             SCREEN_HEIGHT // 2 - 80))
        
        # Draw congratulations
        congrats = self.title_font.render("Congratulations!", True, WHITE)
        screen.blit(congrats, (SCREEN_WIDTH // 2 - congrats.get_width() // 2, 
                              SCREEN_HEIGHT // 2 - 30))
        
        # Draw final score
        score_text = self.title_font.render(f"Final Score: {self.score}", True, YELLOW)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                                SCREEN_HEIGHT // 2 + 20))
        
        # Draw message to return
        return_text = self.font.render("Press ESC to return to level select", True, WHITE)
        screen.blit(return_text, (SCREEN_WIDTH // 2 - return_text.get_width() // 2, 
                                 SCREEN_HEIGHT // 2 + 80))
    
    def reset(self):
        """Reset the level to initial state"""
        super().reset()
        self.score = 0
        self.time_remaining = 600
        self.current_algorithm = None
        self.challenge_complete = False
        self.completed = False
        
        # Reset challenge manager
        self.challenge_manager = ChallengeManager(self.difficulty)
        
        # Start first challenge
        self.start_next_challenge()

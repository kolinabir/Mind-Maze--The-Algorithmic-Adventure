"""
Alpha-Beta Pruning Algorithm Implementation

This module implements the alpha-beta pruning algorithm, which is an optimization
technique for the minimax algorithm used in game AI. Alpha-beta pruning reduces
the number of nodes evaluated in the search tree by eliminating branches that
don't need to be explored.

Key concepts:
- Alpha: Best value that the maximizer has found so far
- Beta: Best value that the minimizer has found so far
- Pruning: Skip evaluating moves when they're proven to be worse than a previously examined move
"""

import copy
import random
import time

class AlphaBetaAI:
    def __init__(self, max_depth=4):
        self.max_depth = max_depth
        self.nodes_evaluated = 0
        self.nodes_pruned = 0
        self.start_time = 0
        self.max_time = 5  # Maximum thinking time in seconds
        self.pruning_stats = {
            'total_nodes': 0,
            'pruned_nodes': 0,
            'pruning_events': [],  # Track where pruning happens
            'time_taken': 0,
            'max_depth_reached': 0,
            'branching_factor': 0
        }
    
    def get_best_move(self, board, ai_piece, player_piece):
        """
        Find the best move using alpha-beta pruning
        
        Args:
            board: 2D list representing board state
            ai_piece: AI's piece identifier
            player_piece: Player's piece identifier
            
        Returns:
            Tuple of ((from_row, from_col), (to_row, to_col)) representing the best move
        """
        # Reset statistics
        self.nodes_evaluated = 0
        self.nodes_pruned = 0
        self.start_time = time.time()
        
        # Get AI's pieces positions and possible moves
        ai_pieces = []
        for row in range(len(board)):
            for col in range(len(board[0])):
                if board[row][col] == ai_piece:
                    ai_pieces.append((row, col))
        
        if not ai_pieces:
            return None
        
        # Try moving each piece to find the best move
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        # Track branching factor
        total_branches = 0
        move_count = 0
        
        # Randomize order to avoid predictable behavior
        random.shuffle(ai_pieces)
        
        for from_pos in ai_pieces:
            from_row, from_col = from_pos
            moves = self.get_valid_moves(board, from_row, from_col, ai_piece, player_piece)
            
            # Update branching factor calculation
            total_branches += len(moves)
            if len(moves) > 0:
                move_count += 1
            
            for to_pos in moves:
                # Make a deep copy of the board to simulate the move
                new_board = copy.deepcopy(board)
                self.make_move(new_board, from_pos, to_pos)
                
                # Calculate score for this move using alpha-beta
                score = self.alpha_beta(
                    new_board, self.max_depth, False, alpha, beta, ai_piece, player_piece)
                
                if score > best_score:
                    best_score = score
                    best_move = (from_pos, to_pos)
                
                # Update alpha
                alpha = max(alpha, best_score)
                
                # Check time limit
                if time.time() - self.start_time > self.max_time:
                    break
            
            if time.time() - self.start_time > self.max_time:
                break
        
        # Calculate average branching factor
        avg_branching_factor = total_branches / max(1, move_count)
        
        # Update stats
        self.pruning_stats['branching_factor'] = avg_branching_factor
        self.pruning_stats['time_taken'] = time.time() - self.start_time
        
        return best_move
    
    def alpha_beta(self, board, depth, is_maximizing, alpha, beta, ai_piece, player_piece):
        """
        Alpha-beta pruning algorithm
        
        Args:
            board: Current board state
            depth: Current depth in search tree
            is_maximizing: Whether current player is maximizing (AI) or minimizing (player)
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            ai_piece: AI's piece identifier
            player_piece: Player's piece identifier
            
        Returns:
            Score for the current board state
        """
        # Increment node count
        self.nodes_evaluated += 1
        self.pruning_stats['total_nodes'] += 1
        
        # Update max depth reached
        current_depth = self.max_depth - depth
        self.pruning_stats['max_depth_reached'] = max(
            self.pruning_stats['max_depth_reached'], 
            current_depth
        )
        
        # Check terminal conditions
        if depth == 0 or self.is_terminal_state(board) or time.time() - self.start_time > self.max_time:
            return self.evaluate_board(board, ai_piece, player_piece)
        
        if is_maximizing:
            # AI's turn - maximize score
            value = float('-inf')
            
            # Get all possible moves for AI pieces
            for row in range(len(board)):
                for col in range(len(board[0])):
                    if board[row][col] == ai_piece:
                        moves = self.get_valid_moves(board, row, col, ai_piece, player_piece)
                        for to_pos in moves:
                            # Make a deep copy of the board to simulate the move
                            new_board = copy.deepcopy(board)
                            self.make_move(new_board, (row, col), to_pos)
                            
                            # Recursive alpha-beta call
                            eval = self.alpha_beta(
                                new_board, depth - 1, False, alpha, beta, ai_piece, player_piece)
                            value = max(value, eval)
                            alpha = max(alpha, value)
                            
                            # Alpha-beta pruning
                            if beta <= alpha:
                                self.nodes_pruned += 1
                                self.pruning_stats['pruned_nodes'] += 1
                                
                                # Record pruning event for visualization
                                self.pruning_stats['pruning_events'].append({
                                    'depth': current_depth,
                                    'alpha': alpha,
                                    'beta': beta,
                                    'is_maximizing': True,
                                    'value': value
                                })
                                
                                break
                        
                        if beta <= alpha:
                            break
                
                if beta <= alpha:
                    break
            
            return value
        
        else:
            # Player's turn - minimize score
            value = float('inf')
            
            # Get all possible moves for player pieces
            for row in range(len(board)):
                for col in range(len(board[0])):
                    if board[row][col] == player_piece:
                        moves = self.get_valid_moves(board, row, col, player_piece, ai_piece)
                        for to_pos in moves:
                            # Make a deep copy of the board to simulate the move
                            new_board = copy.deepcopy(board)
                            self.make_move(new_board, (row, col), to_pos)
                            
                            # Recursive alpha-beta call
                            eval = self.alpha_beta(
                                new_board, depth - 1, True, alpha, beta, ai_piece, player_piece)
                            value = min(value, eval)
                            beta = min(beta, value)
                            
                            # Alpha-beta pruning
                            if beta <= alpha:
                                self.nodes_pruned += 1
                                self.pruning_stats['pruned_nodes'] += 1
                                
                                # Record pruning event for visualization
                                self.pruning_stats['pruning_events'].append({
                                    'depth': current_depth,
                                    'alpha': alpha,
                                    'beta': beta,
                                    'is_maximizing': False,
                                    'value': value
                                })
                                
                                break
                        
                        if beta <= alpha:
                            break
                
                if beta <= alpha:
                    break
            
            return value
    
    def get_valid_moves(self, board, row, col, piece_type, opponent_piece):
        """Get valid moves for a piece at the given position"""
        valid_moves = []
        board_size = len(board)
        
        # Movement directions based on piece type
        directions = []
        
        if piece_type == 1:  # Player piece (moves up)
            directions = [(-1, 0), (-1, -1), (-1, 1)]
        elif piece_type == 2:  # AI piece (moves down)
            directions = [(1, 0), (1, -1), (1, 1)]
        elif piece_type > 10:  # Special piece
            directions = [
                (-1, 0), (1, 0), (0, -1), (0, 1),
                (-1, -1), (-1, 1), (1, -1), (1, 1)
            ]
        
        # Check each direction
        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            
            # Check if position is on the board
            if 0 <= new_row < board_size and 0 <= new_col < board_size:
                # Move to empty space
                if board[new_row][new_col] is None:
                    valid_moves.append((new_row, new_col))
                
                # Capture opponent's piece diagonally
                elif (abs(d_row) == 1 and abs(d_col) == 1 and 
                      board[new_row][new_col] == opponent_piece):
                    valid_moves.append((new_row, new_col))
        
        return valid_moves
    
    def make_move(self, board, from_pos, to_pos):
        """Execute a move on the board"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Move the piece
        board[to_row][to_col] = board[from_row][from_col]
        board[from_row][from_col] = None
    
    def is_terminal_state(self, board):
        """Check if the current board state is terminal (game over)"""
        board_size = len(board)
        player_pieces = 0
        ai_pieces = 0
        
        # Check if either player reached the opponent's side or has no pieces left
        for row in range(board_size):
            for col in range(board_size):
                # Count pieces
                if board[row][col] == 1:  # Player piece
                    player_pieces += 1
                    # Check if player reached the top row
                    if row == 0:
                        return True
                elif board[row][col] == 2:  # AI piece
                    ai_pieces += 1
                    # Check if AI reached the bottom row
                    if row == board_size - 1:
                        return True
        
        # Check if either side has no pieces left
        return player_pieces == 0 or ai_pieces == 0
    
    def evaluate_board(self, board, ai_piece, player_piece):
        """
        Evaluate the current board state
        
        Returns a score:
        - Positive for favorable AI positions
        - Negative for favorable player positions
        """
        board_size = len(board)
        score = 0
        
        # Check for win conditions first
        for col in range(board_size):
            # AI reached bottom row (win)
            if board[board_size-1][col] == ai_piece:
                return 1000
            # Player reached top row (loss)
            if board[0][col] == player_piece:
                return -1000
        
        # Count pieces
        ai_count = 0
        player_count = 0
        
        for row in range(board_size):
            for col in range(board_size):
                if board[row][col] == ai_piece:
                    ai_count += 1
                    # Reward progress toward the goal (bottom row)
                    score += row * 2
                    
                    # Reward controlling the center columns
                    center_bonus = abs(col - board_size // 2)
                    score -= center_bonus
                    
                elif board[row][col] == player_piece:
                    player_count += 1
                    # Penalize player progress toward their goal (top row)
                    score -= (board_size - row - 1) * 2
                    
                    # Penalize player controlling the center columns
                    center_bonus = abs(col - board_size // 2)
                    score += center_bonus
        
        # Heavily reward piece advantage
        score += (ai_count - player_count) * 10
        
        return score
    
    def get_pruning_stats(self, board, ai_piece, player_piece):
        """
        Get pruning statistics for visualization
        
        Returns:
            Dictionary with pruning statistics
        """
        # Reset statistics
        self.pruning_stats = {
            'total_nodes': 0,
            'pruned_nodes': 0,
            'pruning_events': [],
            'time_taken': 0,
            'max_depth_reached': 0,
            'branching_factor': 0
        }
        
        # Start from an empty pruning events list
        self.pruning_stats['pruning_events'] = []
        
        # Run a sample alpha-beta search to generate statistics
        start_time = time.time()
        
        # Find a valid move
        for row in range(len(board)):
            for col in range(len(board)):
                if board[row][col] == ai_piece:
                    moves = self.get_valid_moves(board, row, col, ai_piece, player_piece)
                    if moves:
                        # Make a deep copy of the board to simulate the move
                        new_board = copy.deepcopy(board)
                        self.make_move(new_board, (row, col), moves[0])
                        
                        # Run alpha-beta with reduced depth for visualization
                        self.alpha_beta(
                            new_board, min(3, self.max_depth), False, 
                            float('-inf'), float('inf'), 
                            ai_piece, player_piece
                        )
                        break
            else:
                continue
            break
        
        # Update time taken
        self.pruning_stats['time_taken'] = time.time() - start_time
        
        # Limit the number of pruning events for visualization
        if len(self.pruning_stats['pruning_events']) > 10:
            self.pruning_stats['pruning_events'] = self.pruning_stats['pruning_events'][:10]
        
        return self.pruning_stats

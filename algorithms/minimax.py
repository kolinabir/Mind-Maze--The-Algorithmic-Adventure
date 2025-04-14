import copy
import random


class MinimaxAI:
    def __init__(self, max_depth=9):
        self.max_depth = max_depth
        self.node_count = 0
        self.decision_tree = {}  # For visualization

    def get_best_move(self, board, ai_symbol, player_symbol):
        """
        Find the best move using the minimax algorithm

        Args:
            board: 2D list representing current board state
            ai_symbol: Symbol used by AI ('O' typically)
            player_symbol: Symbol used by player ('X' typically)

        Returns:
            (row, col) tuple of the best move, or None if no moves available
        """
        # Reset node count for tracking algorithm efficiency
        self.node_count = 0

        # Get all available moves
        moves = self._get_available_moves(board)
        if not moves:
            return None

        # If only one move available, return it immediately
        if len(moves) == 1:
            return moves[0]

        best_score = float("-inf")
        best_move = None

        # Try each available move
        for move in moves:
            row, col = move

            # Make a deep copy of the board to simulate the move
            new_board = copy.deepcopy(board)
            new_board[row][col] = ai_symbol

            # Calculate score for this move using minimax
            score = self._minimax(
                new_board,
                0,
                False,  # Next turn is minimizing player
                float("-inf"),
                float("inf"),
                ai_symbol,
                player_symbol,
            )

            # Update best move if better score found
            if score > best_score:
                best_score = score
                best_move = move
            # Add some randomness to equal scores for variety
            elif score == best_score and random.random() < 0.5:
                best_move = move

        return best_move

    def get_decision_tree(self, board, ai_symbol, player_symbol):
        """
        Generate a decision tree for visualization

        Returns:
            Dictionary representing the minimax decision tree
        """
        # Reset decision tree
        self.decision_tree = {
            "board": copy.deepcopy(board),
            "score": None,
            "children": [],
            "move": None,
            "is_maximizing": True,
        }

        # Get all available moves
        moves = self._get_available_moves(board)

        # Generate first level of the tree (AI's possible moves)
        for move in moves:
            row, col = move

            # Make a deep copy of the board to simulate the move
            new_board = copy.deepcopy(board)
            new_board[row][col] = ai_symbol

            child_node = {
                "board": new_board,
                "move": move,
                "score": None,
                "children": [],
                "is_maximizing": False,
            }

            # Add limited depth exploration (just one more level for player's moves)
            child_moves = self._get_available_moves(new_board)
            for child_move in child_moves[:3]:  # Limit to 3 responses for clarity
                c_row, c_col = child_move
                child_board = copy.deepcopy(new_board)
                child_board[c_row][c_col] = player_symbol

                grandchild_node = {
                    "board": child_board,
                    "move": child_move,
                    "score": self._evaluate_board(
                        child_board, ai_symbol, player_symbol
                    ),
                    "children": [],
                    "is_maximizing": True,
                }
                child_node["children"].append(grandchild_node)

            # Calculate score for this move
            if child_node["children"]:
                child_node["score"] = min(
                    child["score"] for child in child_node["children"]
                )
            else:
                child_node["score"] = self._evaluate_board(
                    new_board, ai_symbol, player_symbol
                )

            self.decision_tree["children"].append(child_node)

        # Set the root score to the maximum of children
        if self.decision_tree["children"]:
            self.decision_tree["score"] = max(
                child["score"] for child in self.decision_tree["children"]
            )

        return self.decision_tree

    def _minimax(
        self, board, depth, is_maximizing, alpha, beta, ai_symbol, player_symbol
    ):
        """
        Minimax algorithm with alpha-beta pruning

        Args:
            board: Current board state
            depth: Current depth in the search tree
            is_maximizing: Whether current player is maximizing (AI) or minimizing (player)
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            ai_symbol: Symbol used by AI
            player_symbol: Symbol used by player

        Returns:
            Score for the current board state
        """
        # Increment node count for measuring algorithm efficiency
        self.node_count += 1

        # Check terminal states
        winner = self._check_winner(board)
        if winner:
            if winner == ai_symbol:
                return 10 - depth  # AI wins (higher score for quicker wins)
            else:
                return depth - 10  # Player wins (lower score for slower losses)

        if self._is_board_full(board) or depth == self.max_depth:
            return self._evaluate_board(board, ai_symbol, player_symbol)

        available_moves = self._get_available_moves(board)

        if is_maximizing:
            # AI's turn - maximize score
            best_score = float("-inf")
            for move in available_moves:
                row, col = move

                # Make move
                new_board = copy.deepcopy(board)
                new_board[row][col] = ai_symbol

                # Recursive minimax call
                score = self._minimax(
                    new_board, depth + 1, False, alpha, beta, ai_symbol, player_symbol
                )

                best_score = max(score, best_score)

                # Alpha-beta pruning
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break

            return best_score
        else:
            # Player's turn - minimize score
            best_score = float("inf")
            for move in available_moves:
                row, col = move

                # Make move
                new_board = copy.deepcopy(board)
                new_board[row][col] = player_symbol

                # Recursive minimax call
                score = self._minimax(
                    new_board, depth + 1, True, alpha, beta, ai_symbol, player_symbol
                )

                best_score = min(score, best_score)

                # Alpha-beta pruning
                beta = min(beta, best_score)
                if beta <= alpha:
                    break

            return best_score

    def _get_available_moves(self, board):
        """Get all available moves on the board"""
        size = len(board)
        moves = []

        for row in range(size):
            for col in range(size):
                if board[row][col] is None:
                    moves.append((row, col))

        return moves

    def _is_board_full(self, board):
        """Check if the board is full"""
        for row in board:
            for cell in row:
                if cell is None:
                    return False
        return True

    def _check_winner(self, board):
        """Check if there's a winner on the board"""
        size = len(board)

        # Check rows
        for row in range(size):
            if board[row][0] is not None and all(
                board[row][j] == board[row][0] for j in range(size)
            ):
                return board[row][0]

        # Check columns
        for col in range(size):
            if board[0][col] is not None and all(
                board[i][col] == board[0][col] for i in range(size)
            ):
                return board[0][col]

        # Check main diagonal
        if board[0][0] is not None and all(
            board[i][i] == board[0][0] for i in range(size)
        ):
            return board[0][0]

        # Check other diagonal
        if board[0][size - 1] is not None and all(
            board[i][size - 1 - i] == board[0][size - 1] for i in range(size)
        ):
            return board[0][size - 1]

        # No winner
        return None

    def _evaluate_board(self, board, ai_symbol, player_symbol):
        """
        Evaluate the current board state

        Returns a score:
        - Positive for favorable AI positions
        - Negative for favorable player positions
        - 0 for neutral positions
        """
        size = len(board)
        score = 0

        # Check for immediate win or loss first
        winner = self._check_winner(board)
        if winner == ai_symbol:
            return 10
        elif winner == player_symbol:
            return -10

        # Check rows, columns, diagonals for potential wins

        # Evaluate rows
        for row in range(size):
            score += self._evaluate_line(
                [board[row][col] for col in range(size)], ai_symbol, player_symbol
            )

        # Evaluate columns
        for col in range(size):
            score += self._evaluate_line(
                [board[row][col] for row in range(size)], ai_symbol, player_symbol
            )

        # Evaluate main diagonal
        score += self._evaluate_line(
            [board[i][i] for i in range(size)], ai_symbol, player_symbol
        )

        # Evaluate other diagonal
        score += self._evaluate_line(
            [board[i][size - 1 - i] for i in range(size)], ai_symbol, player_symbol
        )

        # Bonus for center in 3x3 board
        if size == 3 and board[1][1] == ai_symbol:
            score += 2

        return score

    def _evaluate_line(self, line, ai_symbol, player_symbol):
        """
        Evaluate a line (row, column, diagonal)

        Args:
            line: List of symbols in the line
            ai_symbol: Symbol used by AI
            player_symbol: Symbol used by player

        Returns:
            Score for the line
        """
        # Count symbols
        ai_count = line.count(ai_symbol)
        player_count = line.count(player_symbol)
        empty_count = line.count(None)

        # If there's a mix of player and AI symbols, this line can't be won by either
        if ai_count > 0 and player_count > 0:
            return 0

        # AI has some symbols in the line and rest are empty
        if ai_count > 0 and player_count == 0:
            return ai_count

        # Player has some symbols in the line and rest are empty
        if player_count > 0 and ai_count == 0:
            return -player_count

        # All empty
        return 0

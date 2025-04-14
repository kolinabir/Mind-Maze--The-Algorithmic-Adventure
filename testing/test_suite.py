import pygame
import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import game modules
from game_engine import GameEngine
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from algorithms.search_algorithms import BFS, DFS
from algorithms.jug_problem import JugSolver
from algorithms.minimax import MinimaxAI
from algorithms.alpha_beta import AlphaBetaAI


class MockScreen:
    """Mock screen object for testing without actual rendering"""

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def fill(self, color):
        pass

    def blit(self, *args, **kwargs):
        pass


class AlgorithmsTest(unittest.TestCase):
    """Test cases for the game's algorithms"""

    def setUp(self):
        """Set up test environment"""
        pygame.init()
        self.screen = MockScreen(800, 600)

    def test_bfs(self):
        """Test Breadth First Search algorithm"""
        bfs = BFS()

        # Simple maze test case
        grid = [
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
        ]

        start = (0, 0)
        goal = (4, 4)

        path, visited = bfs.find_path(grid, start, goal)

        # Check if path exists
        self.assertIsNotNone(path, "BFS should find a path in this maze")
        self.assertTrue(len(path) > 0, "Path should contain at least one node")

        # Check if path starts and ends correctly
        self.assertEqual(path[0], start, "Path should start at the start point")
        self.assertEqual(path[-1], goal, "Path should end at the goal point")

        # Check if path avoids walls
        for y, x in path:
            self.assertEqual(grid[y][x], 0, "Path should only go through empty cells")

        # Verify BFS properties - shortest path
        self.assertEqual(len(path), 9, "BFS should find the shortest path with 9 steps")

    def test_dfs(self):
        """Test Depth First Search algorithm"""
        dfs = DFS()

        # Simple maze test case
        grid = [
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
        ]

        start = (0, 0)
        goal = (4, 4)

        path, visited = dfs.find_path(grid, start, goal)

        # Check if path exists
        self.assertIsNotNone(path, "DFS should find a path in this maze")
        self.assertTrue(len(path) > 0, "Path should contain at least one node")

        # Check if path starts and ends correctly
        self.assertEqual(path[0], start, "Path should start at the start point")
        self.assertEqual(path[-1], goal, "Path should end at the goal point")

        # Check if path avoids walls
        for y, x in path:
            self.assertEqual(grid[y][x], 0, "Path should only go through empty cells")

        # Note: Not testing path length since DFS doesn't guarantee shortest path

    def test_jug_problem(self):
        """Test Water Jug Problem solver"""
        jug_solver = JugSolver()

        # Classic 5,3 jug problem to measure 4
        jugs = (5, 3)
        target = 4

        steps = jug_solver.solve(jugs, target)

        # Check if solution exists
        self.assertIsNotNone(steps, "Should find a solution to the jug problem")
        self.assertTrue(len(steps) > 0, "Solution should have at least one step")

        # Simulate the solution to verify correctness
        jug1 = 0
        jug2 = 0

        for action, params in steps:
            if action == "fill":
                jug_index = params[0]
                if jug_index == 0:
                    jug1 = jugs[0]
                else:
                    jug2 = jugs[1]

            elif action == "empty":
                jug_index = params[0]
                if jug_index == 0:
                    jug1 = 0
                else:
                    jug2 = 0

            elif action == "pour":
                from_jug, to_jug = params
                if from_jug == 0 and to_jug == 1:
                    # Pour from jug1 to jug2
                    amount = min(jug1, jugs[1] - jug2)
                    jug1 -= amount
                    jug2 += amount
                else:
                    # Pour from jug2 to jug1
                    amount = min(jug2, jugs[0] - jug1)
                    jug2 -= amount
                    jug1 += amount

        # Check if target was achieved
        self.assertTrue(
            jug1 == target or jug2 == target,
            "Solution should result in one jug containing the target amount",
        )

    def test_minimax(self):
        """Test Minimax algorithm for tic-tac-toe"""
        minimax = MinimaxAI(3)  # Depth 3

        # Empty board
        board = [[None, None, None], [None, None, None], [None, None, None]]

        # Get best move as player 1
        move = minimax.get_best_move(board, 1, 2)

        # Best first move should be center or corner
        self.assertTrue(
            move in [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)],
            "First move should be center or corner",
        )

        # Test blocking move
        board = [[1, None, None], [1, 2, None], [None, None, None]]

        # Player 2 should block player 1's win
        move = minimax.get_best_move(board, 2, 1)
        self.assertEqual(move, (2, 0), "AI should block the win")

        # Test winning move
        board = [[2, None, None], [2, 1, None], [None, 1, 1]]

        # Player 2 should take the winning move
        move = minimax.get_best_move(board, 2, 1)
        self.assertEqual(move, (0, 2), "AI should take the winning move")

    def test_alpha_beta(self):
        """Test Alpha-Beta pruning algorithm"""
        alpha_beta = AlphaBetaAI(3)  # Depth 3

        # Empty board
        board = [[None, None, None], [None, None, None], [None, None, None]]

        # Get best move as player 1
        move = alpha_beta.get_best_move(board, 1, 2)

        # Best first move should be center or corner
        self.assertTrue(
            move in [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)],
            "First move should be center or corner",
        )

        # Test blocking move
        board = [[1, None, None], [1, 2, None], [None, None, None]]

        # Player 2 should block player 1's win
        move = alpha_beta.get_best_move(board, 2, 1)
        self.assertEqual(move, (2, 0), "AI should block the win")

        # Test winning move
        board = [[2, None, None], [2, 1, None], [None, 1, 1]]

        # Player 2 should take the winning move
        move = alpha_beta.get_best_move(board, 2, 1)
        self.assertEqual(move, (0, 2), "AI should take the winning move")

    def tearDown(self):
        """Clean up after tests"""
        pygame.quit()


class GameIntegrationTest(unittest.TestCase):
    """Integration tests for main game systems"""

    def setUp(self):
        """Set up test environment"""
        pygame.init()
        # Use a smaller screen for testing
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    def test_game_engine_creation(self):
        """Test GameEngine initialization"""
        # Create game engine without actual screen
        game = GameEngine(self.screen)

        # Check if core systems are initialized
        self.assertIsNotNone(game.state_manager, "State manager should be initialized")
        self.assertIsNotNone(game.assets, "Asset manager should be initialized")

    def tearDown(self):
        """Clean up after tests"""
        pygame.quit()


if __name__ == "__main__":
    unittest.main()

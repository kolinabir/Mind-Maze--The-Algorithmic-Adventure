import random

class ChallengeManager:
    def __init__(self, difficulty=1):
        self.difficulty = difficulty
        self.challenges = []
        self.current_challenge_index = 0
        
        # Generate challenges based on difficulty
        self._generate_challenges()
    
    def _generate_challenges(self):
        """Generate a sequence of challenges"""
        # Base challenges that will be included
        base_challenges = [
            self._generate_maze_challenge,
            self._generate_water_jug_challenge,
            self._generate_tictactoe_challenge,
            self._generate_strategy_challenge
        ]
        
        # Set total number of challenges based on difficulty
        if self.difficulty == 1:
            challenge_count = 4  # One of each
            integration_chance = 0  # No integration challenges
        elif self.difficulty == 2:
            challenge_count = 5
            integration_chance = 0.2  # 20% chance of integration
        elif self.difficulty == 3:
            challenge_count = 6
            integration_chance = 0.3
        else:  # Difficulty 4
            challenge_count = 7
            integration_chance = 0.4
        
        # Make sure we have at least one of each base challenge
        for generator in base_challenges:
            self.challenges.append(generator())
        
        # Add remaining challenges
        remaining = challenge_count - len(self.challenges)
        for _ in range(remaining):
            # Decide if this will be an integration challenge
            if random.random() < integration_chance:
                self.challenges.append(self._generate_integration_challenge())
            else:
                # Pick a random challenge type
                generator = random.choice(base_challenges)
                self.challenges.append(generator())
        
        # Shuffle challenges
        random.shuffle(self.challenges)
    
    def _generate_maze_challenge(self):
        """Create a maze challenge"""
        # Generate a small maze grid
        size = 5 + self.difficulty
        grid = [[0 for _ in range(size)] for _ in range(size)]
        
        # Add some walls
        for _ in range(size * size // 3):
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)
            if (x, y) != (1, 1) and (x, y) != (size - 2, size - 2):
                grid[y][x] = 1
        
        # Ensure a path exists (simplified)
        for x in range(1, size - 1):
            grid[1][x] = 0  # Clear top row path
            grid[size - 2][x] = 0  # Clear bottom row path
        
        for y in range(1, size - 1):
            grid[y][1] = 0  # Clear left column path
            grid[y][size - 2] = 0  # Clear right column path
        
        return {
            "type": "maze",
            "grid": grid,
            "current_pos": (1, 1),
            "target_pos": (size - 2, size - 2),
            "required_algorithm": random.choice(["bfs", "dfs"]),
            "description": "Navigate through the maze to reach the target"
        }
    
    def _generate_water_jug_challenge(self):
        """Create a water jug challenge"""
        if self.difficulty == 1:
            # Classic 3,5 to get 4 liters
            capacities = [3, 5]
            target = 4
        elif self.difficulty == 2:
            # 3 jugs
            capacities = [3, 5, 8]
            target = 4
        elif self.difficulty == 3:
            capacities = [5, 7, 10]
            target = 6
        else:
            capacities = [3, 7, 9, 12]
            target = 10
        
        return {
            "type": "water_jug",
            "jugs": [0] * len(capacities),  # Start with empty jugs
            "capacities": capacities,
            "target": target,
            "selected_jug": None,
            "required_algorithm": "water_jug",
            "description": f"Measure exactly {target}L using the available jugs"
        }
    
    def _generate_tictactoe_challenge(self):
        """Create a tic-tac-toe challenge"""
        size = 3
        if self.difficulty >= 3:
            # 4x4 board for higher difficulties
            size = 4
        
        # Create empty board
        board = [[None for _ in range(size)] for _ in range(size)]
        
        # For higher difficulties, pre-fill some positions
        if self.difficulty >= 2:
            # Add some random X and O positions
            for _ in range(self.difficulty):
                x = random.randint(0, size - 1)
                y = random.randint(0, size - 1)
                if random.random() < 0.7:
                    board[y][x] = 'X'  # Player
                else:
                    board[y][x] = 'O'  # AI
        
        return {
            "type": "tictactoe",
            "board": board,
            "ai_turn": False,
            "required_algorithm": random.choice(["minimax", "alpha_beta"]),
            "description": "Get three in a row before the AI does"
        }
    
    def _generate_strategy_challenge(self):
        """Create a strategy game challenge"""
        size = 6 + self.difficulty
        board = [[None for _ in range(size)] for _ in range(size)]
        
        # Place player pieces at bottom
        for col in range(size):
            if col % 2 == 0 and random.random() < 0.8:
                board[size - 1][col] = 1
                if size - 2 >= 0 and random.random() < 0.6:
                    board[size - 2][col] = 1
        
        # Place AI pieces at top
        for col in range(size):
            if col % 2 == 1 and random.random() < 0.8:
                board[0][col] = 2
                if random.random() < 0.6:
                    board[1][col] = 2
        
        return {
            "type": "strategy",
            "board": board,
            "selected": None,
            "required_algorithm": "alpha_beta",
            "description": "Reach the top row with any piece"
        }
    
    def _generate_integration_challenge(self):
        """Create an integration challenge that combines multiple algorithms"""
        # Pick a base challenge type for the integration challenge
        base_type = random.choice(["maze", "water_jug", "tictactoe", "strategy"])
        
        if base_type == "maze":
            challenge = self._generate_maze_challenge()
        elif base_type == "water_jug":
            challenge = self._generate_water_jug_challenge()
        elif base_type == "tictactoe":
            challenge = self._generate_tictactoe_challenge()
        else:  # strategy
            challenge = self._generate_strategy_challenge()
        
        # Modify it to be an integration challenge
        challenge["type"] = "integration"
        challenge["sub_type"] = base_type
        challenge["required_algorithm"] = "integration"
        challenge["description"] = f"Integration Challenge: {challenge['description']}"
        
        return challenge
    
    def get_next_challenge(self):
        """Get the next challenge in the sequence"""
        if self.current_challenge_index < len(self.challenges):
            challenge = self.challenges[self.current_challenge_index]
            self.current_challenge_index += 1
            return challenge
        return None
    
    def reset(self):
        """Reset the challenge sequence"""
        self.current_challenge_index = 0
        self._generate_challenges()

import pygame
import random
import math
import time
import heapq
from levels.base_level import BaseLevel
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BLACK,
    WHITE,
    GREEN,
    RED,
    BLUE,
    YELLOW,
    LIGHT_BLUE,
)


class IntegrationLevel(BaseLevel):
    def __init__(self, game_engine, asset_manager):
        super().__init__(game_engine, asset_manager)

        # Game settings
        self.difficulty = 1

        # Grid settings - reduce size to fit on screen better
        self.grid_size = 16  # Reduced from 20
        self.cell_size = 28  # Reduced from 30

        # Initialize the game state
        self.reset()

        # Instructions modal
        self.show_instructions = True
        self.instructions_read = False

        self.win_rate = 50.0  # Initial win rate percentage
        self.moves_made = 0  # Track total moves made
        self.optimal_path_length = 0  # Length of optimal path

    def reset(self):
        """Reset the level to initial state"""
        super().reset()

        # Set difficulty which affects game parameters
        self.set_difficulty(self.difficulty)

        # Initialize the grid
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        # Player attributes
        self.player_pos = (self.grid_size - 2, 1)
        self.target_pos = (1, self.grid_size - 2)
        self.player_score = 0
        self.moves_remaining = 100
        self.collecting_mode = False

        # Generate the maze with walls and collectibles
        self._generate_maze()

        # Items and enemies
        self.collectibles = []
        self.enemies = []
        self._place_collectibles(15 + self.difficulty * 5)
        self._generate_enemies(3 + self.difficulty)

        # Pathfinding attributes
        self.current_path = []
        self.visited_nodes = set()
        self.show_path = False

        # Level status
        self.game_over = False
        self.time_limit = 180 - (
            self.difficulty * 15
        )  # Decreasing time with difficulty
        self.time_remaining = self.time_limit
        self.completed = False

        # UI elements
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 36)

        # Power-ups
        self.power_ups = {"teleport": 1, "reveal_path": 2, "freeze_enemies": 1}
        self.freeze_time = 0
        self.reveal_time = 0

        # Win rate tracking
        self.win_rate = 50.0
        self.moves_made = 0

    def set_difficulty(self, level):
        """Set the difficulty level"""
        self.difficulty = max(1, min(level, 4))  # Clamp between 1-4

        # Adjust game parameters based on difficulty
        if level == 1:  # Easy
            self.enemy_speed = 0.5
            self.enemy_intelligence = 0.3
        elif level == 2:  # Medium
            self.enemy_speed = 0.7
            self.enemy_intelligence = 0.5
        elif level == 3:  # Hard
            self.enemy_speed = 0.9
            self.enemy_intelligence = 0.7
        else:  # Expert
            self.enemy_speed = 1.1
            self.enemy_intelligence = 0.9

    def _generate_maze(self):
        """Generate a maze using recursive division"""
        # Start with empty grid
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                # Create boundary walls
                if (
                    x == 0
                    or y == 0
                    or x == self.grid_size - 1
                    or y == self.grid_size - 1
                ):
                    self.grid[y][x] = 1  # Wall
                else:
                    self.grid[y][x] = 0  # Empty space

        # Clear player starting position and target
        player_y, player_x = self.player_pos
        target_y, target_x = self.target_pos

        # Clear area around player and target
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                py, px = player_y + dy, player_x + dx
                ty, tx = target_y + dy, target_x + dx
                if 0 <= py < self.grid_size and 0 <= px < self.grid_size:
                    self.grid[py][px] = 0
                if 0 <= ty < self.grid_size and 0 <= tx < self.grid_size:
                    self.grid[ty][tx] = 0

        # Recursively divide the maze
        self._divide_maze(1, 1, self.grid_size - 2, self.grid_size - 2)

        # Make sure there is a valid path from start to finish by using A*
        path = self._find_path_astar(self.player_pos, self.target_pos)
        if not path:
            # If no path, clear some walls to ensure there is one
            self._ensure_path_exists()

    def _divide_maze(self, x1, y1, x2, y2):
        """Recursively divide the maze"""
        width = x2 - x1
        height = y2 - y1

        # Base case: If the room is too small to divide further
        if width < 3 or height < 3:
            return

        # Choose a random point to create a wall
        wx = random.randint(x1 + 1, x2 - 2)
        wy = random.randint(y1 + 1, y2 - 2)

        # Choose a random point for a passage
        px1, py1 = random.randint(x1, wx - 1), wy
        px2, py2 = random.randint(wx + 1, x2), wy
        px3, py3 = wx, random.randint(y1, wy - 1)
        px4, py4 = wx, random.randint(wy + 1, y2)

        # Create the walls
        for x in range(x1, x2 + 1):
            if (
                self.grid[wy][x] == 0
                and (x, wy) != (px1, py1)
                and (x, wy) != (px2, py2)
            ):
                self.grid[wy][x] = 1

        for y in range(y1, y2 + 1):
            if (
                self.grid[y][wx] == 0
                and (wx, y) != (px3, py3)
                and (wx, y) != (px4, py4)
            ):
                self.grid[y][wx] = 1

        # Recursively divide the four new rooms
        self._divide_maze(x1, y1, wx - 1, wy - 1)
        self._divide_maze(wx + 1, y1, x2, wy - 1)
        self._divide_maze(x1, wy + 1, wx - 1, y2)
        self._divide_maze(wx + 1, wy + 1, x2, y2)

    def _ensure_path_exists(self):
        """Make sure there's a path from start to finish"""
        current = self.player_pos
        target = self.target_pos

        while current != target:
            # Get the direction to move toward the target
            y, x = current
            ty, tx = target

            # Decide which direction to move
            if abs(ty - y) > abs(tx - x):
                # Move vertically
                dy = 1 if ty > y else -1
                dx = 0
            else:
                # Move horizontally
                dy = 0
                dx = 1 if tx > x else -1

            # Move to the next position
            next_y, next_x = y + dy, x + dx

            # Clear the wall if there is one
            self.grid[next_y][next_x] = 0

            # Update current position
            current = (next_y, next_x)

    def _place_collectibles(self, count):
        """Place collectibles around the maze"""
        self.collectibles = []
        empty_cells = []

        # Find all empty cells
        for y in range(1, self.grid_size - 1):
            for x in range(1, self.grid_size - 1):
                if (
                    self.grid[y][x] == 0
                    and (y, x) != self.player_pos
                    and (y, x) != self.target_pos
                ):
                    empty_cells.append((y, x))

        # Place collectibles
        if empty_cells:
            for _ in range(min(count, len(empty_cells))):
                pos = random.choice(empty_cells)
                value = random.randint(5, 20) * self.difficulty
                self.collectibles.append(
                    {"pos": pos, "value": value, "collected": False}
                )
                empty_cells.remove(pos)

    def _generate_enemies(self, count):
        """Generate enemies with different behaviors"""
        self.enemies = []
        empty_cells = []

        # Find all empty cells that are at least 5 steps away from player
        for y in range(1, self.grid_size - 1):
            for x in range(1, self.grid_size - 1):
                if (
                    self.grid[y][x] == 0
                    and (y, x) != self.player_pos
                    and (y, x) != self.target_pos
                ):
                    if abs(y - self.player_pos[0]) + abs(x - self.player_pos[1]) > 5:
                        empty_cells.append((y, x))

        # Place enemies with more hunters
        if empty_cells:
            # Adjust distribution: more hunters but keep game winnable
            hunter_count = min(count // 2 + self.difficulty, len(empty_cells) // 3)
            patrol_count = count // 3
            random_count = count - hunter_count - patrol_count

            # Place hunters (more dangerous)
            for i in range(min(hunter_count, len(empty_cells))):
                pos = random.choice(empty_cells)
                enemy = {
                    "pos": pos,
                    "type": "hunter",
                    "move_timer": 0,
                    "path": [],
                    "patrol_points": [],
                }
                self.enemies.append(enemy)
                empty_cells.remove(pos)

            # Place patrol enemies
            for i in range(min(patrol_count, len(empty_cells))):
                pos = random.choice(empty_cells)
                enemy = {
                    "pos": pos,
                    "type": "patrol",
                    "move_timer": 0,
                    "path": [],
                    "patrol_points": [],
                }

                # For patrol enemies, set up patrol points
                # Find patrol points
                patrol_points = [pos]
                for _ in range(3):
                    found = False
                    for attempt in range(20):
                        dy, dx = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                        ny, nx = (
                            patrol_points[-1][0] + dy,
                            patrol_points[-1][1] + dx,
                        )

                        # Check if valid cell
                        if (
                            0 < ny < self.grid_size - 1
                            and 0 < nx < self.grid_size - 1
                            and self.grid[ny][nx] == 0
                        ):
                            patrol_points.append((ny, nx))
                            found = True
                            break

                    if not found:
                        break

                enemy["patrol_points"] = patrol_points
                enemy["patrol_index"] = 0
                enemy["patrol_direction"] = 1

                self.enemies.append(enemy)
                empty_cells.remove(pos)

        # Calculate initial optimal path length for win rate calculation
        path = self._find_path_astar(self.player_pos, self.target_pos)
        self.optimal_path_length = len(path) if path else self.grid_size * 2

    def _find_path_astar(self, start, end):
        """Find path using A* algorithm"""
        if start == end:
            return [start]

        # Initialize open and closed sets
        open_list = [(0, 0, start, [])]  # (f_score, g_score, position, path)
        closed_set = set()

        while open_list:
            # Get node with lowest f_score
            f_score, g_score, current, path = heapq.heappop(open_list)

            # If we reached the target
            if current == end:
                return path + [current]

            # Skip if already visited
            if current in closed_set:
                continue

            # Mark as visited
            closed_set.add(current)

            # Check all neighbors
            for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                ny, nx = current[0] + dy, current[1] + dx

                # Check if valid move
                if (
                    0 <= ny < self.grid_size
                    and 0 <= nx < self.grid_size
                    and self.grid[ny][nx] != 1
                    and (ny, nx) not in closed_set
                ):

                    # Calculate scores
                    new_g = g_score + 1
                    new_h = abs(ny - end[0]) + abs(nx - end[1])
                    new_f = new_g + new_h

                    # Add to open list
                    heapq.heappush(
                        open_list, (new_f, new_g, (ny, nx), path + [current])
                    )

        # No path found
        return []

    def handle_event(self, event):
        """Handle user input"""
        # Handle instructions modal first
        if self.show_instructions:
            if event.type == pygame.KEYDOWN or (
                event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            ):
                self.show_instructions = False
                self.instructions_read = True
                return

        if self.game_over:
            # Allow restart with any key
            if event.type == pygame.KEYDOWN:
                self.reset()
            return

        if event.type == pygame.KEYDOWN:
            # Movement
            if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                self._handle_movement(event.key)

            # Toggle path visualization
            elif event.key == pygame.K_SPACE:
                self.show_path = not self.show_path
                if self.show_path:
                    self.current_path = self._find_path_astar(
                        self.player_pos, self.target_pos
                    )

            # Toggle collectible mode
            elif event.key == pygame.K_c:
                self.collecting_mode = not self.collecting_mode
                if self.collecting_mode:
                    # Find nearest collectible
                    nearest = self._find_nearest_collectible()
                    if nearest:
                        self.current_path = self._find_path_astar(
                            self.player_pos, nearest["pos"]
                        )
                else:
                    # Path to target
                    self.current_path = self._find_path_astar(
                        self.player_pos, self.target_pos
                    )

            # Use power-ups
            elif event.key == pygame.K_1 and self.power_ups["teleport"] > 0:
                self._use_teleport()
            elif event.key == pygame.K_2 and self.power_ups["reveal_path"] > 0:
                self._use_reveal_path()
            elif event.key == pygame.K_3 and self.power_ups["freeze_enemies"] > 0:
                self._use_freeze_enemies()

    def _handle_movement(self, key):
        """Handle player movement"""
        if self.moves_remaining <= 0:
            return

        y, x = self.player_pos
        new_y, new_x = y, x

        if key == pygame.K_UP:
            new_y -= 1
        elif key == pygame.K_DOWN:
            new_y += 1
        elif key == pygame.K_LEFT:
            new_x -= 1
        elif key == pygame.K_RIGHT:
            new_x += 1

        # Check if the move is valid
        if (
            0 <= new_y < self.grid_size
            and 0 <= new_x < self.grid_size
            and self.grid[new_y][new_x] != 1
        ):

            # Move player
            self.player_pos = (new_y, new_x)
            self.moves_remaining -= 1
            self.moves_made += 1

            # Update win rate calculation
            self._update_win_rate()

            # Check for collectibles
            self._check_collectibles()

            # Check for target
            if self.player_pos == self.target_pos:
                self.completed = True
                self.game_over = True
                self.player_score += 500 + self.difficulty * 100

            # Recalculate path if needed
            if self.show_path or self.collecting_mode:
                if self.collecting_mode:
                    nearest = self._find_nearest_collectible()
                    if nearest:
                        self.current_path = self._find_path_astar(
                            self.player_pos, nearest["pos"]
                        )
                    else:
                        self.current_path = self._find_path_astar(
                            self.player_pos, self.target_pos
                        )
                else:
                    self.current_path = self._find_path_astar(
                        self.player_pos, self.target_pos
                    )

    def _check_collectibles(self):
        """Check if player collected any collectibles"""
        for item in self.collectibles:
            if not item["collected"] and item["pos"] == self.player_pos:
                item["collected"] = True
                self.player_score += item["value"]

                # Chance to get a power-up
                if random.random() < 0.3:
                    power_up = random.choice(list(self.power_ups.keys()))
                    self.power_ups[power_up] += 1

    def _find_nearest_collectible(self):
        """Find the nearest uncollected collectible"""
        uncollected = [item for item in self.collectibles if not item["collected"]]
        if not uncollected:
            return None

        # Sort by Manhattan distance
        uncollected.sort(
            key=lambda item: abs(item["pos"][0] - self.player_pos[0])
            + abs(item["pos"][1] - self.player_pos[1])
        )

        return uncollected[0]

    def _use_teleport(self):
        """Use teleport power-up"""
        self.power_ups["teleport"] -= 1

        # Find a safe spot to teleport to
        empty_cells = []
        for y in range(1, self.grid_size - 1):
            for x in range(1, self.grid_size - 1):
                if self.grid[y][x] == 0 and (y, x) != self.player_pos:
                    # Make sure it's not too close to enemies
                    safe = True
                    for enemy in self.enemies:
                        ey, ex = enemy["pos"]
                        if abs(y - ey) + abs(x - ex) < 3:
                            safe = False
                            break

                    if safe:
                        empty_cells.append((y, x))

        if empty_cells:
            # Pick a cell that's closer to the target if possible
            target_y, target_x = self.target_pos
            empty_cells.sort(
                key=lambda pos: abs(pos[0] - target_y) + abs(pos[1] - target_x)
            )

            # Teleport to a cell in the first third of sorted cells (closer to target)
            idx = random.randint(0, len(empty_cells) // 3)
            self.player_pos = empty_cells[min(idx, len(empty_cells) - 1)]

            # Recalculate path if needed
            if self.show_path or self.collecting_mode:
                if self.collecting_mode:
                    nearest = self._find_nearest_collectible()
                    if nearest:
                        self.current_path = self._find_path_astar(
                            self.player_pos, nearest["pos"]
                        )
                    else:
                        self.current_path = self._find_path_astar(
                            self.player_pos, self.target_pos
                        )
                else:
                    self.current_path = self._find_path_astar(
                        self.player_pos, self.target_pos
                    )

    def _use_reveal_path(self):
        """Use reveal path power-up"""
        self.power_ups["reveal_path"] -= 1
        self.show_path = True
        self.reveal_time = 10.0  # Show path for 10 seconds

        # Calculate optimal path to target
        if self.collecting_mode:
            # Find path that collects as many collectibles as possible
            self.current_path = self._find_collecting_path()
        else:
            self.current_path = self._find_path_astar(self.player_pos, self.target_pos)

    def _use_freeze_enemies(self):
        """Use freeze enemies power-up"""
        self.power_ups["freeze_enemies"] -= 1
        self.freeze_time = 8.0  # Freeze for 8 seconds

    def _find_collecting_path(self):
        """Find a path that collects multiple collectibles"""
        # TODO: This is a simplification - ideally would use TSP-like algorithm
        # For now, we'll use a greedy approach
        uncollected = [item for item in self.collectibles if not item["collected"]]
        if not uncollected:
            return self._find_path_astar(self.player_pos, self.target_pos)

        current = self.player_pos
        full_path = []
        remaining = 3  # Limit to 3 collectibles for performance

        while uncollected and remaining > 0:
            # Find nearest collectible
            uncollected.sort(
                key=lambda item: abs(item["pos"][0] - current[0])
                + abs(item["pos"][1] - current[1])
            )

            next_item = uncollected[0]
            path = self._find_path_astar(current, next_item["pos"])

            if path:
                # Add path to next collectible (excluding start point if not the first segment)
                if full_path:
                    full_path.extend(path[1:])
                else:
                    full_path.extend(path)

                current = next_item["pos"]
                uncollected.remove(next_item)
                remaining -= 1
            else:
                break

        # Finally, add path to target
        path_to_target = self._find_path_astar(current, self.target_pos)
        if path_to_target:
            full_path.extend(path_to_target[1:])

        return full_path

    def update(self, dt):
        """Update game state"""
        if self.game_over:
            return

        # Update timer
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.game_over = True

        # Update power-up timers
        if self.freeze_time > 0:
            self.freeze_time -= dt
        if self.reveal_time > 0:
            self.reveal_time -= dt
            if self.reveal_time <= 0:
                self.show_path = False

        # Update enemies if not frozen
        if self.freeze_time <= 0:
            for enemy in self.enemies:
                enemy["move_timer"] += dt * self.enemy_speed

                # Move enemy when timer exceeds threshold
                if enemy["move_timer"] >= 1.0:
                    enemy["move_timer"] = 0
                    self._move_enemy(enemy)

        # Check if player was caught by enemy
        self._check_enemy_collision()

    def _move_enemy(self, enemy):
        """Move an enemy based on its type"""
        y, x = enemy["pos"]

        if enemy["type"] == "hunter":
            # Hunter enemies try to move toward the player
            if random.random() < self.enemy_intelligence:
                # Use pathfinding
                path = self._find_path_astar(enemy["pos"], self.player_pos)
                if path and len(path) > 1:
                    enemy["pos"] = path[1]
                    return

            # Fallback - move toward player
            py, px = self.player_pos
            moves = []

            # Try to move closer to player
            if py < y and self.grid[y - 1][x] != 1:
                moves.append((y - 1, x))
            if py > y and self.grid[y + 1][x] != 1:
                moves.append((y + 1, x))
            if px < x and self.grid[y][x - 1] != 1:
                moves.append((y, x - 1))
            if px > x and self.grid[y][x + 1] != 1:
                moves.append((y, x + 1))

            # If no good moves, try any valid move
            if not moves:
                for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    ny, nx = y + dy, x + dx
                    if (
                        0 <= ny < self.grid_size
                        and 0 <= nx < self.grid_size
                        and self.grid[ny][nx] != 1
                    ):
                        moves.append((ny, nx))

            if moves:
                enemy["pos"] = random.choice(moves)

        elif enemy["type"] == "patrol":
            # Patrol enemies follow a predetermined path
            if not enemy["patrol_points"]:
                return

            # Get next patrol point
            next_idx = enemy["patrol_index"] + enemy["patrol_direction"]

            # Check bounds and reverse if needed
            if next_idx < 0 or next_idx >= len(enemy["patrol_points"]):
                enemy["patrol_direction"] *= -1
                next_idx = enemy["patrol_index"] + enemy["patrol_direction"]

            # Update position and index
            enemy["pos"] = enemy["patrol_points"][next_idx]
            enemy["patrol_index"] = next_idx

        else:  # Random movement
            # Try to move in a random direction
            for _ in range(4):
                dy, dx = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                ny, nx = y + dy, x + dx

                if (
                    0 <= ny < self.grid_size
                    and 0 <= nx < self.grid_size
                    and self.grid[ny][nx] != 1
                ):
                    enemy["pos"] = (ny, nx)
                    break

    def _check_enemy_collision(self):
        """Check if player collided with an enemy"""
        for enemy in self.enemies:
            if enemy["pos"] == self.player_pos:
                self.player_score -= 50
                self.moves_remaining = max(0, self.moves_remaining - 10)

                # Teleport the player to a safe spot
                self._emergency_teleport()
                break

    def _emergency_teleport(self):
        """Teleport player after enemy collision"""
        safe_cells = []

        # Find cells that are empty and away from enemies
        for y in range(1, self.grid_size - 1):
            for x in range(1, self.grid_size - 1):
                if self.grid[y][x] == 0:
                    # Check distance from enemies
                    safe = True
                    for enemy in self.enemies:
                        ey, ex = enemy["pos"]
                        if abs(y - ey) + abs(x - ex) < 5:
                            safe = False
                            break

                    if safe:
                        safe_cells.append((y, x))

        if safe_cells:
            self.player_pos = random.choice(safe_cells)
        else:
            # If no safe cells, try to move closer to target
            self.player_pos = self._find_safer_spot()

    def _find_safer_spot(self):
        """Find a safer spot when no completely safe spots exist"""
        current_y, current_x = self.player_pos

        # Try adjacent cells
        for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            ny, nx = current_y + dy, current_x + dx

            if (
                0 <= ny < self.grid_size
                and 0 <= nx < self.grid_size
                and self.grid[ny][nx] != 1
            ):

                # Check if enemies are on this cell
                occupied = False
                for enemy in self.enemies:
                    if enemy["pos"] == (ny, nx):
                        occupied = True
                        break

                if not occupied:
                    return (ny, nx)

        # If all adjacent cells are unsafe, return current position
        return self.player_pos

    def render(self, screen):
        """Render the game"""
        # Fill background
        screen.fill((20, 30, 40))

        # Draw title
        title = self.title_font.render("PATHFINDER ADVENTURE", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))

        # Calculate board dimensions
        board_width = self.grid_size * self.cell_size
        board_height = self.grid_size * self.cell_size
        board_left = (SCREEN_WIDTH - board_width) // 2
        board_top = 50

        # Draw game statistics (time, score, moves)
        stats_y = board_top + board_height + 10

        # Time
        time_text = self.font.render(
            f"Time: {int(self.time_remaining // 60):02d}:{int(self.time_remaining % 60):02d}",
            True,
            WHITE if self.time_remaining > 30 else RED,
        )
        screen.blit(time_text, (board_left, stats_y))

        # Score
        score_text = self.font.render(f"Score: {self.player_score}", True, WHITE)
        screen.blit(
            score_text, (board_left + board_width - score_text.get_width(), stats_y)
        )

        # Win rate - add to display
        win_color = (
            GREEN if self.win_rate > 60 else YELLOW if self.win_rate > 30 else RED
        )
        win_rate_text = self.font.render(
            f"Win Rate: {self.win_rate:.1f}%", True, win_color
        )
        screen.blit(win_rate_text, (board_left, stats_y + 30))

        # Draw progress bar for win rate
        bar_width = 100
        bar_height = 8
        bar_x = board_left + win_rate_text.get_width() + 20
        bar_y = stats_y + 36

        # Background bar
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))

        # Fill bar based on win rate
        fill_width = int(bar_width * (self.win_rate / 100.0))
        pygame.draw.rect(screen, win_color, (bar_x, bar_y, fill_width, bar_height))

        # Border
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

        # Moves
        moves_text = self.font.render(f"Moves: {self.moves_remaining}", True, WHITE)
        screen.blit(
            moves_text,
            (board_left + (board_width - moves_text.get_width()) // 2, stats_y),
        )

        # Draw grid
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                # Calculate cell position
                cell_x = board_left + x * self.cell_size
                cell_y = board_top + y * self.cell_size
                cell_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)

                # Draw cell based on type
                if self.grid[y][x] == 1:  # Wall
                    pygame.draw.rect(screen, (80, 80, 100), cell_rect)
                else:  # Empty space
                    pygame.draw.rect(screen, (40, 40, 50), cell_rect)

                # Draw cell border
                pygame.draw.rect(screen, (30, 30, 30), cell_rect, 1)

        # Draw optimal path if requested
        if self.show_path and self.current_path:
            for i in range(len(self.current_path) - 1):
                start_y, start_x = self.current_path[i]
                end_y, end_x = self.current_path[i + 1]

                # Calculate pixel positions
                start_px = board_left + start_x * self.cell_size + self.cell_size // 2
                start_py = board_top + start_y * self.cell_size + self.cell_size // 2
                end_px = board_left + end_x * self.cell_size + self.cell_size // 2
                end_py = board_top + end_y * self.cell_size + self.cell_size // 2

                pygame.draw.line(
                    screen, (100, 200, 255), (start_px, start_py), (end_px, end_py), 2
                )

        # Draw collectibles
        for item in self.collectibles:
            if not item["collected"]:
                y, x = item["pos"]
                item_x = board_left + x * self.cell_size + self.cell_size // 2
                item_y = board_top + y * self.cell_size + self.cell_size // 2

                # Draw collectible as yellow circle
                pygame.draw.circle(
                    screen, YELLOW, (item_x, item_y), self.cell_size // 4
                )
                pygame.draw.circle(
                    screen, (255, 255, 200), (item_x, item_y), self.cell_size // 4, 1
                )

        # Draw enemies
        for enemy in self.enemies:
            y, x = enemy["pos"]
            enemy_x = board_left + x * self.cell_size + self.cell_size // 2
            enemy_y = board_top + y * self.cell_size + self.cell_size // 2

            # Different colors for different enemy types
            if enemy["type"] == "hunter":
                color = RED
            elif enemy["type"] == "patrol":
                color = (200, 100, 50)
            else:  # Random
                color = (150, 50, 150)

            # Draw enemy
            if self.freeze_time > 0:
                # Draw frozen enemies with blue tint
                pygame.draw.circle(
                    screen,
                    (color[0] // 2, color[1] // 2, 255),
                    (enemy_x, enemy_y),
                    self.cell_size // 3,
                )
                pygame.draw.circle(
                    screen, BLUE, (enemy_x, enemy_y), self.cell_size // 3, 2
                )
            else:
                pygame.draw.circle(
                    screen, color, (enemy_x, enemy_y), self.cell_size // 3
                )
                pygame.draw.circle(
                    screen, (255, 200, 200), (enemy_x, enemy_y), self.cell_size // 3, 1
                )

        # Draw player
        player_y, player_x = self.player_pos
        player_x = board_left + player_x * self.cell_size + self.cell_size // 2
        player_y = board_top + player_y * self.cell_size + self.cell_size // 2
        pygame.draw.circle(screen, GREEN, (player_x, player_y), self.cell_size // 3)
        pygame.draw.circle(
            screen, (200, 255, 200), (player_x, player_y), self.cell_size // 3, 2
        )

        # Draw target
        target_y, target_x = self.target_pos
        target_x = board_left + target_x * self.cell_size + self.cell_size // 2
        target_y = board_top + target_y * self.cell_size + self.cell_size // 2

        # Draw target as red square
        target_rect = pygame.Rect(
            target_x - self.cell_size // 3,
            target_y - self.cell_size // 3,
            self.cell_size * 2 // 3,
            self.cell_size * 2 // 3,
        )
        pygame.draw.rect(screen, (200, 50, 50), target_rect)
        pygame.draw.rect(screen, (255, 200, 200), target_rect, 2)

        # Draw collection mode indicator
        collection_y = stats_y + 30
        mode_text = self.font.render(
            f"Mode: {'Collecting' if self.collecting_mode else 'Target'}",
            True,
            YELLOW if self.collecting_mode else WHITE,
        )
        screen.blit(mode_text, (board_left, collection_y))

        # Draw power-ups
        power_ups_y = collection_y
        power_text = self.font.render("Power-ups:", True, WHITE)
        screen.blit(
            power_text, (board_left + board_width - power_text.get_width(), power_ups_y)
        )

        # Draw each power-up
        power_up_x = board_left + board_width - 200
        for i, (name, count) in enumerate(self.power_ups.items()):
            text = self.font.render(
                f"{i+1}. {name.capitalize()}: {count}",
                True,
                LIGHT_BLUE if count > 0 else GRAY,
            )
            screen.blit(text, (power_up_x, power_ups_y + 25 + i * 25))

        # Draw controls help
        controls_y = collection_y + 100
        controls = [
            "Controls:",
            "Arrow keys: Move",
            "Space: Toggle path",
            "C: Toggle collection mode",
            "1-3: Use power-ups",
        ]

        for i, text in enumerate(controls):
            ctrl_text = self.font.render(text, True, WHITE)
            screen.blit(ctrl_text, (board_left, controls_y + i * 25))

        # Draw game over message
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            if self.player_pos == self.target_pos:
                result = "VICTORY!"
                color = GREEN
            else:
                result = "GAME OVER"
                color = RED

            # Draw result
            result_font = pygame.font.SysFont(None, 72)
            result_text = result_font.render(result, True, color)
            screen.blit(
                result_text,
                (
                    SCREEN_WIDTH // 2 - result_text.get_width() // 2,
                    SCREEN_HEIGHT // 2 - 60,
                ),
            )

            # Draw final score
            score_text = self.title_font.render(
                f"Final Score: {self.player_score}", True, WHITE
            )
            screen.blit(
                score_text,
                (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2),
            )

            # Draw restart instruction
            restart_text = self.font.render(
                "Press any key to restart or ESC to return to menu", True, WHITE
            )
            screen.blit(
                restart_text,
                (
                    SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                    SCREEN_HEIGHT // 2 + 50,
                ),
            )

        # Draw instructions modal
        if self.show_instructions:
            self._draw_instructions(screen)

    def _draw_instructions(self, screen):
        """Draw instructions modal"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Instructions panel
        panel_width = 600
        panel_height = 400
        panel_left = (SCREEN_WIDTH - panel_width) // 2
        panel_top = (SCREEN_HEIGHT - panel_height) // 2

        # Draw panel background
        pygame.draw.rect(
            screen, (40, 50, 70), (panel_left, panel_top, panel_width, panel_height)
        )
        pygame.draw.rect(
            screen, LIGHT_BLUE, (panel_left, panel_top, panel_width, panel_height), 3
        )

        # Draw title
        title = self.title_font.render("HOW TO PLAY", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, panel_top + 20))

        # Draw instructions text
        instructions = [
            "Welcome to Pathfinder Adventure!",
            "",
            "OBJECTIVE:",
            "• Navigate through the maze to reach the target (red square)",
            "• Collect items (yellow circles) to earn points and power-ups",
            "• Avoid enemies that will cost you points and moves",
            "• Watch your Win Rate to gauge your chances of success",
            "",
            "CONTROLS:",
            "• Arrow Keys: Move your character",
            "• Space: Toggle path visualization using A* algorithm",
            "• C: Toggle between Target mode and Collection mode",
            "• 1: Use Teleport power-up",
            "• 2: Use Reveal Path power-up",
            "• 3: Use Freeze Enemies power-up",
            "",
            "ENEMIES:",
            "• Red: Hunters that chase you",
            "• Orange: Patrol enemies that follow fixed paths",
            "• Purple: Random movement enemies",
            "",
            "Press any key to start playing!",
        ]

        y_pos = panel_top + 70
        for line in instructions:
            if line.startswith("•"):
                text = self.font.render(line, True, LIGHT_BLUE)
                screen.blit(text, (panel_left + 35, y_pos))
            elif (
                line.startswith("OBJECTIVE:")
                or line.startswith("CONTROLS:")
                or line.startswith("ENEMIES:")
            ):
                text = self.title_font.render(line, True, YELLOW)
                screen.blit(text, (panel_left + 20, y_pos))
            elif line == "":
                # Just skip to next line for blank lines
                pass
            else:
                text = self.font.render(line, True, WHITE)
                screen.blit(text, (panel_left + 20, y_pos))
            y_pos += 20

    def _update_win_rate(self):
        """Calculate real-time win rate based on player's situation"""
        # Several factors determine win rate:
        # 1. Distance to target (closer = higher rate)
        # 2. Remaining moves (more = higher rate)
        # 3. Remaining time (more = higher rate)
        # 4. Proximity to enemies (closer = lower rate)
        # 5. Number of collected items (more = higher rate)
        # 6. Power-ups available (more = higher rate)

        # Base win rate starts at 50%
        base_rate = 50.0

        # Factor 1: Distance to target
        current_path = self._find_path_astar(self.player_pos, self.target_pos)
        distance_to_target = len(current_path) if current_path else self.grid_size * 2

        path_factor = 20.0 * (
            1 - (distance_to_target / (self.optimal_path_length * 1.5))
        )

        # Factor 2: Remaining moves
        move_factor = 10.0 * (self.moves_remaining / 100.0)

        # Factor 3: Remaining time
        time_factor = 10.0 * (self.time_remaining / self.time_limit)

        # Factor 4: Enemy proximity
        enemy_danger = 0
        for enemy in self.enemies:
            ey, ex = enemy["pos"]
            distance = abs(ey - self.player_pos[0]) + abs(ex - self.player_pos[1])
            if distance < 5:
                if enemy["type"] == "hunter":
                    enemy_danger += (5 - distance) * 2
                else:
                    enemy_danger += 5 - distance
        enemy_factor = -10.0 * (enemy_danger / 20.0)
        enemy_factor = max(enemy_factor, -15.0)  # Cap negative impact

        # Factor 5: Collected items
        collected_count = sum(1 for item in self.collectibles if item["collected"])
        total_items = len(self.collectibles)
        collection_factor = 5.0 * (collected_count / max(total_items, 1))

        # Factor 6: Available power-ups
        power_up_count = sum(self.power_ups.values())
        power_up_factor = 5.0 * (power_up_count / 6.0)  # Assuming max ~6 power-ups

        # Calculate total win rate
        self.win_rate = min(
            100.0,
            max(
                0.0,
                base_rate
                + path_factor
                + move_factor
                + time_factor
                + enemy_factor
                + collection_factor
                + power_up_factor,
            ),
        )

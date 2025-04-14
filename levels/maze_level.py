import pygame
import random
from levels.base_level import BaseLevel
from entities.player import Player
from entities.obstacles import Teleporter
from algorithms.search_algorithms import BFS, DFS
from visualization.path_visualizer import PathVisualizer
from settings import BLACK, WHITE, GREEN, RED, BLUE, SCREEN_WIDTH, SCREEN_HEIGHT

class MazeLevel(BaseLevel):
    def __init__(self, game_engine, asset_manager):
        super().__init__(game_engine, asset_manager)
        
        # Maze settings
        self.cell_size = 30
        self.grid_width = 20  # Cells horizontally
        self.grid_height = 15  # Cells vertically
        self.maze_offset_x = (SCREEN_WIDTH - (self.grid_width * self.cell_size)) // 2
        self.maze_offset_y = (SCREEN_HEIGHT - (self.grid_height * self.cell_size)) // 2 + 50
        
        # Initialize grid (1 = wall, 0 = path)
        self.grid = [[1 for x in range(self.grid_width)] for y in range(self.grid_height)]
        
        # Generate maze
        self.generate_maze()
        
        # Set up player
        self.start_pos = (1, 1)
        self.end_pos = (self.grid_width - 2, self.grid_height - 2)
        self.grid[self.start_pos[1]][self.start_pos[0]] = 0
        self.grid[self.end_pos[1]][self.end_pos[0]] = 0
        
        # Create player
        self.player = Player(
            self.cell_to_pixel(self.start_pos[0], self.start_pos[1]),
            (self.cell_size - 6, self.cell_size - 6)
        )
        
        # Create teleporters (random placement)
        self.teleporters = []
        self._add_teleporters(2)  # Add 2 pairs of teleporters
        
        # Algorithm selection
        self.algorithms = {
            "BFS": BFS(),
            "DFS": DFS()
        }
        self.current_algorithm = "BFS"
        
        # Path visualization
        self.visualizer = PathVisualizer()
        self.current_path = []
        self.visited_cells = set()
        self.show_algorithm = False
        
        # UI elements
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.button_rect = pygame.Rect(50, 20, 150, 40)
        self.button_hovered = False
        
        # Completion state
        self.completed = False
    
    def cell_to_pixel(self, x, y):
        """Convert cell coordinates to pixel coordinates"""
        return (
            self.maze_offset_x + x * self.cell_size + self.cell_size // 2,
            self.maze_offset_y + y * self.cell_size + self.cell_size // 2
        )
    
    def pixel_to_cell(self, x, y):
        """Convert pixel coordinates to cell coordinates"""
        # Convert to integers for safe division
        x, y = int(x), int(y)
        cell_x = int((x - self.maze_offset_x) // self.cell_size)
        cell_y = int((y - self.maze_offset_y) // self.cell_size)
        
        # Ensure within grid bounds
        cell_x = max(0, min(cell_x, self.grid_width - 1))
        cell_y = max(0, min(cell_y, self.grid_height - 1))
        
        return (cell_x, cell_y)
    
    def generate_maze(self):
        """Generate a random maze using recursive backtracking algorithm"""
        # Start with a grid full of walls
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                self.grid[y][x] = 1
        
        # Use recursive backtracking to carve paths
        self._carve_passages_from(1, 1)
    
    def _carve_passages_from(self, x, y):
        """Recursive function to carve passages in the maze"""
        # Mark current cell as path
        self.grid[y][x] = 0
        
        # Shuffle directions to randomize maze generation
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # Up, right, down, left
        random.shuffle(directions)
        
        # Try each direction
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            
            # Check if the new position is within the grid and is a wall
            if (0 < new_x < self.grid_width - 1 and 
                0 < new_y < self.grid_height - 1 and 
                self.grid[new_y][new_x] == 1):
                
                # Carve a path by making the wall between current and new cell into a path
                self.grid[y + dy//2][x + dx//2] = 0
                
                # Recursively carve passages from the new position
                self._carve_passages_from(new_x, new_y)
    
    def _add_teleporters(self, num_pairs):
        """Add teleporter pairs to the maze"""
        for _ in range(num_pairs):
            # Find two empty cells for a teleporter pair
            positions = []
            colors = [(128, 0, 128), (255, 20, 147)]  # Purple, Pink
            
            while len(positions) < 2:
                x = random.randint(1, self.grid_width - 2)
                y = random.randint(1, self.grid_height - 2)
                
                # Ensure it's not on the player start, end, or another teleporter
                is_start_or_end = (x, y) == self.start_pos or (x, y) == self.end_pos
                is_on_teleporter = any(t.cell_pos == (x, y) for t in self.teleporters)
                
                if self.grid[y][x] == 0 and not is_start_or_end and not is_on_teleporter:
                    positions.append((x, y))
            
            # Create teleporter pair
            color = random.choice(colors)
            t1 = Teleporter(positions[0], self.cell_to_pixel(*positions[0]), color)
            t2 = Teleporter(positions[1], self.cell_to_pixel(*positions[1]), color)
            
            # Link teleporters to each other
            t1.link_teleporter(t2)
            t2.link_teleporter(t1)
            
            self.teleporters.extend([t1, t2])
    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            self._handle_player_movement(event)
            
            # Toggle algorithm visibility
            if event.key == pygame.K_SPACE:
                self.show_algorithm = not self.show_algorithm
                if self.show_algorithm:
                    self._run_algorithm()
        
        # Handle algorithm button click
        if event.type == pygame.MOUSEMOTION:
            self.button_hovered = self.button_rect.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                self._toggle_algorithm()
    
    def _toggle_algorithm(self):
        """Toggle between BFS and DFS algorithms"""
        if self.current_algorithm == "BFS":
            self.current_algorithm = "DFS"
        else:
            self.current_algorithm = "BFS"
        
        if self.show_algorithm:
            self._run_algorithm()
    
    def _handle_player_movement(self, event):
        """Process player movement based on key input"""
        if self.completed:
            return
            
        # Get current cell position
        cell_x, cell_y = self.pixel_to_cell(*self.player.position)
        
        # Calculate new position based on key
        new_cell_x, new_cell_y = cell_x, cell_y
        
        if event.key == pygame.K_UP:
            new_cell_y -= 1
        elif event.key == pygame.K_RIGHT:
            new_cell_x += 1
        elif event.key == pygame.K_DOWN:
            new_cell_y += 1
        elif event.key == pygame.K_LEFT:
            new_cell_x -= 1
        else:
            return  # Not a movement key
        
        # Ensure cell coordinates are integers
        new_cell_x, new_cell_y = int(new_cell_x), int(new_cell_y)
        
        # Check if the new position is valid (not a wall)
        if (0 <= new_cell_x < self.grid_width and 
            0 <= new_cell_y < self.grid_height and 
            self.grid[new_cell_y][new_cell_x] == 0):
            
            # Move player to center of new cell
            new_pos = self.cell_to_pixel(new_cell_x, new_cell_y)
            self.player.move_to(new_pos)
            
            # Check for teleporters
            for teleporter in self.teleporters:
                if teleporter.cell_pos == (new_cell_x, new_cell_y):
                    linked_teleporter = teleporter.linked_teleporter
                    if linked_teleporter:
                        # Teleport the player
                        self.player.move_to(linked_teleporter.position)
                        break
            
            # Check for completion (reached the end)
            current_cell = self.pixel_to_cell(*self.player.position)
            if current_cell == self.end_pos:
                self.completed = True
    
    def _run_algorithm(self):
        """Run the selected pathfinding algorithm"""
        # Get player's current position
        start_cell = self.pixel_to_cell(*self.player.position)
        
        # Run algorithm to find path to end
        algorithm = self.algorithms[self.current_algorithm]
        path, visited = algorithm.find_path(self.grid, start_cell, self.end_pos)
        
        # Update visualization
        self.current_path = path
        self.visited_cells = visited
        print(f"Path found with {len(visited)} cells visited")
    
    def update(self, dt):
        """Update maze level logic"""
        self.player.update(dt)
        
        for teleporter in self.teleporters:
            teleporter.update(dt)
        
        # Update visualizer
        self.visualizer.update(dt)
    
    def render(self, screen):
        """Render the maze level"""
        # Fill background
        screen.fill(BLACK)
        
        # Draw maze grid
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                cell_rect = pygame.Rect(
                    self.maze_offset_x + x * self.cell_size,
                    self.maze_offset_y + y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                # Determine cell color
                cell_pos = (x, y)
                color = BLACK if self.grid[y][x] == 1 else WHITE
                
                # Mark start and end cells
                if cell_pos == self.start_pos:
                    color = GREEN
                elif cell_pos == self.end_pos:
                    color = RED
                
                # Highlight visited cells and path if algorithm visualization is active
                if self.show_algorithm:
                    if cell_pos in self.visited_cells and self.grid[y][x] == 0:
                        color = (200, 200, 255)  # Light blue for visited
                    if cell_pos in self.current_path:
                        color = (100, 100, 255)  # Blue for path
                
                pygame.draw.rect(screen, color, cell_rect)
                pygame.draw.rect(screen, (50, 50, 50), cell_rect, 1)  # Grid lines
        
        # If visualization is active, draw path
        if self.show_algorithm and self.current_path:
            self.visualizer.render_path(screen, self.current_path, self.cell_to_pixel)
        
        # Draw teleporters
        for teleporter in self.teleporters:
            teleporter.render(screen)
        
        # Draw player
        self.player.render(screen)
        
        # Draw algorithm UI
        self._render_ui(screen)
        
        # Draw completion message if complete
        if self.completed:
            self._render_completion_message(screen)
    
    def _render_ui(self, screen):
        """Render UI elements"""
        # Draw algorithm button
        button_color = (100, 100, 255) if self.button_hovered else (50, 50, 200)
        pygame.draw.rect(screen, button_color, self.button_rect)
        pygame.draw.rect(screen, WHITE, self.button_rect, 2)
        
        # Draw button text
        button_text = self.font.render(f"Algo: {self.current_algorithm}", True, WHITE)
        button_text_rect = button_text.get_rect(center=self.button_rect.center)
        screen.blit(button_text, button_text_rect)
        
        # Draw instructions
        instructions = self.small_font.render("Use arrow keys to move. Press SPACE to toggle algorithm visualization.", True, WHITE)
        screen.blit(instructions, (50, SCREEN_HEIGHT - 30))
    
    def _render_completion_message(self, screen):
        """Render completion message"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Draw completion message
        font = pygame.font.SysFont(None, 64)
        message = font.render("Maze Complete!", True, GREEN)
        message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(message, message_rect)
        
        # Draw sub-message
        sub_font = pygame.font.SysFont(None, 32)
        sub_message = sub_font.render("Press ESC to return to level select", True, WHITE)
        sub_rect = sub_message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(sub_message, sub_rect)
    
    def reset(self):
        """Reset the level to initial state"""
        super().reset()
        
        # Reset player to start position
        self.player.move_to(self.cell_to_pixel(self.start_pos[0], self.start_pos[1]))
        
        # Regenerate maze
        self.generate_maze()
        
        # Set start and end to be paths
        self.grid[self.start_pos[1]][self.start_pos[0]] = 0
        self.grid[self.end_pos[1]][self.end_pos[0]] = 0
        
        # Reset teleporters
        self.teleporters = []
        self._add_teleporters(2)
        
        # Reset visualization
        self.current_path = []
        self.visited_cells = set()

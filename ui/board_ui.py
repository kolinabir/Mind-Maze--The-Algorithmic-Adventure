import pygame
from settings import WHITE, BLACK, BLUE, RED, GREEN

class GameBoard:
    def __init__(self, size, center_pos, special_tiles=None):
        """
        Initialize the game board
        
        Args:
            size: Size of the board (size x size)
            center_pos: Center position of the board (x, y)
            special_tiles: List of (row, col, type) tuples for special tiles
        """
        self.size = size
        self.center_pos = center_pos
        self.special_tiles = special_tiles or []
        
        # Calculate board dimensions and position
        self.cell_size = 80  # Size of each cell in pixels
        self.board_size = size * self.cell_size  # Total board size in pixels
        self.board_pos = (
            center_pos[0] - self.board_size // 2,
            center_pos[1] - self.board_size // 2
        )
        
        # Initialize the board state (None = empty, 'X', 'O', or 'B' for blocked)
        self.board_state = [[None for _ in range(size)] for _ in range(size)]
        
        # Special tile colors
        self.special_tile_colors = {
            'double': (0, 200, 100),
            'block': (200, 50, 50),
            'swap': (200, 200, 0),
            'random': (150, 100, 200)
        }
        
        # Animation properties
        self.animations = []  # List of active animations
    
    def get_state(self):
        """Get the current board state"""
        return self.board_state
    
    def is_empty(self, row, col):
        """Check if a cell is empty"""
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.board_state[row][col] is None
        return False
    
    def is_full(self):
        """Check if the board is full"""
        for row in range(self.size):
            for col in range(self.size):
                if self.is_empty(row, col):
                    return False
        return True
    
    def place_symbol(self, row, col, symbol):
        """Place a symbol on the board"""
        if self.is_empty(row, col):
            self.board_state[row][col] = symbol
            
            # Add placement animation
            cell_center = self.get_cell_center_pos(row, col)
            self.animations.append({
                'type': 'place',
                'pos': cell_center,
                'symbol': symbol,
                'scale': 0.1,
                'duration': 0.3,
                'elapsed': 0,
                'row': row,
                'col': col
            })
            
            return True
        return False
    
    def block_cell(self, row, col):
        """Block a cell so it can't be used"""
        if self.is_empty(row, col):
            self.board_state[row][col] = 'B'  # B for blocked
            return True
        return False
    
    def get_empty_cells(self):
        """Get a list of empty cells as (row, col) tuples"""
        empty_cells = []
        for row in range(self.size):
            for col in range(self.size):
                if self.is_empty(row, col):
                    empty_cells.append((row, col))
        return empty_cells
    
    def get_cell_at_pos(self, pos):
        """Get the board cell at a screen position, or None if not on the board"""
        x, y = pos
        board_x, board_y = self.board_pos
        
        # Check if position is on the board
        if (board_x <= x < board_x + self.board_size and
            board_y <= y < board_y + self.board_size):
            
            # Calculate cell coordinates
            col = (x - board_x) // self.cell_size
            row = (y - board_y) // self.cell_size
            
            if 0 <= row < self.size and 0 <= col < self.size:
                return (row, col)
        
        return None
    
    def get_cell_rect(self, row, col):
        """Get the rectangle for a cell"""
        board_x, board_y = self.board_pos
        cell_x = board_x + col * self.cell_size
        cell_y = board_y + row * self.cell_size
        
        return pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
    
    def get_cell_center_pos(self, row, col):
        """Get the center position of a cell"""
        rect = self.get_cell_rect(row, col)
        return rect.center
    
    def is_special_tile(self, row, col):
        """Check if a cell is a special tile"""
        if not self.special_tiles:
            return False
            
        for r, c, type in self.special_tiles:
            if r == row and c == col:
                return True
        return False
    
    def get_special_tile_type(self, row, col):
        """Get the type of a special tile, or None if not special"""
        for r, c, type in self.special_tiles:
            if r == row and c == col:
                return type
        return None
    
    def update(self, dt):
        """Update board animations"""
        # Update active animations
        for anim in self.animations[:]:
            anim['elapsed'] += dt
            if anim['elapsed'] >= anim['duration']:
                self.animations.remove(anim)
    
    def render(self, screen):
        """Render the game board"""
        # Draw board background
        board_rect = pygame.Rect(*self.board_pos, self.board_size, self.board_size)
        pygame.draw.rect(screen, (50, 50, 50), board_rect)
        
        # Draw cells
        for row in range(self.size):
            for col in range(self.size):
                cell_rect = self.get_cell_rect(row, col)
                
                # Draw cell background
                if self.is_special_tile(row, col):
                    # Special tile background
                    special_type = self.get_special_tile_type(row, col)
                    bg_color = self.special_tile_colors.get(special_type, WHITE)
                    pygame.draw.rect(screen, bg_color, cell_rect)
                else:
                    # Standard cell background
                    pygame.draw.rect(screen, (200, 200, 200), cell_rect)
                
                # Draw cell border
                pygame.draw.rect(screen, BLACK, cell_rect, 2)
                
                # Draw symbol
                symbol = self.board_state[row][col]
                if symbol == 'X':
                    self._draw_x(screen, cell_rect.center, cell_rect.width * 0.4)
                elif symbol == 'O':
                    self._draw_o(screen, cell_rect.center, cell_rect.width * 0.4)
                elif symbol == 'B':  # Blocked cell
                    self._draw_blocked(screen, cell_rect)
        
        # Draw animations
        for anim in self.animations:
            if anim['type'] == 'place':
                progress = min(anim['elapsed'] / anim['duration'], 1.0)
                scale = anim['scale'] + (1.0 - anim['scale']) * progress
                
                if anim['symbol'] == 'X':
                    self._draw_x(screen, anim['pos'], self.cell_size * 0.4 * scale)
                elif anim['symbol'] == 'O':
                    self._draw_o(screen, anim['pos'], self.cell_size * 0.4 * scale)
    
    def _draw_x(self, screen, center, size):
        """Draw an X symbol"""
        x, y = center
        offset = size / 2
        
        # Draw X (two diagonal lines)
        pygame.draw.line(screen, RED, (x - offset, y - offset), (x + offset, y + offset), 5)
        pygame.draw.line(screen, RED, (x - offset, y + offset), (x + offset, y - offset), 5)
    
    def _draw_o(self, screen, center, size):
        """Draw an O symbol"""
        pygame.draw.circle(screen, BLUE, center, size, 5)
    
    def _draw_blocked(self, screen, rect):
        """Draw a blocked cell"""
        # Draw a cross pattern
        pygame.draw.line(screen, BLACK, rect.topleft, rect.bottomright, 3)
        pygame.draw.line(screen, BLACK, rect.bottomleft, rect.topright, 3)
        
        # Draw a "blocked" background
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((100, 100, 100, 150))
        screen.blit(overlay, rect)

from collections import deque

class BFS:
    """Breadth-First Search algorithm for pathfinding"""
    
    def find_path(self, grid, start, goal):
        """
        Find path from start to goal using BFS
        
        Args:
            grid: 2D list where 0 is path and 1 is wall
            start: Tuple (x, y) of starting position
            goal: Tuple (x, y) of goal position
            
        Returns:
            path: List of tuples representing the path from start to goal
            visited: Set of all cells visited during the search
        """
        # Check if start or goal is a wall
        if grid[start[1]][start[0]] == 1 or grid[goal[1]][goal[0]] == 1:
            return [], set()
        
        # Get grid dimensions
        height = len(grid)
        width = len(grid[0])
        
        # Direction vectors (up, right, down, left)
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        # Queue for BFS
        queue = deque([start])
        
        # Track visited cells and previous cells for path reconstruction
        visited = {start}
        previous = {start: None}
        
        while queue:
            current = queue.popleft()
            
            # If we reached the goal, reconstruct and return the path
            if current == goal:
                return self._reconstruct_path(previous, start, goal), visited
            
            # Try all four directions
            for dy, dx in directions:
                ny, nx = current[1] + dy, current[0] + dx
                next_cell = (nx, ny)
                
                # Check if next cell is valid
                if (0 <= nx < width and 0 <= ny < height and 
                    grid[ny][nx] == 0 and next_cell not in visited):
                    
                    queue.append(next_cell)
                    visited.add(next_cell)
                    previous[next_cell] = current
        
        # No path found
        return [], visited
    
    def _reconstruct_path(self, previous, start, goal):
        """Reconstruct path from start to goal using the previous dictionary"""
        path = []
        current = goal
        
        while current != start:
            path.append(current)
            current = previous[current]
        
        path.append(start)
        path.reverse()
        return path

class DFS:
    """Depth-First Search algorithm for pathfinding"""
    
    def find_path(self, grid, start, goal):
        """
        Find path from start to goal using DFS
        
        Args:
            grid: 2D list where 0 is path and 1 is wall
            start: Tuple (x, y) of starting position
            goal: Tuple (x, y) of goal position
            
        Returns:
            path: List of tuples representing the path from start to goal
            visited: Set of all cells visited during the search
        """
        # Check if start or goal is a wall
        if grid[start[1]][start[0]] == 1 or grid[goal[1]][goal[0]] == 1:
            return [], set()
        
        # Get grid dimensions
        height = len(grid)
        width = len(grid[0])
        
        # Direction vectors (up, right, down, left)
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        # Stack for DFS
        stack = [start]
        
        # Track visited cells and previous cells for path reconstruction
        visited = {start}
        previous = {start: None}
        
        while stack:
            current = stack.pop()
            
            # If we reached the goal, reconstruct and return the path
            if current == goal:
                return self._reconstruct_path(previous, start, goal), visited
            
            # Try all four directions
            for dy, dx in directions:
                ny, nx = current[1] + dy, current[0] + dx
                next_cell = (nx, ny)
                
                # Check if next cell is valid
                if (0 <= nx < width and 0 <= ny < height and 
                    grid[ny][nx] == 0 and next_cell not in visited):
                    
                    stack.append(next_cell)
                    visited.add(next_cell)
                    previous[next_cell] = current
        
        # No path found
        return [], visited
    
    def _reconstruct_path(self, previous, start, goal):
        """Reconstruct path from start to goal using the previous dictionary"""
        path = []
        current = goal
        
        while current != start:
            path.append(current)
            current = previous[current]
        
        path.append(start)
        path.reverse()
        return path

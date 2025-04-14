from collections import deque

class JugSolver:
    def __init__(self):
        # Maximum states to prevent infinite loops on unsolvable puzzles
        self.max_states = 10000
    
    def solve(self, capacities, initial_state, target):
        """
        Solve the water jug problem using BFS
        
        Args:
            capacities: List of jug capacities
            initial_state: List of initial water amounts in jugs
            target: Target amount to measure
            
        Returns:
            List of steps to reach the solution, or empty list if no solution
        """
        # Initialize BFS
        queue = deque([(initial_state, [])])  # (state, steps)
        visited = set([tuple(initial_state)])
        states_checked = 0
        
        while queue and states_checked < self.max_states:
            current_state, steps = queue.popleft()
            states_checked += 1
            
            # Check if we've reached the target
            if target in current_state:
                return steps
            
            # Generate all possible next states
            for next_state, action in self._get_next_states(current_state, capacities):
                state_tuple = tuple(next_state)
                if state_tuple not in visited:
                    visited.add(state_tuple)
                    queue.append((next_state, steps + [action]))
        
        # No solution found
        return []
    
    def _get_next_states(self, current_state, capacities):
        """Generate all possible next states from current state"""
        next_states = []
        
        # Fill operations
        for i in range(len(current_state)):
            if current_state[i] < capacities[i]:
                new_state = current_state.copy()
                new_state[i] = capacities[i]
                action = (f"Fill jug {i+1}", f"Fill jug {i+1} to capacity {capacities[i]}")
                next_states.append((new_state, action))
        
        # Empty operations
        for i in range(len(current_state)):
            if current_state[i] > 0:
                new_state = current_state.copy()
                new_state[i] = 0
                action = (f"Empty jug {i+1}", f"Empty jug {i+1}")
                next_states.append((new_state, action))
        
        # Pour operations
        for i in range(len(current_state)):
            for j in range(len(current_state)):
                if i != j and current_state[i] > 0 and current_state[j] < capacities[j]:
                    new_state = current_state.copy()
                    
                    # Calculate amount to pour
                    amount = min(current_state[i], capacities[j] - current_state[j])
                    
                    # Update jugs
                    new_state[i] -= amount
                    new_state[j] += amount
                    
                    action = (f"Pour jug {i+1} into jug {j+1}", 
                             f"Pour {amount}L from jug {i+1} to jug {j+1}")
                    next_states.append((new_state, action))
        
        return next_states

# Mind Maze: The Algorithmic Adventure

Mind Maze is a 2D puzzle game built with Pygame that features multiple algorithmic challenges including BFS, DFS, tic-tac-toe with minimax/alpha-beta pruning, and the water jug problem. The game takes players through different puzzle chambers, each showcasing a different algorithm with engaging visualizations.

## Features

- **Maze Explorer**: Navigate through procedurally generated mazes using BFS or DFS algorithms
- **Water Jug Challenge**: Solve the classic water jug problem with interactive mechanics
- **Tic-Tac-Toe Master**: Play against an AI opponent using the minimax algorithm
- **Strategy Game**: Face a challenging opponent with alpha-beta pruning
- **Final Integration**: A comprehensive challenge combining all previous algorithms

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

### Setup

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/mind-maze.git
   cd mind-maze
   ```

2. Create a virtual environment (recommended):

   ```
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Game

After installing the requirements, run the game using:

```
python main.py
```

## How to Play

### Maze Explorer

- Use arrow keys to navigate through the maze
- Press Space to toggle algorithm visualization
- Click the algorithm button to switch between BFS and DFS
- Find teleporters to quickly move around the maze
- Reach the red square to complete the level

### Water Jug Challenge

- Click on a jug to select it
- Use Fill, Empty, or Pour actions to manipulate the water
- Measure the exact target amount in any jug to win
- Use the Hint button if you get stuck
- Complete the puzzle within the limited number of moves

### Controls

- **Arrow Keys**: Navigate in mazes
- **Mouse**: Select jugs, buttons, and UI elements
- **Space**: Toggle algorithm visualization
- **Escape**: Return to level selection

## Project Structure

```
Mind Maze/
├── main.py                 # Entry point
├── settings.py             # Game configurations
├── game_engine/            # Core game functionality
├── algorithms/             # Algorithm implementations
├── levels/                 # Level designs and mechanics
├── entities/               # Game entities
├── visualization/          # Algorithm visualizations
├── ui/                     # User interface elements
├── audio/                  # Sound management
├── graphics/               # Visual effects
├── save/                   # Save/load functionality
└── assets/                 # Game assets
```

## Development

This project is structured to implement different algorithms as engaging puzzle experiences. Each level showcases a different algorithm with interactive visualizations to help players understand how they work.

### Current Implementation Status:

- [x] Part 1: Project Setup and Basic Structure
- [x] Part 2: Home Screen and UI Design
- [x] Part 3: Maze Generation and Navigation (BFS/DFS)
- [x] Part 4: Water Jug Puzzle
- [ ] Part 5: Tic-Tac-Toe with Minimax
- [ ] Part 6: Alpha-Beta Pruning
- [ ] Part 7: Final Integration Challenge
- [ ] Part 8: Graphics, Audio, and Polish
- [ ] Part 9: Save System and Tutorial

## Part 6: Strategy Game with Alpha-Beta Pruning

The Strategy Game level features:

1. **Alpha-Beta Pruning Algorithm**: An optimized search algorithm that reduces the number of nodes evaluated in the minimax search tree
2. **Pruning Visualization**: Interactive visualization showing how alpha-beta pruning eliminates unnecessary branches
3. **Strategy Board Game**: A challenging game where pieces move across the board toward the opponent's side
4. **Power-Up System**: Special items that give players advantages like extra moves or protected pieces
5. **Move Timer**: Time pressure element that requires quick decision making
6. **Multiple Difficulty Levels**: Four difficulty settings that adjust AI search depth and time limits

### How to Play

- Select your pieces with a mouse click
- Yellow highlights show valid moves
- Capture opponent pieces by moving diagonally onto them
- Collect power-ups for special abilities
- Win by reaching the opponent's side or eliminating all opponent pieces
- Be careful not to run out of time!

### Understanding Alpha-Beta Pruning

The visualization panel shows:

- Alpha (red) and beta (blue) values that represent the best scores for each player
- When alpha becomes greater than or equal to beta, branches are pruned
- Pruned branches appear in red during the animation
- Statistics show how effective the pruning is at reducing the search space

## Part 7: Final Integration Challenge

The Final Integration Challenge combines all the algorithms you've learned into a comprehensive series of puzzles:

- **Algorithm Switching**: Analyze each challenge and choose the right algorithm
- **Mixed Challenges**: Tackle a variety of puzzle types requiring different algorithms
- **Progressive Difficulty**: Face increasingly complex challenges
- **Score System**: Earn points based on speed and algorithm selection
- **Algorithm Visualizations**: See how different algorithms work together

This culminating level tests your understanding of all the algorithms covered in the game, requiring you to apply the right technique to each situation.

## License

[Include your chosen license here]

## Acknowledgements

- Pygame community for the excellent gaming library
- Algorithms inspired by classic computer science problems

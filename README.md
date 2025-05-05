# Mind Maze: The Algorithmic Adventure

Mind Maze is a 2D puzzle game built with Pygame that features multiple algorithmic challenges including BFS, DFS, tic-tac-toe with minimax/alpha-beta pruning, and the water jug problem. The game takes players through different puzzle chambers, each showcasing a different algorithm with engaging visualizations.
![image](https://github.com/user-attachments/assets/84320fb4-867e-498a-a6da-0f15042cf685)
![image](https://github.com/user-attachments/assets/20d5d7f9-560e-4a4b-b6f6-9f05b8e2fd2a)

## Features

- **Maze Explorer**: Navigate through procedurally generated mazes using BFS or DFS algorithms
- ![image](https://github.com/user-attachments/assets/97a6788d-ca28-4ff6-8efb-0451ae2afc59)

- **Water Jug Challenge**: Solve the classic water jug problem with interactive mechanics -![image](https://github.com/user-attachments/assets/5652b4c9-7cc6-4b51-8bb5-86610ff93cb2)

-
- **Tic-Tac-Toe Master**: Play against an AI opponent using the minimax algorithm
- ![image](https://github.com/user-attachments/assets/a8d9f5a5-1cdd-4f6c-90ba-a2d0806438b3)

- **Strategy Game**: Face a challenging opponent with alpha-beta pruning
- ![image](https://github.com/user-attachments/assets/05a9b833-5895-42f4-872d-a2923aab92f1)

- **Final Integration**: A comprehensive challenge combining all previous algorithms
  ![image](https://github.com/user-attachments/assets/0054dc65-5798-4337-ad1a-5ebe37c269d5)

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

## Quick Navigation

<div align="center">

[![How to Play](https://github.com/kolinabir/Mind-Maze--The-Algorithmic-Adventure/blob/main/how_to_play.mdx)](https://github.com/kolinabir/Mind-Maze--The-Algorithmic-Adventure/blob/main/how_to_play.mdx)
[![Project Structure](https://img.shields.io/badge/📁-Project_Structure-green)](#project-structure)
[![Development](https://img.shields.io/badge/🔧-Development-orange)](#development)

</div>

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


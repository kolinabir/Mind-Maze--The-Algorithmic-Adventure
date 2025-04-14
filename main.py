import pygame
import sys
# Update import to use actual file location
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from game_engine import GameEngine


def main():
    # Initialize pygame
    pygame.init()

    # Create the game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)

    # Initialize clock for framerate control
    clock = pygame.time.Clock()

    # Create game engine
    game = GameEngine(screen)

    # Main game loop
    while True:
        # Get delta time
        dt = clock.tick(FPS) / 1000.0

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Pass events to game engine
            game.handle_event(event)

        # Update game logic
        game.update(dt)

        # Render game
        game.render()

        # Update display
        pygame.display.flip()


if __name__ == "__main__":
    main()

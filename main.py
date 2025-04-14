import pygame
import sys
import time
from game_engine import GameEngine
from settings import FPS, SCREEN_WIDTH, SCREEN_HEIGHT, MENU_STATE, GRAY


def main():
    # Initialize pygame
    pygame.init()
    print(f"pygame {pygame.version.ver} ({pygame.version.SDL})")

    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mind Maze: The Algorithmic Adventure")

    # Create game engine
    game = GameEngine(screen)

    # Initialize save system
    from save.save_manager import SaveManager

    game.save_manager = SaveManager(game)

    # Load the last save if available
    profiles = game.save_manager.get_all_profiles()
    if profiles:
        game.save_manager.load_profile(profiles[0]["id"])

    # Initialize tutorial system
    from tutorial.tutorial import TutorialManager

    game.tutorial_manager = TutorialManager(game, game.assets)
    game.tutorial_manager.create_default_tutorials()

    # Initialize help system
    from ui.help_system import HelpSystem

    game.help_system = HelpSystem(game.assets)

    # Set the starting state
    game.state_manager.change_state(MENU_STATE)

    # Game loop
    clock = pygame.time.Clock()
    previous_time = time.time()

    while True:
        # Calculate delta time
        current_time = time.time()
        dt = current_time - previous_time
        previous_time = current_time

        # Cap delta time to prevent large jumps
        dt = min(dt, 0.1)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Save game before exiting
                if hasattr(game, "save_manager"):
                    game.save_manager.save_game()
                pygame.quit()
                sys.exit()

            # Check if help key is pressed (F1)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                game.help_system.toggle_help()
                continue

            # Handle events for active systems
            if hasattr(game, "help_system") and game.help_system.help_overlay_active:
                if game.help_system.handle_event(event):
                    continue

            if hasattr(game, "tutorial_manager"):
                if game.tutorial_manager.handle_event(event):
                    continue

            # Normal event handling
            game.handle_event(event)

        # Update game
        game.update(dt)

        # Update help and tutorial systems
        if hasattr(game, "help_system"):
            game.help_system.update(dt)

        if hasattr(game, "tutorial_manager"):
            game.tutorial_manager.update(dt)

        # Render game
        screen.fill(GRAY)
        game.render()

        # Render help and tutorial overlays
        if hasattr(game, "tutorial_manager"):
            game.tutorial_manager.render(screen)

        if hasattr(game, "help_system"):
            game.help_system.render(screen)

        # Update display
        pygame.display.flip()

        # Cap the framerate
        clock.tick(FPS)


if __name__ == "__main__":
    main()

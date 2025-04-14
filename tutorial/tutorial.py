import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, BLUE, LIGHT_BLUE


class TutorialStep:
    def __init__(
        self,
        title,
        content,
        target_rect=None,
        highlight=True,
        advance_on_click=True,
        image_path=None,
        required_action=None,
    ):
        self.title = title
        self.content = content
        self.target_rect = target_rect  # Rectangle to highlight
        self.highlight = highlight  # Whether to highlight the target
        self.advance_on_click = advance_on_click  # Advance to next step on click
        self.image_path = image_path  # Optional image to show
        self.image = None  # Will be loaded when needed
        self.required_action = (
            required_action  # Function that must return True to proceed
        )

    def load_image(self, asset_manager):
        """Load image if specified"""
        if self.image_path and asset_manager:
            self.image = asset_manager.get_image(self.image_path)


class Tutorial:
    """
    Interactive tutorial system that guides players through game mechanics
    """

    def __init__(self, game_engine, asset_manager):
        self.game_engine = game_engine
        self.assets = asset_manager
        self.steps = []  # Tutorial steps
        self.current_step = 0
        self.active = False
        self.completed = False

        # UI elements
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 32)
        self.panel_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT - 200, 600, 150
        )

        # Animation
        self.highlight_alpha = 0
        self.highlight_fade_in = True

    def add_step(
        self,
        title,
        content,
        target_rect=None,
        highlight=True,
        advance_on_click=True,
        image_path=None,
        required_action=None,
    ):
        """Add a tutorial step"""
        step = TutorialStep(
            title,
            content,
            target_rect,
            highlight,
            advance_on_click,
            image_path,
            required_action,
        )
        self.steps.append(step)

        # Load image if available
        if image_path:
            step.load_image(self.assets)

    def start(self):
        """Start the tutorial"""
        if not self.steps:
            print("Warning: No tutorial steps defined.")
            return

        self.current_step = 0
        self.active = True
        self.completed = False

    def next_step(self):
        """Advance to next step"""
        if not self.active:
            return

        self.current_step += 1

        # Check if tutorial completed
        if self.current_step >= len(self.steps):
            self.complete()

    def previous_step(self):
        """Go back to previous step"""
        if not self.active or self.current_step <= 0:
            return

        self.current_step -= 1

    def complete(self):
        """Complete the tutorial"""
        self.active = False
        self.completed = True

        # Save tutorial completion status
        if hasattr(self.game_engine, "save_manager"):
            self.game_engine.save_manager.set_tutorial_completed(True)

    def handle_event(self, event):
        """Handle user input for tutorial navigation"""
        if not self.active or self.current_step >= len(self.steps):
            return False  # Not handled

        current = self.steps[self.current_step]

        # Handle advancing to next step
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check if clicking the next button
            if self.panel_rect.collidepoint(event.pos):
                # Check if this step has a required action
                if current.required_action:
                    if current.required_action():
                        self.next_step()
                        return True
                elif current.advance_on_click:
                    self.next_step()
                    return True

        # Handle keyboard navigation
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                # Check if this step has a required action
                if current.required_action:
                    if current.required_action():
                        self.next_step()
                        return True
                elif current.advance_on_click:
                    self.next_step()
                    return True
            elif event.key == pygame.K_ESCAPE:
                # Allow skipping the tutorial
                self.complete()
                return True

        return False  # Event not handled

    def update(self, dt):
        """Update tutorial state"""
        if not self.active:
            return

        # Update highlight animation
        if self.highlight_fade_in:
            self.highlight_alpha = min(180, self.highlight_alpha + 300 * dt)
            if self.highlight_alpha >= 180:
                self.highlight_fade_in = False
        else:
            self.highlight_alpha = max(100, self.highlight_alpha - 300 * dt)
            if self.highlight_alpha <= 100:
                self.highlight_fade_in = True

    def render(self, screen):
        """Draw the tutorial overlay"""
        if not self.active or self.current_step >= len(self.steps):
            return

        # Get current step
        current = self.steps[self.current_step]

        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))

        # If target exists, create a "cutout" for the highlighted area
        if current.target_rect and current.highlight:
            pygame.draw.rect(overlay, (0, 0, 0, 0), current.target_rect)

            # Draw animated highlight around target
            highlight = pygame.Surface(
                (current.target_rect.width + 20, current.target_rect.height + 20),
                pygame.SRCALPHA,
            )
            pygame.draw.rect(
                highlight,
                (BLUE[0], BLUE[1], BLUE[2], int(self.highlight_alpha)),
                (0, 0, highlight.get_width(), highlight.get_height()),
                4,
            )
            screen.blit(
                highlight, (current.target_rect.x - 10, current.target_rect.y - 10)
            )

        # Blit the overlay
        screen.blit(overlay, (0, 0))

        # Draw tutorial panel
        panel = pygame.Surface(
            (self.panel_rect.width, self.panel_rect.height), pygame.SRCALPHA
        )
        pygame.draw.rect(
            panel, (20, 20, 40, 230), (0, 0, panel.get_width(), panel.get_height())
        )
        pygame.draw.rect(
            panel, LIGHT_BLUE, (0, 0, panel.get_width(), panel.get_height()), 2
        )

        # Draw step indicator
        step_text = self.font.render(
            f"Step {self.current_step + 1} of {len(self.steps)}", True, WHITE
        )
        panel.blit(step_text, (panel.get_width() - step_text.get_width() - 10, 10))

        # Draw title
        title_text = self.title_font.render(current.title, True, LIGHT_BLUE)
        panel.blit(title_text, (20, 15))

        # Draw content (handle multi-line text)
        content_lines = current.content.split("\n")
        y_offset = 60
        for line in content_lines:
            content_text = self.font.render(line, True, WHITE)
            panel.blit(content_text, (20, y_offset))
            y_offset += 25

        # Draw hint to continue
        hint_text = self.font.render(
            "Click or press Space to continue", True, (180, 180, 180)
        )
        panel.blit(
            hint_text,
            (
                panel.get_width() - hint_text.get_width() - 10,
                panel.get_height() - hint_text.get_height() - 10,
            ),
        )

        screen.blit(panel, self.panel_rect)

        # Draw image if available
        if current.image:
            # Position the image to the right of the panel
            img_x = self.panel_rect.right + 20
            img_y = self.panel_rect.centery - current.image.get_height() // 2

            # Make sure image fits on screen
            if img_x + current.image.get_width() > SCREEN_WIDTH:
                img_x = SCREEN_WIDTH - current.image.get_width() - 20

            screen.blit(current.image, (img_x, img_y))


class TutorialManager:
    """
    Manages different tutorials for various parts of the game
    """

    def __init__(self, game_engine, asset_manager):
        self.game_engine = game_engine
        self.assets = asset_manager
        self.tutorials = {}  # Dictionary of tutorials by name

        # Track which tutorials have been shown
        self.shown_tutorials = set()

    def create_tutorial(self, name):
        """Create a new tutorial with the given name"""
        tutorial = Tutorial(self.game_engine, self.assets)
        self.tutorials[name] = tutorial
        return tutorial

    def get_tutorial(self, name):
        """Get a tutorial by name"""
        return self.tutorials.get(name)

    def start_tutorial(self, name):
        """Start a specific tutorial"""
        tutorial = self.get_tutorial(name)
        if tutorial:
            tutorial.start()
            self.shown_tutorials.add(name)
            return True
        return False

    def has_shown_tutorial(self, name):
        """Check if a tutorial has been shown"""
        return name in self.shown_tutorials

    def handle_event(self, event):
        """Handle events for active tutorials"""
        for tutorial in self.tutorials.values():
            if tutorial.active and tutorial.handle_event(event):
                return True  # Event was handled
        return False

    def update(self, dt):
        """Update all active tutorials"""
        for tutorial in self.tutorials.values():
            if tutorial.active:
                tutorial.update(dt)

    def render(self, screen):
        """Render active tutorials"""
        for tutorial in self.tutorials.values():
            if tutorial.active:
                tutorial.render(screen)

    def create_default_tutorials(self):
        """Create default tutorials for the game"""
        # Main menu tutorial
        menu_tutorial = self.create_tutorial("main_menu")
        menu_tutorial.add_step(
            "Welcome to Mind Maze!",
            "This game will test your understanding of algorithms through fun puzzles.\n"
            + "Let's start by navigating the main menu.",
            None,  # No specific target yet
            False,  # No highlight
        )

        # More steps would be added in a real implementation

        # Maze level tutorial
        maze_tutorial = self.create_tutorial("maze_level")
        maze_tutorial.add_step(
            "Maze Navigation",
            "In this level, you'll navigate through a maze using search algorithms.\n"
            + "Use arrow keys to move your character.",
            None,  # Would target the player in actual implementation
            True,
        )

        maze_tutorial.add_step(
            "Algorithm Selection",
            "You can switch between BFS and DFS algorithms to find paths.\n"
            + "BFS finds the shortest path, while DFS might explore more of the maze.",
            None,  # Would target algorithm selector in actual implementation
            True,
        )

        # More tutorials would be created here for other levels

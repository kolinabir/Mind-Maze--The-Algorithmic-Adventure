import pygame


class ScreenTransition:
    def __init__(self, duration=0.5):
        self.duration = duration
        self.progress = 0.0
        self.from_screen = None
        self.to_screen = None
        self.active = False

    def start(self, from_screen, to_screen):
        self.from_screen = from_screen
        self.to_screen = to_screen
        self.progress = 0.0
        self.active = True

    def update(self, dt):
        if not self.active:
            return True  # Already finished

        self.progress += dt / self.duration
        if self.progress >= 1.0:
            self.progress = 1.0
            self.active = False
            return True  # Transition finished

        return False  # Still transitioning

    def render(self, screen):
        # Override in subclasses
        pass


class FadeTransition(ScreenTransition):
    def __init__(self, duration=0.5):
        super().__init__(duration)

    def render(self, screen):
        if self.from_screen and self.to_screen:
            if self.progress < 0.5:
                # First half: fade out from original screen
                alpha = int(255 * (1 - (self.progress * 2)))
                fade_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                fade_surface.fill((0, 0, 0, 255 - alpha))
                screen.blit(self.from_screen, (0, 0))
                screen.blit(fade_surface, (0, 0))
            else:
                # Second half: fade in to new screen
                alpha = int(255 * ((self.progress - 0.5) * 2))
                fade_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                fade_surface.fill((0, 0, 0, 255 - alpha))
                screen.blit(self.to_screen, (0, 0))
                screen.blit(fade_surface, (0, 0))


class SlideTransition(ScreenTransition):
    def __init__(self, duration=0.5, direction="left"):
        super().__init__(duration)
        self.direction = direction

    def render(self, screen):
        if self.from_screen and self.to_screen:
            width, height = screen.get_size()

            if self.direction == "left":
                # Slide from right to left
                x_offset = int(width * (1 - self.progress))
                screen.blit(self.from_screen, (-x_offset, 0))
                screen.blit(self.to_screen, (width - x_offset, 0))
            elif self.direction == "right":
                # Slide from left to right
                x_offset = int(width * self.progress)
                screen.blit(self.from_screen, (x_offset, 0))
                screen.blit(self.to_screen, (x_offset - width, 0))
            elif self.direction == "up":
                # Slide from bottom to top
                y_offset = int(height * self.progress)
                screen.blit(self.from_screen, (0, y_offset))
                screen.blit(self.to_screen, (0, y_offset - height))
            else:  # down
                # Slide from top to bottom
                y_offset = int(height * (1 - self.progress))
                screen.blit(self.from_screen, (0, -y_offset))
                screen.blit(self.to_screen, (0, height - y_offset))


class ScreenManager:
    def __init__(self):
        self.transitions = {
            "fade": FadeTransition(),
            "slide_left": SlideTransition(direction="left"),
            "slide_right": SlideTransition(direction="right"),
            "slide_up": SlideTransition(direction="up"),
            "slide_down": SlideTransition(direction="down"),
        }

        self.current_transition = None
        self.transition_from = None
        self.transition_to = None

    def start_transition(self, from_screen, to_screen, transition_type="fade"):
        if transition_type in self.transitions:
            self.transition_from = pygame.Surface(from_screen.get_size())
            self.transition_from.blit(from_screen, (0, 0))

            self.transition_to = pygame.Surface(to_screen.get_size())
            self.transition_to.blit(to_screen, (0, 0))

            self.current_transition = self.transitions[transition_type]
            self.current_transition.start(self.transition_from, self.transition_to)

            return True
        return False

    def update(self, dt):
        if self.current_transition:
            transition_complete = self.current_transition.update(dt)
            if transition_complete:
                self.current_transition = None
                return True
        return False

    def render(self, screen):
        if self.current_transition:
            self.current_transition.render(screen)
            return True
        return False

    def is_transitioning(self):
        return self.current_transition is not None

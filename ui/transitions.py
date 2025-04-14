import pygame
import math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Transition:
    """
    Base class for screen transitions
    """
    def __init__(self, duration=1.0):
        self.duration = duration  # Duration in seconds
        self.elapsed = 0
        self.completed = False
    
    def update(self, dt):
        """Update transition progress"""
        if self.completed:
            return True
            
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.elapsed = self.duration
            self.completed = True
            
        return self.completed
    
    def get_progress(self):
        """Get transition progress from 0.0 to 1.0"""
        return self.elapsed / self.duration
    
    def render(self, screen, from_surface, to_surface):
        """Render transition effect"""
        # To be implemented by subclasses
        pass
    
    def reset(self):
        """Reset transition to initial state"""
        self.elapsed = 0
        self.completed = False


class FadeTransition(Transition):
    """
    Simple fade between screens
    """
    def __init__(self, duration=1.0, color=(0, 0, 0)):
        super().__init__(duration)
        self.color = color
    
    def render(self, screen, from_surface, to_surface):
        progress = self.get_progress()
        
        if progress < 0.5:
            # Fade out the current screen
            alpha = int(255 * (progress * 2))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill(self.color)
            overlay.set_alpha(alpha)
            
            # Draw current screen with overlay
            screen.blit(from_surface, (0, 0))
            screen.blit(overlay, (0, 0))
        else:
            # Fade in the next screen
            alpha = int(255 * (2 - progress * 2))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill(self.color)
            overlay.set_alpha(alpha)
            
            # Draw next screen with overlay
            screen.blit(to_surface, (0, 0))
            screen.blit(overlay, (0, 0))


class SlideTransition(Transition):
    """
    Slide transition between screens
    """
    def __init__(self, duration=1.0, direction="left"):
        super().__init__(duration)
        self.direction = direction
    
    def render(self, screen, from_surface, to_surface):
        progress = self.get_progress()
        
        # Calculate offset based on direction
        if self.direction == "left":
            offset = int(SCREEN_WIDTH * progress)
            from_x = -offset
            to_x = SCREEN_WIDTH - offset
        elif self.direction == "right":
            offset = int(SCREEN_WIDTH * progress)
            from_x = offset
            to_x = -SCREEN_WIDTH + offset
        elif self.direction == "up":
            offset = int(SCREEN_HEIGHT * progress)
            from_y = -offset
            to_y = SCREEN_HEIGHT - offset
            from_x, to_x = 0, 0
        elif self.direction == "down":
            offset = int(SCREEN_HEIGHT * progress)
            from_y = offset
            to_y = -SCREEN_HEIGHT + offset
            from_x, to_x = 0, 0
        
        # Render the surfaces with the calculated offsets
        if self.direction in ["left", "right"]:
            screen.blit(from_surface, (from_x, 0))
            screen.blit(to_surface, (to_x, 0))
        else:
            screen.blit(from_surface, (0, from_y))
            screen.blit(to_surface, (0, to_y))


class WipeTransition(Transition):
    """
    Wipe transition between screens
    """
    def __init__(self, duration=1.0, direction="left"):
        super().__init__(duration)
        self.direction = direction
    
    def render(self, screen, from_surface, to_surface):
        progress = self.get_progress()
        
        if self.direction == "left":
            # Wipe from left to right
            width = int(SCREEN_WIDTH * progress)
            screen.blit(from_surface, (0, 0))
            screen.blit(to_surface, (0, 0), 
                       (0, 0, width, SCREEN_HEIGHT))
        elif self.direction == "right":
            # Wipe from right to left
            width = int(SCREEN_WIDTH * progress)
            offset = SCREEN_WIDTH - width
            screen.blit(from_surface, (0, 0))
            screen.blit(to_surface, (offset, 0), 
                       (offset, 0, width, SCREEN_HEIGHT))
        elif self.direction == "up":
            # Wipe from top to bottom
            height = int(SCREEN_HEIGHT * progress)
            screen.blit(from_surface, (0, 0))
            screen.blit(to_surface, (0, 0), 
                       (0, 0, SCREEN_WIDTH, height))
        elif self.direction == "down":
            # Wipe from bottom to top
            height = int(SCREEN_HEIGHT * progress)
            offset = SCREEN_HEIGHT - height
            screen.blit(from_surface, (0, 0))
            screen.blit(to_surface, (0, offset), 
                       (0, offset, SCREEN_WIDTH, height))


class CircleTransition(Transition):
    """
    Circle wipe transition
    """
    def __init__(self, duration=1.0, reverse=False):
        super().__init__(duration)
        self.reverse = reverse
    
    def render(self, screen, from_surface, to_surface):
        progress = self.get_progress()
        
        if self.reverse:
            # Circle close (from to_surface to from_surface)
            radius = int(math.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2) * (1 - progress))
            screen.blit(to_surface, (0, 0))
            
            # Create a circular mask
            mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(mask, (0, 0, 0, 255), 
                              (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), radius)
            
            # Apply the mask
            temp = from_surface.copy()
            temp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(temp, (0, 0))
        else:
            # Circle open (from from_surface to to_surface)
            radius = int(math.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2) * progress)
            screen.blit(from_surface, (0, 0))
            
            # Create a circular mask
            mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(mask, (0, 0, 0, 255), 
                              (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), radius)
            
            # Apply the mask
            temp = to_surface.copy()
            temp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(temp, (0, 0))


class TransitionManager:
    """
    Manages screen transitions
    """
    def __init__(self):
        self.transition = None
        self.from_surface = None
        self.to_surface = None
        self.transitioning = False
        
        # Available transition types
        self.transitions = {
            "fade": FadeTransition,
            "slide_left": lambda duration: SlideTransition(duration, "left"),
            "slide_right": lambda duration: SlideTransition(duration, "right"),
            "slide_up": lambda duration: SlideTransition(duration, "up"),
            "slide_down": lambda duration: SlideTransition(duration, "down"),
            "wipe_left": lambda duration: WipeTransition(duration, "left"),
            "wipe_right": lambda duration: WipeTransition(duration, "right"),
            "wipe_up": lambda duration: WipeTransition(duration, "up"),
            "wipe_down": lambda duration: WipeTransition(duration, "down"),
            "circle_open": lambda duration: CircleTransition(duration, False),
            "circle_close": lambda duration: CircleTransition(duration, True)
        }
    
    def start_transition(self, from_surface, to_surface, transition_type="fade", duration=1.0):
        """Start a transition between two surfaces"""
        if transition_type not in self.transitions:
            transition_type = "fade"
        
        # Create transition
        self.transition = self.transitions[transition_type](duration)
        
        # Copy surfaces
        self.from_surface = from_surface.copy()
        self.to_surface = to_surface.copy()
        self.transitioning = True
    
    def update(self, dt):
        """Update current transition"""
        if not self.transitioning or self.transition is None:
            return True
        
        # Update transition
        if self.transition.update(dt):
            self.transitioning = False
            return True
        
        return False
    
    def render(self, screen):
        """Render current transition"""
        if not self.transitioning or self.transition is None:
            return
        
        # Render transition
        self.transition.render(screen, self.from_surface, self.to_surface)
    
    def is_transitioning(self):
        """Check if a transition is in progress"""
        return self.transitioning

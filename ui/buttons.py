import pygame
from settings import WHITE, BLACK, MENU_BG_COLOR, MENU_TEXT_COLOR, MENU_HIGHLIGHT_COLOR, BUTTON_SIZE

class Button:
    def __init__(self, position, size, action=None):
        self.position = position
        self.size = size
        self.action = action
        self.rect = pygame.Rect(position[0] - size[0] // 2, position[1] - size[1] // 2, size[0], size[1])
        self.is_hovered = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()
    
    def update(self, dt):
        pass
    
    def render(self, screen):
        pass

class TextButton(Button):
    def __init__(self, text, position, size=BUTTON_SIZE, action=None, 
                 bg_color=MENU_BG_COLOR, text_color=MENU_TEXT_COLOR, hover_color=MENU_HIGHLIGHT_COLOR):
        super().__init__(position, size, action)
        self.text = text
        self.bg_color = list(bg_color)  # Convert tuple to list so we can modify it
        self.text_color = text_color
        self.hover_color = list(hover_color)  # Convert tuple to list
        self.font = pygame.font.SysFont(None, 32)
        
        # Animation properties
        self.current_bg_color = list(self.bg_color)  # Convert to list
        self.animation_speed = 5.0  # Color transition speed
    
    def update(self, dt):
        # Smooth color transition when hovered
        target_color = self.hover_color if self.is_hovered else self.bg_color
        
        # Interpolate towards target color
        for i in range(3):
            if self.current_bg_color[i] < target_color[i]:
                self.current_bg_color[i] = min(target_color[i], self.current_bg_color[i] + self.animation_speed * dt * 255)
            elif self.current_bg_color[i] > target_color[i]:
                self.current_bg_color[i] = max(target_color[i], self.current_bg_color[i] - self.animation_speed * dt * 255)
    
    def render(self, screen):
        # Draw button background
        pygame.draw.rect(screen, tuple(self.current_bg_color), self.rect)  # Convert back to tuple for drawing
        pygame.draw.rect(screen, self.text_color, self.rect, 2)  # Button border
        
        # Draw button text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class ImageButton(Button):
    def __init__(self, image, position, size=None, action=None, hover_image=None, scale_on_hover=1.1):
        self.image = image
        self.hover_image = hover_image or image
        self.current_image = image
        self.scale_on_hover = scale_on_hover
        
        # Get image size if not provided
        if size is None:
            size = image.get_rect().size
        
        super().__init__(position, size, action)
        
        # Calculate scaled image dimensions for hover effect
        self.normal_size = size
        scaled_width = int(size[0] * scale_on_hover)
        scaled_height = int(size[1] * scale_on_hover)
        self.hover_size = (scaled_width, scaled_height)
        
        # Current display size
        self.current_size = self.normal_size
    
    def update(self, dt):
        # Update image and size based on hover state
        target_size = self.hover_size if self.is_hovered else self.normal_size
        target_image = self.hover_image if self.is_hovered else self.image
        
        # Smooth transition between sizes
        w_diff = target_size[0] - self.current_size[0]
        h_diff = target_size[1] - self.current_size[1]
        
        new_width = self.current_size[0] + w_diff * 5 * dt
        new_height = self.current_size[1] + h_diff * 5 * dt
        
        self.current_size = (new_width, new_height)
        self.current_image = target_image
    
    def render(self, screen):
        # Scale image
        scaled_image = pygame.transform.scale(self.current_image, (int(self.current_size[0]), int(self.current_size[1])))
        
        # Center the image on position
        image_rect = scaled_image.get_rect(center=self.position)
        
        # Draw image
        screen.blit(scaled_image, image_rect)

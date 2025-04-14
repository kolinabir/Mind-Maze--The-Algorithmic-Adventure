import pygame
import time

class Animation:
    """
    Handles sprite animations and transitions
    """
    def __init__(self, frames, frame_duration=0.1, loop=True):
        """
        Initialize an animation
        
        Args:
            frames: List of pygame surfaces that make up the animation frames
            frame_duration: Time in seconds each frame is displayed
            loop: Whether the animation should repeat
        """
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame = 0
        self.start_time = time.time()
        self.playing = True
        self.completed = False
    
    def update(self):
        """Update animation state"""
        if not self.playing or self.completed:
            return
        
        elapsed = time.time() - self.start_time
        total_frames = len(self.frames)
        
        # Calculate current frame based on elapsed time
        frame_num = int(elapsed / self.frame_duration)
        
        # Handle animation completion
        if frame_num >= total_frames:
            if self.loop:
                # Loop back to beginning
                frame_num = frame_num % total_frames
                self.start_time = time.time() - (frame_num * self.frame_duration)
            else:
                # Stop at the last frame
                self.completed = True
                frame_num = total_frames - 1
        
        self.current_frame = frame_num
    
    def get_current_frame(self):
        """Get the current frame of the animation"""
        if self.frames:
            return self.frames[self.current_frame]
        return None
    
    def play(self):
        """Start or resume the animation"""
        if self.completed:
            self.reset()
        self.playing = True
    
    def pause(self):
        """Pause the animation"""
        self.playing = False
    
    def reset(self):
        """Reset the animation to the beginning"""
        self.current_frame = 0
        self.start_time = time.time()
        self.playing = True
        self.completed = False


class AnimationManager:
    """
    Manages multiple animations for game entities
    """
    def __init__(self):
        self.animations = {}
        self.current_animation = None
    
    def add_animation(self, name, frames, frame_duration=0.1, loop=True):
        """Add a new animation to the manager"""
        self.animations[name] = Animation(frames, frame_duration, loop)
        
        # Set as current if it's the first one added
        if self.current_animation is None:
            self.current_animation = name
    
    def play(self, name=None):
        """Play the specified animation or current"""
        if name and name in self.animations:
            self.current_animation = name
        
        if self.current_animation:
            self.animations[self.current_animation].play()
    
    def update(self):
        """Update current animation"""
        if self.current_animation:
            self.animations[self.current_animation].update()
    
    def get_current_frame(self):
        """Get the current frame of the current animation"""
        if self.current_animation:
            return self.animations[self.current_animation].get_current_frame()
        return None

    def is_completed(self):
        """Check if current animation is completed"""
        if self.current_animation:
            return self.animations[self.current_animation].completed
        return True


class SpriteSheet:
    """
    Utility for loading and parsing sprite sheets
    """
    def __init__(self, filename):
        """
        Initialize with the path to the spritesheet image
        """
        self.sheet = pygame.image.load(filename).convert_alpha()
    
    def get_image(self, x, y, width, height, scale=1.0, colorkey=None):
        """Extract image from sheet"""
        # Create a new blank image
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Copy the sprite from the sheet
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        
        # Scale the image if needed
        if scale != 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = pygame.transform.scale(image, (new_width, new_height))
        
        # Set colorkey if specified
        if colorkey:
            image.set_colorkey(colorkey)
            
        return image
    
    def get_animation_frames(self, start_x, start_y, width, height, columns, count, scale=1.0, colorkey=None):
        """Extract a sequence of frames for an animation"""
        frames = []
        
        for i in range(count):
            # Calculate position in the sheet
            x = start_x + (i % columns) * width
            y = start_y + (i // columns) * height
            
            frames.append(self.get_image(x, y, width, height, scale, colorkey))
        
        return frames

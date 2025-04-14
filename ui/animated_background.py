import pygame
import random
import math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, DARK_BLUE, BLUE, LIGHT_BLUE

class Particle:
    def __init__(self):
        self.reset()
    
    def reset(self):
        # Position
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        
        # Velocity
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        
        # Size and color
        self.size = random.randint(1, 3)
        self.alpha = random.randint(50, 200)
        self.color = [
            random.randint(100, 200),  # R
            random.randint(100, 200),  # G
            255,                       # B
            self.alpha
        ]  # Using list instead of tuple
        
        # Blinking
        self.blink_speed = random.uniform(0.5, 2.0)
        self.blink_offset = random.uniform(0, 2 * math.pi)
    
    def update(self, dt):
        # Move particle
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        
        # Wrap around screen edges
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0
        
        if self.y < 0:
            self.y = SCREEN_HEIGHT
        elif self.y > SCREEN_HEIGHT:
            self.y = 0
        
        # Animate alpha for blinking effect
        t = pygame.time.get_ticks() / 1000
        self.alpha = 100 + int(50 * math.sin(t * self.blink_speed + self.blink_offset))
        self.color[3] = self.alpha  # Update alpha in the list

class Connection:
    def __init__(self, particle1, particle2):
        self.particle1 = particle1
        self.particle2 = particle2
        self.max_distance = 150
    
    def should_draw(self):
        # Calculate distance between particles
        dx = self.particle1.x - self.particle2.x
        dy = self.particle1.y - self.particle2.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < self.max_distance
    
    def get_alpha(self):
        # Alpha based on distance (closer = more opaque)
        dx = self.particle1.x - self.particle2.x
        dy = self.particle1.y - self.particle2.y
        distance = math.sqrt(dx * dx + dy * dy)
        return int(255 * (1 - distance / self.max_distance))

class AnimatedBackground:
    def __init__(self, num_particles=50):
        self.particles = [Particle() for _ in range(num_particles)]
        self.connections = []
        
        # Create connections between particles
        for i in range(len(self.particles)):
            for j in range(i+1, len(self.particles)):
                self.connections.append(Connection(self.particles[i], self.particles[j]))
        
        # Create background surface with gradient
        self.bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.create_gradient_background()
        
        # Create particle surface with per-pixel alpha
        self.particle_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    def create_gradient_background(self):
        # Create a vertical gradient from dark blue to black
        for y in range(SCREEN_HEIGHT):
            # Calculate gradient color
            t = y / SCREEN_HEIGHT
            r = int((1-t) * DARK_BLUE[0])
            g = int((1-t) * DARK_BLUE[1])
            b = int((1-t) * DARK_BLUE[2])
            color = (r, g, b)
            
            # Draw a horizontal line with the calculated color
            pygame.draw.line(self.bg_surface, color, (0, y), (SCREEN_WIDTH, y))
    
    def update(self, dt):
        for particle in self.particles:
            particle.update(dt)
    
    def render(self, screen):
        # Draw the gradient background
        screen.blit(self.bg_surface, (0, 0))
        
        # Clear the particle layer
        self.particle_surface.fill((0, 0, 0, 0))
        
        # Draw connections between particles
        for connection in self.connections:
            if connection.should_draw():
                alpha = connection.get_alpha()
                pygame.draw.line(
                    self.particle_surface, 
                    (100, 150, 255, alpha), 
                    (connection.particle1.x, connection.particle1.y), 
                    (connection.particle2.x, connection.particle2.y), 
                    1
                )
        
        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(
                self.particle_surface, 
                tuple(particle.color),  # Convert list back to tuple for rendering
                (int(particle.x), int(particle.y)), 
                particle.size
            )
        
        # Draw the particle layer onto the screen
        screen.blit(self.particle_surface, (0, 0))

import pygame
import random
import math

class Particle:
    """
    Represents a single particle in a particle system
    """
    def __init__(self, x, y, color, vel_x=0, vel_y=0, size=2, life=1.0, gravity=0, 
                 fade=True, shape='circle'):
        self.x = x
        self.y = y
        self.orig_color = color
        self.color = color
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.size = size
        self.orig_size = size
        self.life = life  # Life in seconds
        self.max_life = life
        self.gravity = gravity
        self.fade = fade
        self.shape = shape
        self.alive = True
        self.shrink = True
    
    def update(self, dt):
        """Update particle state"""
        # Apply velocity
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        # Apply gravity
        self.vel_y += self.gravity * dt
        
        # Update life
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        
        # Fade color if needed
        if self.fade:
            alpha = (self.life / self.max_life) * 255
            # Handle both RGB and RGBA colors
            if len(self.orig_color) == 3:
                r, g, b = self.orig_color
                self.color = (r, g, b, int(alpha))
            elif len(self.orig_color) == 4:
                r, g, b, _ = self.orig_color
                self.color = (r, g, b, int(alpha))
        
        # Shrink size if needed
        if self.shrink:
            self.size = self.orig_size * (self.life / self.max_life)
    
    def draw(self, surface):
        """Draw the particle"""
        if not self.alive:
            return
        
        if self.shape == 'circle':
            if len(self.color) == 4:  # With alpha
                # Create a temporary surface with alpha
                s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, self.color, (self.size, self.size), self.size)
                surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))
            else:
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))
        elif self.shape == 'rect':
            if len(self.color) == 4:  # With alpha
                s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
                pygame.draw.rect(s, self.color, (0, 0, self.size * 2, self.size * 2))
                surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))
            else:
                pygame.draw.rect(surface, self.color, 
                             (int(self.x - self.size), int(self.y - self.size), 
                              int(self.size * 2), int(self.size * 2)))


class ParticleSystem:
    """
    Manages multiple particles for effects
    """
    def __init__(self):
        self.particles = []
        self.active = True
        self.emitters = {}
    
    def add_particle(self, particle):
        """Add a single particle to the system"""
        self.particles.append(particle)
    
    def add_particles(self, x, y, count, color, vel_range=(-1, 1), size_range=(1, 3), 
                     life_range=(0.5, 1.5), gravity=0, fade=True, shape='circle'):
        """Add multiple particles at once"""
        for _ in range(count):
            # Random velocity within range
            vel_x = random.uniform(vel_range[0], vel_range[1])
            vel_y = random.uniform(vel_range[0], vel_range[1])
            
            # Random size within range
            size = random.uniform(size_range[0], size_range[1])
            
            # Random life within range
            life = random.uniform(life_range[0], life_range[1])
            
            # Create particle with slight position variation
            pos_x = x + random.uniform(-2, 2)
            pos_y = y + random.uniform(-2, 2)
            
            # Add alpha component if fading
            if fade and len(color) == 3:
                color = (color[0], color[1], color[2], 255)
            
            particle = Particle(pos_x, pos_y, color, vel_x, vel_y, size, life, gravity, fade, shape)
            self.particles.append(particle)
    
    def create_emitter(self, name, x, y, rate, count, color, vel_range=(-1, 1), 
                      size_range=(1, 3), life_range=(0.5, 1.5), gravity=0, fade=True, 
                      shape='circle', duration=-1):
        """Create a particle emitter that continuously spawns particles"""
        self.emitters[name] = {
            'active': True,
            'x': x,
            'y': y,
            'rate': rate,  # Particles per second
            'count': count,  # Particles per emission
            'timer': 0,
            'color': color,
            'vel_range': vel_range,
            'size_range': size_range,
            'life_range': life_range,
            'gravity': gravity,
            'fade': fade,
            'shape': shape,
            'duration': duration,  # -1 for continuous
            'elapsed': 0
        }
    
    def set_emitter_position(self, name, x, y):
        """Update the position of an emitter"""
        if name in self.emitters:
            self.emitters[name]['x'] = x
            self.emitters[name]['y'] = y
    
    def toggle_emitter(self, name, active=None):
        """Toggle or set an emitter's active state"""
        if name in self.emitters:
            if active is not None:
                self.emitters[name]['active'] = active
            else:
                self.emitters[name]['active'] = not self.emitters[name]['active']
    
    def update(self, dt):
        """Update all particles and emitters"""
        # Update existing particles
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.alive:
                self.particles.remove(particle)
        
        # Update emitters
        for name, emitter in self.emitters.items():
            if not emitter['active']:
                continue
                
            # Update duration if applicable
            if emitter['duration'] > 0:
                emitter['elapsed'] += dt
                if emitter['elapsed'] >= emitter['duration']:
                    emitter['active'] = False
                    continue
            
            # Update timer and emit particles
            emitter['timer'] += dt
            emission_interval = 1.0 / emitter['rate']
            
            while emitter['timer'] >= emission_interval:
                emitter['timer'] -= emission_interval
                
                self.add_particles(
                    emitter['x'], emitter['y'],
                    emitter['count'],
                    emitter['color'],
                    emitter['vel_range'],
                    emitter['size_range'],
                    emitter['life_range'],
                    emitter['gravity'],
                    emitter['fade'],
                    emitter['shape']
                )
    
    def draw(self, surface):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(surface)
    
    def create_explosion(self, x, y, count=50, color=(255, 100, 20), size_range=(2, 5)):
        """Create an explosion effect"""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 150)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            size = random.uniform(size_range[0], size_range[1])
            life = random.uniform(0.5, 1.2)
            
            # Create particle with slight position variation
            pos_x = x + random.uniform(-3, 3)
            pos_y = y + random.uniform(-3, 3)
            
            # Add alpha component for fading
            if len(color) == 3:
                color = (color[0], color[1], color[2], 255)
            
            particle = Particle(pos_x, pos_y, color, vel_x, vel_y, size, life, 20, True, 'circle')
            self.particles.append(particle)
    
    def create_sparkle(self, x, y, count=20, color=(255, 255, 100)):
        """Create a sparkle effect"""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(10, 30)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            size = random.uniform(1, 3)
            life = random.uniform(0.3, 0.8)
            
            # Create particle with slight position variation
            pos_x = x + random.uniform(-2, 2)
            pos_y = y + random.uniform(-2, 2)
            
            # Add alpha component for fading
            if len(color) == 3:
                color = (color[0], color[1], color[2], 255)
            
            particle = Particle(pos_x, pos_y, color, vel_x, vel_y, size, life, -5, True, 'circle')
            self.particles.append(particle)

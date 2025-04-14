import pygame
import math
import random
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    WHITE,
    BLACK,
    LIGHT_BLUE,
    MENU_STATE,
    MENU_BG_COLOR,
    MENU_TEXT_COLOR,
    MENU_HIGHLIGHT_COLOR,
)
from ui.buttons import TextButton
from effects.particles import ParticleSystem


class CreditEntry:
    def __init__(self, id_number, name, position=(0, 0), color=LIGHT_BLUE):
        self.id_number = id_number
        self.name = name
        self.position = list(position)
        self.target_position = list(position)
        self.color = color
        self.scale = 0.0
        self.target_scale = 1.0
        self.rotation = random.randint(-10, 10)
        self.offset_y = 0
        self.wave_offset = random.random() * 10
        self.highlighted = False

    def update(self, dt):
        # Smooth movement
        dx = self.target_position[0] - self.position[0]
        dy = self.target_position[1] - self.position[1]

        self.position[0] += dx * 3 * dt
        self.position[1] += dy * 3 * dt

        # Smooth scaling
        scale_diff = self.target_scale - self.scale
        self.scale += scale_diff * 5 * dt

        # Wave animation
        self.wave_offset += dt * 2
        self.offset_y = math.sin(self.wave_offset) * 5 if self.highlighted else 0


class CreditsScreen:
    def __init__(self, game_engine, asset_manager):
        self.game_engine = game_engine
        self.assets = asset_manager

        # Fonts
        self.title_font = pygame.font.SysFont(None, 60)
        self.subtitle_font = pygame.font.SysFont(None, 48)
        self.credit_font = pygame.font.SysFont(None, 32)
        self.id_font = pygame.font.SysFont(None, 24)

        # Create starfield background
        self.background = self.create_starfield_background()
        self.stars = []
        for _ in range(100):
            self.stars.append(
                [
                    random.randint(0, SCREEN_WIDTH),
                    random.randint(0, SCREEN_HEIGHT),
                    random.random() * 2 + 0.5,  # Size
                ]
            )

        # Create particles
        self.particles = ParticleSystem()
        self.particles.create_emitter(
            "ambient",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            2,
            1,  # Changed from 0.3 to 1 (integer value)
            (100, 150, 255, 100),
            vel_range=(-40, 40),
            size_range=(2, 5),
            life_range=(2, 5),
            fade=True,
        )

        # Credits data - ID, Name pairs
        self.credits = [
            CreditEntry("221-15-4682", "Anupam Abir Kolin"),
            CreditEntry("221-15-5253", "Faria Afrose Limpa"),
            CreditEntry("221-15-5665", "Md Soroar Jahan"),
            CreditEntry("221-15-5439", "Farhan Mahmud"),
            CreditEntry("221-15-4934", "Farhan Tanvir"),
        ]

        # Position credits in a circle
        self.position_credits()

        # Animation properties
        self.time = 0
        self.rotation = 0
        self.highlight_index = 0
        self.highlight_timer = 0
        self.highlight_interval = 3.0  # Change highlight every 3 seconds

        # Create back button
        self.back_button = TextButton(
            "Back to Menu",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70),
            (200, 50),
            self.return_to_menu,
        )

    def create_starfield_background(self):
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.fill((10, 15, 30))  # Dark blue background

        # Draw some distant stars (dots)
        for _ in range(200):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            radius = random.random() * 1.5
            brightness = random.randint(150, 255)
            color = (brightness, brightness, brightness)
            pygame.draw.circle(surface, color, (x, y), radius)

        # Draw some nebula-like shapes
        for _ in range(5):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            width = random.randint(100, 300)
            height = random.randint(100, 300)

            # Create a nebula surface with alpha
            nebula = pygame.Surface((width, height), pygame.SRCALPHA)

            # Random nebula color (blues and purples)
            r = random.randint(0, 100)
            g = random.randint(0, 100)
            b = random.randint(150, 255)

            # Draw the nebula with radial gradient
            for radius in range(min(width, height) // 2, 0, -2):
                alpha = int(100 * (radius / (min(width, height) // 2)))
                pygame.draw.ellipse(
                    nebula,
                    (r, g, b, alpha),
                    (width // 2 - radius, height // 2 - radius, radius * 2, radius * 2),
                )

            surface.blit(nebula, (x - width // 2, y - height // 2))

        return surface

    def position_credits(self):
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2 - 50
        radius = 180

        for i, credit in enumerate(self.credits):
            angle = (i / len(self.credits)) * 2 * math.pi
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            credit.position = [x, y]
            credit.target_position = [x, y]

    def rotate_credits(self, angle):
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2 - 50
        radius = 180

        for i, credit in enumerate(self.credits):
            # Offset angle for each credit
            credit_angle = angle + (i / len(self.credits)) * 2 * math.pi

            # Calculate new target position
            x = center_x + radius * math.cos(credit_angle)
            y = center_y + radius * math.sin(credit_angle)

            credit.target_position = [x, y]

    def return_to_menu(self):
        self.game_engine.state_manager.change_state(MENU_STATE)

    def handle_event(self, event):
        self.back_button.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.return_to_menu()

        if event.type == pygame.MOUSEMOTION:
            # Check if mouse is hovering over any credit
            mouse_pos = pygame.mouse.get_pos()
            for credit in self.credits:
                # Check approximate distance for hover
                dx = mouse_pos[0] - credit.position[0]
                dy = mouse_pos[1] - credit.position[1]
                distance = math.sqrt(dx * dx + dy * dy)

                if distance < 100:  # Hover radius
                    credit.target_scale = 1.2
                    self.particles.create_sparkle(
                        credit.position[0], credit.position[1], 5, (200, 200, 255)
                    )
                else:
                    credit.target_scale = 1.0

    def update(self, dt):
        self.time += dt
        self.back_button.update(dt)
        self.particles.update(dt)

        # Update stars for parallax effect
        for star in self.stars:
            star[1] += dt * 20 * star[2]  # Move based on size (parallax)
            if star[1] > SCREEN_HEIGHT:
                star[0] = random.randint(0, SCREEN_WIDTH)
                star[1] = 0
                star[2] = random.random() * 2 + 0.5

        # Gently rotate the credits
        self.rotation += dt * 0.1
        self.rotate_credits(self.rotation)

        # Update highlight
        self.highlight_timer += dt
        if self.highlight_timer >= self.highlight_interval:
            # Reset highlight on previous
            self.credits[self.highlight_index].highlighted = False

            # Move to next credit
            self.highlight_index = (self.highlight_index + 1) % len(self.credits)

            # Set new highlight
            self.credits[self.highlight_index].highlighted = True

            # Create special effect around highlighted credit
            pos = self.credits[self.highlight_index].position
            self.particles.create_explosion(pos[0], pos[1], 20, (100, 200, 255))

            # Reset timer
            self.highlight_timer = 0

        # Update credit entries
        for credit in self.credits:
            credit.update(dt)

    def render(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))

        # Draw moving stars
        for star in self.stars:
            pygame.draw.circle(
                screen, WHITE, (int(star[0]), int(star[1])), int(star[2])
            )

        # Draw particles
        self.particles.draw(screen)

        # Draw title
        title_text = self.title_font.render("CREDITS", True, WHITE)
        title_shadow = self.title_font.render("CREDITS", True, (0, 0, 100))

        # Draw title with shadow effect
        screen.blit(
            title_shadow, (SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 3, 53)
        )
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

        # Draw subtitle
        subtitle_text = self.subtitle_font.render("Development Team", True, LIGHT_BLUE)
        screen.blit(
            subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, 110)
        )

        # Draw each credit entry
        for credit in self.credits:
            # Scale factor for text
            scale = credit.scale

            # Get text objects
            name_text = self.credit_font.render(
                credit.name,
                True,
                LIGHT_BLUE if not credit.highlighted else (200, 255, 255),
            )
            id_text = self.id_font.render(credit.id_number, True, WHITE)

            # Create scaled versions if needed
            if abs(scale - 1.0) > 0.01:
                name_w = int(name_text.get_width() * scale)
                name_h = int(name_text.get_height() * scale)
                name_text = pygame.transform.scale(name_text, (name_w, name_h))

                id_w = int(id_text.get_width() * scale)
                id_h = int(id_text.get_height() * scale)
                id_text = pygame.transform.scale(id_text, (id_w, id_h))

            # Position texts
            name_pos = (
                credit.position[0] - name_text.get_width() // 2,
                credit.position[1] - name_text.get_height() + credit.offset_y,
            )
            id_pos = (
                credit.position[0] - id_text.get_width() // 2,
                credit.position[1] + 5 + credit.offset_y,
            )

            # Draw texts
            screen.blit(name_text, name_pos)
            screen.blit(id_text, id_pos)

            # Draw connecting line to center for highlighted credit
            if credit.highlighted:
                center_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
                pygame.draw.line(
                    screen, (100, 200, 255), center_pos, credit.position, 2
                )

                # Draw pulsing circle around highlighted credit
                pulse = (math.sin(self.time * 5) + 1) * 0.5  # 0 to 1
                radius = 40 + pulse * 15
                pygame.draw.circle(
                    screen,
                    (100, 200, 255, 50),
                    (int(credit.position[0]), int(credit.position[1])),
                    int(radius),
                    3,
                )

        # Draw back button
        self.back_button.render(screen)

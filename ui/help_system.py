import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, LIGHT_BLUE


class HelpSystem:
    """
    Provides contextual help and tooltips throughout the game
    """

    def __init__(self, asset_manager):
        self.assets = asset_manager
        self.font = pygame.font.SysFont(None, 20)
        self.title_font = pygame.font.SysFont(None, 28)

        # Help topics by category
        self.topics = {
            "general": {
                "navigation": {
                    "title": "Navigation",
                    "content": "Use arrow keys to navigate menus and movement.\n"
                    + "Press Enter to select options or interact.\n"
                    + "Press ESC to go back or access the pause menu.",
                },
                "saving": {
                    "title": "Saving Progress",
                    "content": "Your game is automatically saved when completing levels.\n"
                    + "You can also manually save from the pause menu.",
                },
            },
            "maze_level": {
                "movement": {
                    "title": "Maze Movement",
                    "content": "Use arrow keys to move through the maze.\n"
                    + "The goal is to reach the exit marker.",
                },
                "algorithms": {
                    "title": "Search Algorithms",
                    "content": "BFS (Breadth-First Search): Finds the shortest path by exploring\n"
                    + "all neighboring nodes before moving deeper.\n\n"
                    + "DFS (Depth-First Search): Explores as far as possible down each\n"
                    + "branch before backtracking.",
                },
            },
            "water_jug": {
                "rules": {
                    "title": "Water Jug Rules",
                    "content": "You have two jugs with different capacities.\n"
                    + "The goal is to measure a specific amount of water.",
                },
                "actions": {
                    "title": "Available Actions",
                    "content": "Fill: Fill a jug completely\n"
                    + "Empty: Empty a jug completely\n"
                    + "Pour: Pour water from one jug to another",
                },
            },
            "tictactoe": {
                "gameplay": {
                    "title": "Tic-Tac-Toe Gameplay",
                    "content": "Place marks on a 3x3 grid aiming to get three in a row.\n"
                    + "You play as X and the AI plays as O.",
                },
                "minimax": {
                    "title": "Minimax Algorithm",
                    "content": "The AI uses the Minimax algorithm to make optimal moves.\n"
                    + "It simulates all possible future moves and chooses the best one.",
                },
            },
            "strategy": {
                "gameplay": {
                    "title": "Strategy Game",
                    "content": "A turn-based strategy game where you must outmaneuver the opponent.\n"
                    + "Capture all opponent pieces to win.",
                },
                "alphabeta": {
                    "title": "Alpha-Beta Pruning",
                    "content": "An optimization of the Minimax algorithm that ignores branches\n"
                    + "which cannot affect the final decision, making AI faster.",
                },
            },
        }

        # Active tooltips
        self.active_tooltips = []

        # Current help overlay
        self.help_overlay_active = False
        self.current_category = "general"
        self.current_topic_key = None
        self.help_scroll_offset = 0
        self.max_scroll = 0

    def show_tooltip(self, text, position, duration=3.0, anchor="bottom"):
        """
        Show a tooltip at the specified position
        anchor: top, bottom, left, right - which side of the position to anchor to
        """
        self.active_tooltips.append(
            {
                "text": text,
                "position": position,
                "duration": duration,
                "elapsed": 0,
                "anchor": anchor,
            }
        )

    def show_help(self, category, topic_key):
        """Show help overlay for a specific topic"""
        if category in self.topics and topic_key in self.topics[category]:
            self.help_overlay_active = True
            self.current_category = category
            self.current_topic_key = topic_key
            self.help_scroll_offset = 0
            return True
        return False

    def show_help_index(self, category=None):
        """Show index of help topics"""
        self.help_overlay_active = True
        self.current_category = category if category else "general"
        self.current_topic_key = None
        self.help_scroll_offset = 0

    def hide_help(self):
        """Hide the help overlay"""
        self.help_overlay_active = False

    def toggle_help(self):
        """Toggle the help overlay"""
        self.help_overlay_active = not self.help_overlay_active
        if self.help_overlay_active and not self.current_topic_key:
            self.current_category = "general"

    def handle_event(self, event):
        """Handle events for help system"""
        if not self.help_overlay_active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_h:
                self.hide_help()
                return True

            elif event.key == pygame.K_UP:
                # Scroll up
                self.help_scroll_offset = max(0, self.help_scroll_offset - 20)
                return True

            elif event.key == pygame.K_DOWN:
                # Scroll down
                self.help_scroll_offset = min(
                    self.max_scroll, self.help_scroll_offset + 20
                )
                return True

            elif event.key == pygame.K_BACKSPACE:
                # Go back to index if viewing a topic
                if self.current_topic_key:
                    self.current_topic_key = None
                    self.help_scroll_offset = 0
                    return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.help_scroll_offset = max(0, self.help_scroll_offset - 20)
                return True
            elif event.button == 5:  # Scroll down
                self.help_scroll_offset = min(
                    self.max_scroll, self.help_scroll_offset + 20
                )
                return True
            elif event.button == 1:  # Left click
                # Check if clicking on a topic in the index
                if not self.current_topic_key:
                    mouse_pos = pygame.mouse.get_pos()
                    help_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, 100, 600, 500)

                    if help_rect.collidepoint(mouse_pos):
                        # Calculate which topic was clicked
                        relative_y = (
                            mouse_pos[1] - help_rect.top + self.help_scroll_offset
                        )
                        topic_height = 40
                        clicked_index = relative_y // topic_height

                        # Get list of topics in current category
                        topics = list(self.topics.get(self.current_category, {}).keys())

                        if 0 <= clicked_index < len(topics):
                            self.current_topic_key = topics[clicked_index]
                            self.help_scroll_offset = 0
                            return True

        return False

    def update(self, dt):
        """Update tooltips and help overlay"""
        # Update tooltips
        for tooltip in self.active_tooltips[:]:
            tooltip["elapsed"] += dt
            if tooltip["elapsed"] >= tooltip["duration"]:
                self.active_tooltips.remove(tooltip)

    def render(self, screen):
        """Render tooltips and help overlay"""
        # Render tooltips
        for tooltip in self.active_tooltips:
            text = self.font.render(tooltip["text"], True, WHITE)
            position = tooltip["position"]

            # Calculate position based on anchor
            if tooltip["anchor"] == "bottom":
                x = position[0] - text.get_width() // 2
                y = position[1] + 10
            elif tooltip["anchor"] == "top":
                x = position[0] - text.get_width() // 2
                y = position[1] - text.get_height() - 10
            elif tooltip["anchor"] == "left":
                x = position[0] - text.get_width() - 10
                y = position[1] - text.get_height() // 2
            else:  # right
                x = position[0] + 10
                y = position[1] - text.get_height() // 2

            # Draw background
            padding = 5
            bg_rect = pygame.Rect(
                x - padding,
                y - padding,
                text.get_width() + padding * 2,
                text.get_height() + padding * 2,
            )

            # Fade based on elapsed time
            alpha = 255
            if tooltip["elapsed"] > tooltip["duration"] - 1.0:
                fade_time = tooltip["duration"] - tooltip["elapsed"]
                alpha = max(0, int(255 * fade_time))

            bg = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg.fill((20, 20, 30, min(200, alpha)))
            pygame.draw.rect(
                bg, (100, 150, 200, alpha), (0, 0, bg_rect.width, bg_rect.height), 1
            )
            screen.blit(bg, bg_rect)

            # Apply alpha to text
            text.set_alpha(alpha)
            screen.blit(text, (x, y))

        # Render help overlay
        if self.help_overlay_active:
            self._render_help_overlay(screen)

    def _render_help_overlay(self, screen):
        """Render the help overlay"""
        # Draw semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

        # Draw help panel
        help_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, 100, 600, 500)
        pygame.draw.rect(screen, (30, 30, 50), help_rect)
        pygame.draw.rect(screen, LIGHT_BLUE, help_rect, 2)

        # Draw title
        title = "Help: " + self.current_category.replace("_", " ").title()
        title_text = self.title_font.render(title, True, LIGHT_BLUE)
        screen.blit(
            title_text,
            (help_rect.centerx - title_text.get_width() // 2, help_rect.top + 20),
        )

        # Draw content based on whether we're showing the index or a topic
        if self.current_topic_key:
            self._render_topic_content(screen, help_rect)
        else:
            self._render_topic_index(screen, help_rect)

        # Draw navigation help
        nav_text = self.font.render(
            "ESC: Close  |  ↑/↓: Scroll  |  Backspace: Back to Index", True, WHITE
        )
        screen.blit(
            nav_text,
            (help_rect.centerx - nav_text.get_width() // 2, help_rect.bottom - 30),
        )

    def _render_topic_index(self, screen, help_rect):
        """Render the index of topics in the current category"""
        # Draw category list on the left
        categories = list(self.topics.keys())
        cat_x = help_rect.left + 20
        cat_y = help_rect.top + 60

        for category in categories:
            display_name = category.replace("_", " ").title()

            # Highlight current category
            if category == self.current_category:
                cat_text = self.font.render(display_name, True, LIGHT_BLUE)
            else:
                cat_text = self.font.render(display_name, True, WHITE)

            screen.blit(cat_text, (cat_x, cat_y))
            cat_y += 30

        # Draw separator line
        pygame.draw.line(
            screen,
            LIGHT_BLUE,
            (help_rect.left + 150, help_rect.top + 60),
            (help_rect.left + 150, help_rect.bottom - 40),
            1,
        )

        # Draw topics in current category
        topic_x = help_rect.left + 170
        base_topic_y = help_rect.top + 60

        # Apply scroll offset
        topic_y = base_topic_y - self.help_scroll_offset

        topics = self.topics.get(self.current_category, {})

        for key, topic in topics.items():
            # Skip if outside visible area
            if topic_y + 40 < help_rect.top + 60:
                topic_y += 40
                continue

            if topic_y > help_rect.bottom - 40:
                break

            # Draw topic title
            topic_title = self.font.render(topic["title"], True, WHITE)
            screen.blit(topic_title, (topic_x, topic_y))

            # Draw a short preview
            preview = topic["content"].split("\n")[0]
            if len(preview) > 50:
                preview = preview[:47] + "..."

            preview_text = self.font.render(preview, True, (180, 180, 180))
            screen.blit(preview_text, (topic_x, topic_y + 20))

            topic_y += 40

        # Calculate max scroll
        total_height = len(topics) * 40
        visible_height = help_rect.height - 100  # Accounting for header and footer
        self.max_scroll = max(0, total_height - visible_height)

        # Draw scroll indicators if needed
        if self.max_scroll > 0:
            if self.help_scroll_offset > 0:
                # Up arrow
                pygame.draw.polygon(
                    screen,
                    WHITE,
                    [
                        (help_rect.right - 20, help_rect.top + 60),
                        (help_rect.right - 30, help_rect.top + 70),
                        (help_rect.right - 10, help_rect.top + 70),
                    ],
                )

            if self.help_scroll_offset < self.max_scroll:
                # Down arrow
                pygame.draw.polygon(
                    screen,
                    WHITE,
                    [
                        (help_rect.right - 20, help_rect.bottom - 50),
                        (help_rect.right - 30, help_rect.bottom - 60),
                        (help_rect.right - 10, help_rect.bottom - 60),
                    ],
                )

    def _render_topic_content(self, screen, help_rect):
        """Render the content of a specific topic"""
        topic = self.topics[self.current_category][self.current_topic_key]

        # Draw topic title
        topic_title = self.title_font.render(topic["title"], True, WHITE)
        screen.blit(topic_title, (help_rect.left + 20, help_rect.top + 60))

        # Draw horizontal separator
        pygame.draw.line(
            screen,
            LIGHT_BLUE,
            (help_rect.left + 20, help_rect.top + 90),
            (help_rect.right - 20, help_rect.top + 90),
            1,
        )

        # Draw content with scroll offset
        content_y = help_rect.top + 110 - self.help_scroll_offset

        # Split content into lines
        lines = topic["content"].split("\n")
        for line in lines:
            # Skip if outside visible area
            if content_y + 25 < help_rect.top + 110:
                content_y += 25
                continue

            if content_y > help_rect.bottom - 40:
                break

            content_text = self.font.render(line, True, WHITE)
            screen.blit(content_text, (help_rect.left + 20, content_y))
            content_y += 25

        # Calculate max scroll
        total_height = len(lines) * 25
        visible_height = help_rect.height - 150  # Accounting for header and footer
        self.max_scroll = max(0, total_height - visible_height)

        # Draw scroll indicators if needed
        if self.max_scroll > 0:
            if self.help_scroll_offset > 0:
                # Up arrow
                pygame.draw.polygon(
                    screen,
                    WHITE,
                    [
                        (help_rect.right - 20, help_rect.top + 110),
                        (help_rect.right - 30, help_rect.top + 120),
                        (help_rect.right - 10, help_rect.top + 120),
                    ],
                )

            if self.help_scroll_offset < self.max_scroll:
                # Down arrow
                pygame.draw.polygon(
                    screen,
                    WHITE,
                    [
                        (help_rect.right - 20, help_rect.bottom - 50),
                        (help_rect.right - 30, help_rect.bottom - 60),
                        (help_rect.right - 10, help_rect.bottom - 60),
                    ],
                )

import pygame

from settings import WINDOW_WIDTH, WINDOW_HEIGHT

class PyGameProgressBar:
    def __init__(self, surface, position: int = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 10), size: int = (round(WINDOW_WIDTH * 0.9, 2), 30), colors=None, text=""):
        self.surface = surface
        self.x, self.y = position
        self.width, self.height = size
        
        # Default colors (background, border, fill)
        self.colors = colors or {
            'background': (200, 200, 200),  # Light gray
            'border': (100, 100, 100),      # Dark gray
            'fill': (50, 150, 50),          # Green
            'text': (0, 0, 0)               # Black
        }
        
        self.progress = 0.0
        self.text = text
        self.font = pygame.font.Font(None, 24)
        self.border_width = 2
        self._visible = False

    def update(self, current, total):
        """Update progress bar value"""
        if total > 0:
            # Validate and update progress without changing visibility
            new_progress = current / total
            self.progress = max(0.0, min(1.0, new_progress))
        else:
            self.progress = 0.0

    def set_text(self, text):
        """Set the text displayed on the progress bar"""
        self.text = text
    def set_colors(self, background=None, border=None, fill=None, text=None):
        """Update progress bar colors"""
        if background:
            self.colors['background'] = background
        if border:
            self.colors['border'] = border
        if fill:
            self.colors['fill'] = fill
        if text:
            self.colors['text'] = text

    def render(self):
        """Draw the progress bar on the surface"""
        # Draw background
        pygame.draw.rect(
            self.surface,
            self.colors['background'],
            (self.x - self.width / 2, self.y - self.height, self.width, self.height)
        )
        
        # Draw border
        pygame.draw.rect(
            self.surface,
            self.colors['border'],
            (self.x - self.width / 2, self.y - self.height, self.width, self.height),
            self.border_width
        )
        
        # Draw fill
        fill_width = int(self.width * self.progress)
        if fill_width > 0:
            pygame.draw.rect(
                self.surface,
                self.colors['fill'],
                (self.x - self.width / 2 + self.border_width,
                 self.y - self.height + self.border_width,
                 fill_width - (self.border_width * 2),
                 self.height - (self.border_width * 2))
            )
        
        # Draw text
        if self.text:
            text_surface = self.font.render(
                f"{self.text} {int(self.progress * 100)}%",
                True,
                self.colors['text']
            )
            text_rect = text_surface.get_rect()
            text_rect.center = (self.x, self.y - self.height / 2)
            self.surface.blit(text_surface, text_rect)

    def reset(self):
        """Reset progress bar to initial state"""
        self.progress = 0.0
        self._visible = False

    def show(self):
        """Make the progress bar visible"""
        self._visible = True

    def hide(self):
        """Hide the progress bar"""
        self._visible = False

    def is_active(self):
        """Check if progress bar should be displayed"""
        return self._visible

    def draw(self):
        """Draw the progress bar if it's active"""
        if self._visible:
            self.render()
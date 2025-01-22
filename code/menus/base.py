from __future__ import annotations

# Standard library imports
import sys
from typing import List, Tuple, Optional

# Third-party imports
import pygame

# Local imports
from settings import (
    PYGAME_COLORS,
    WINDOW_WIDTH,
    WINDOW_HEIGHT
)

import logging_util

# Create logger for this module
logger = logging_util.logging.getLogger(__name__)
logger.setLevel(logging_util.LOG_LEVEL)
logger.addHandler(logging_util.file_handler)
logger.addHandler(logging_util.stream_handler)

class Menus:
    def __init__(self, surface: pygame.Surface):
        self.display_surface = surface
        self.font = pygame.font.Font(None, 36)
        self.items: List[str] = []
        self.item_rects: List[pygame.Rect] = []
        self.selected_item: Optional[int] = None
        self.current_selection_index: Optional[int] = None

    def calculate_positions(self) -> None:
        """Calculate positions for menu items."""
        self.item_rects.clear()
        menu_y = WINDOW_HEIGHT // 2 - len(self.items) * 25
        
        for item in self.items:
            text = self.font.render(item, True, PYGAME_COLORS['white'])
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, menu_y))
            self.item_rects.append(text_rect)
            menu_y += 50
            
    def get_clicked_item(self, mouse_pos: Tuple[int, int]) -> Optional[int]:
        """Return the index of the clicked menu item."""
        for i, rect in enumerate(self.item_rects):
            if rect.collidepoint(mouse_pos):
                return i
        return None
    
    def render(self) -> None:
        """Render menu items on the display surface."""
        for i, (item, rect) in enumerate(zip(self.items, self.item_rects)):
            color = PYGAME_COLORS['gold'] if i == self.selected_item or i == self.current_selection_index else PYGAME_COLORS['white']
            text = self.font.render(item, True, color)
            self.display_surface.blit(text, rect)

    def handle_keyboard_navigation(self, direction: str) -> None:
        """Update current_selection_index based on keyboard input direction."""
        if not self.items:
            return

        if self.current_selection_index is None:
            self.current_selection_index = 0
            return

        if direction == 'up':
            if self.current_selection_index > 0:
                self.current_selection_index -= 1
            else:
                self.current_selection_index = len(self.items) - 1
        elif direction == 'down':
            if self.current_selection_index < len(self.items) - 1:
                self.current_selection_index += 1
            else:
                self.current_selection_index = 0

    def handle_selection(self) -> Optional[str]:
        """Handle selection of the current menu item."""
        if self.current_selection_index is not None:
            return self.items[self.current_selection_index]
        elif self.selected_item is not None:
            return self.items[self.selected_item]
        return None
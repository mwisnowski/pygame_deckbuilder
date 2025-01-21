from __future__ import annotations

# Standard library imports
import sys
from typing import List, Tuple, Optional

# Third-party imports
import pygame
# Local imports
from settings import (
    COLORS,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MAIN_MENU_ITEMS,
    SETUP_MENU_ITEMS
)

import logging_util

# Create logger for this module
logger = logging_util.logging.getLogger(__name__)
logger.setLevel(logging_util.LOG_LEVEL)

# Add handlers to logger
logger.addHandler(logging_util.file_handler)
logger.addHandler(logging_util.stream_handler)

class Menus:
    def __init__(self, surface: pygame.Surface):
        self.display_surface = surface
        self.font = pygame.font.Font(None, 36)
        self.items: List[str] = []
        self.item_rects: List[pygame.Rect] = []
        self.selected_item: Optional[int] = None
        
    def calculate_positions(self) -> None:
        """Calculate positions for menu items."""
        self.item_rects.clear()
        menu_y = WINDOW_HEIGHT // 2 - len(self.items) * 25
        
        for item in self.items:
            text = self.font.render(item, True, COLORS['white'])
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
            color = COLORS['gold'] if i == self.selected_item else COLORS['white']
            text = self.font.render(item, True, color)
            self.display_surface.blit(text, rect)

class MainMenu(Menus):
    def __init__(self, surface: pygame.Surface):
        super().__init__(surface)
        self.items = MAIN_MENU_ITEMS
        self.calculate_positions()
        
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """Update menu state based on mouse position."""
        self.selected_item = self.get_clicked_item(mouse_pos)
        
    def handle_click(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """Handle mouse click and return selected action."""
        clicked_index = self.get_clicked_item(mouse_pos)
        if clicked_index is not None:
            action = self.items[clicked_index]
            return action
        return None


class SetupMenu(Menus):
    def __init__(self, surface: pygame.Surface):
        super().__init__(surface)
        self.items = SETUP_MENU_ITEMS
        self.calculate_positions()
        
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """Update menu state based on mouse position."""
        self.selected_item = self.get_clicked_item(mouse_pos)
        
    def handle_click(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """Handle mouse click and return selected action."""
        clicked_index = self.get_clicked_item(mouse_pos)
        if clicked_index is not None:
            action = self.items[clicked_index]
            return action
        return None
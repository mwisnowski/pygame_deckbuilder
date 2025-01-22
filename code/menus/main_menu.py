from __future__ import annotations

import pygame
from settings import PYGAME_COLORS, WINDOW_WIDTH, WINDOW_HEIGHT
from settings import MAIN_MENU_ITEMS
from .base import Menus
import logging_util

# Create logger for this module
logger = logging_util.logging.getLogger(__name__)
logger.setLevel(logging_util.LOG_LEVEL)
logger.addHandler(logging_util.file_handler)
logger.addHandler(logging_util.stream_handler)

class MainMenu(Menus):
    """Main menu class that handles the primary navigation menu."""
    
    def __init__(self, surface: pygame.Surface):
        super().__init__(surface)
        self.items = MAIN_MENU_ITEMS
        self.calculate_positions()
    
    def update(self, mouse_pos: tuple[int, int]) -> None:
        """Update menu state based on mouse position."""
        self.selected_item = self.get_clicked_item(mouse_pos)
        # Reset keyboard selection when mouse moves
        if self.selected_item is not None:
            self.current_selection_index = None

        # Initialize keyboard selection if nothing is selected
        if self.selected_item is None and self.current_selection_index is None:
            self.current_selection_index = 0

    def handle_click(self, mouse_pos: tuple[int, int]) -> str | None:
        """Handle mouse click and return selected action."""
        clicked_index = self.get_clicked_item(mouse_pos)
        if clicked_index is not None:
            action = self.items[clicked_index]
            return action
        return None
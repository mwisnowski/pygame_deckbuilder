from __future__ import annotations

# Standard library imports
from typing import Optional, Tuple

# Third-party imports
import pygame

# Local imports
from .base import Menus
from settings import SETUP_MENU_ITEMS
import logging_util

# Create logger for this module
logger = logging_util.logging.getLogger(__name__)
logger.setLevel(logging_util.LOG_LEVEL)
logger.addHandler(logging_util.file_handler)
logger.addHandler(logging_util.stream_handler)

class SetupMenu(Menus):
    def __init__(self, surface: pygame.Surface):
        super().__init__(surface)
        self.items = SETUP_MENU_ITEMS
        self.calculate_positions()
        
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """Update menu state based on mouse position."""
        self.selected_item = self.get_clicked_item(mouse_pos)
        # Reset keyboard selection when mouse moves
        if self.selected_item is not None:
            self.current_selection_index = None

        # Initialize keyboard selection if nothing is selected
        if self.selected_item is None and self.current_selection_index is None:
            self.current_selection_index = 0

    def handle_click(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """Handle mouse click and return selected action."""
        clicked_index = self.get_clicked_item(mouse_pos)
        if clicked_index is not None:
            action = self.items[clicked_index]
            return action
        return None
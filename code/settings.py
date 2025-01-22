from __future__ import annotations

# Standard library imports
import os
from sys import exit
from typing import Dict, List, Optional, Final, Tuple, Pattern, Union, Callable

# Third-party imports
import pygame
from pygame.math import Vector2 as vector

WINDOW_WIDTH: int = 1280
WINDOW_HEIGHT: int = 720
TILESIZE: int = 64

COLORS: Dict[str, Optional[str]] = {
	'white': '#f4fefa', 
	'pure white': '#ffffff',
	'dark': '#2b292c',
	'light': '#c8c8c8',
	'gray': '#3a373b',
	'gold': '#ffd700',
	'light-gray': '#4b484d',
	'black': '#000000', 
	'red': '#f03131',
	'blue': '#66d7ee'
}

MAIN_MENU_ITEMS: List[str] = ['Build A Deck', 'Setup CSV Files', 'Tag CSV Files', 'Quit']

SETUP_MENU_ITEMS: List[str] = ['Initial Setup', 'Regenerate CSV', 'Main Menu']

CSV_DIRECTORY: str = 'csv_files'

# Configuration for handling null/NA values in DataFrame columns
FILL_NA_COLUMNS: Dict[str, Optional[str]] = {
    'colorIdentity': 'Colorless',  # Default color identity for cards without one
    'faceName': None  # Use card's name column value when face name is not available
}
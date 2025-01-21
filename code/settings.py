from __future__ import annotations

# Standard library imports
import os
from sys import exit

# Third-party imports
import pygame
from pygame.math import Vector2 as vector

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TILESIZE = 64

COLORS = {
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

MAIN_MENU_ITEMS = ['Build A Deck', 'Setup CSV Files', 'Tag CSV Files', 'Quit']

SETUP_MENU_ITEMS = ['Initial Setup', 'Regenerate CSV', 'Main Menu']
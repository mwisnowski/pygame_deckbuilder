"""
Main script for the MTG Pygame Deckbuilder application.

This module provides the main menu and user interaction functionality for the
MTG Pygame Deckbuilder. It handles menu display, user input processing, and
routing to different application features like setup, deck building, and CSV file tagging.
"""

from __future__ import annotations

# Standard library imports
import sys
import os
from pathlib import Path

# Third-party imports
# Local imports
from settings import exit, pygame, vector
from file_setup import Setup
from menus import MainMenu
from settings import (PYGAME_COLORS, WINDOW_WIDTH,
                      WINDOW_HEIGHT)
from deck_builder.builder import DeckBuilder
from tagging import tagger
import logging_util
from groups import AllSprites

# Create logger for this module
logger = logging_util.logging.getLogger(__name__)
logger.setLevel(logging_util.LOG_LEVEL)

# Add handlers to logger
logger.addHandler(logging_util.file_handler)
logger.addHandler(logging_util.stream_handler)
class Game:
    def __init__(self):
        # Add timer and flag for pop-up
        self.popup_start_time = 0
        self.showing_popup = False
        pygame.init()
        self.FONT = pygame.font.Font(None, 36)
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Magic: The Gathering, Deckbuilder')
        self.clock = pygame.time.Clock()
        
        # Groups
        self.all_sprites = AllSprites()
        self.main_menu = MainMenu(self.display_surface)
        
        # State management
        self.current_state = 'main_menu'
        self.setup = Setup(self.display_surface)
        self.tagger = tagger
        self.builder = DeckBuilder()

    def display_popup(self, message):
        # Create semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(PYGAME_COLORS['black'])
        overlay.set_alpha(128)
        self.display_surface.blit(overlay, (0, 0))

        # Render message
        text_surface = self.FONT.render(message, True, PYGAME_COLORS['white'])
        text_rect = text_surface.get_rect()
        text_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        # Draw message
        pygame.draw.rect(self.display_surface, PYGAME_COLORS['black'], 
                        text_rect.inflate(20, 20))
        self.display_surface.blit(text_surface, text_rect)

    def run(self):
        while True:
            delta_time = self.clock.tick(60) /1000
            mouse_pos = pygame.mouse.get_pos()
            
            if self.current_state == 'main_menu':
                self.main_menu.update(mouse_pos)

            # Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logger.info('Quitting game...')
                    pygame.quit()
                    exit()
                
                # Handle any input during build state to dismiss popup
                if self.current_state == 'build' and event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                    self.current_state = 'main_menu'
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.current_state == 'main_menu':
                        action = self.main_menu.handle_click(mouse_pos)
                        logger.info(f'Selected menu item: {action}')
                        if action == 'Quit':
                            logger.info('Quitting game...')
                            pygame.quit()
                            exit()
                        elif action == 'Setup CSV Files':
                            logger.info('Switching to setup menu...')
                            self.current_state = 'setup'
                        elif action == 'Tag CSV Files':
                            logger.info('Tagging CSV files...')
                            self.current_state = 'tag'
                        elif action == 'Build A Deck':
                            #logger.info('Displaying build function in progress pop-up')
                            #self.popup_start_time = pygame.time.get_ticks()
                            self.current_state = 'build'
                
                if event.type == pygame.KEYDOWN and self.current_state == 'main_menu':
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.main_menu.handle_keyboard_navigation('up')
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.main_menu.handle_keyboard_navigation('down')
                    elif event.key == pygame.K_RETURN:
                        action = self.main_menu.handle_selection()
                        if action:
                            logger.info(f'Selected menu item: {action}')
                            if action == 'Quit':
                                logger.info('Quitting game...')
                                pygame.quit()
                                exit()
                            elif action == 'Setup CSV Files':
                                logger.info('Switching to setup menu...')
                                self.current_state = 'setup'
                            elif action == 'Tag CSV Files':
                                logger.info('Tagging CSV files...')
                                self.current_state = 'tag'
                            elif action == 'Build A Deck':
                                #logger.info('Displaying build function in progress pop-up')
                                #self.popup_start_time = pygame.time.get_ticks()
                                self.current_state = 'build'
                                
            # Game logic
            self.all_sprites.update(delta_time)
            self.display_surface.fill(PYGAME_COLORS['black'])
            if self.current_state == 'main_menu':
                self.main_menu.render()
            
            elif self.current_state == 'setup':
                # Draw setup menu background
                self.display_surface.fill(PYGAME_COLORS['black'])
                
                # Run setup and check for completion
                if self.setup.run():
                    self.current_state = 'main_menu'
            
            elif self.current_state == 'tag':
                # Draw setup menu background
                self.display_surface.fill(PYGAME_COLORS['black'])
                
                # Run tagger and check for completion
                if self.tagger:
                    tagger.run_tagging()
                    self.current_state = 'main_menu'
            
            elif self.current_state == 'build':
                self.display_surface.fill(PYGAME_COLORS['black'])
                if self.builder:
                    # Update and render builder menu
                    self.builder.determine_commander()
                #self.main_menu.render()
                # Check if 2 seconds have passed
                #current_time = pygame.time.get_ticks()
                #if current_time - self.popup_start_time <= 2000:  # 2000 milliseconds = 2 seconds
                #    self.display_popup('Build function is in progress.')
                #else:
                    # Reset to main menu after popup duration
                #    self.current_state = 'main_menu'
            
            pygame.display.flip()

if __name__ == '__main__':
    game = Game()
    logger.info('Starting game')
    game.run()
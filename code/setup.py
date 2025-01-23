"""
MTG Pygame Deckbuilder setup module.

This module provides the main setup functionality for the MTG Pygame Deckbuilder
application. It handles initial setup tasks such as downloading card data,
creating color-filtered card lists, and generating commander-eligible card lists.

Key Features:
    - Initial setup and configuration
    - Card data download and processing
    - Color-based card filtering
    - Commander card list generation
    - CSV file management and validation

The module works in conjunction with setup_utils.py for utility functions and
exceptions.py for error handling.
"""

from __future__ import annotations

# Standard library imports
import sys
import os
from pathlib import Path
from enum import Enum
from typing import Union, List, Dict, Any, Optional
from settings import exit, pygame, vector

# Third party imports
import pandas as pd
# Local imports
import logging_util
from pygame_progress_bar import PyGameProgressBar
from menus import SetupMenu
from settings import PYGAME_COLORS, CSV_DIRECTORY, WINDOW_HEIGHT, WINDOW_WIDTH
from setup_constants import BANNED_CARDS, SETUP_COLORS, COLOR_ABRV, MTGJSON_API_URL
from setup_utils import (
    download_cards_csv,
    filter_by_color_identity,
    filter_dataframe,
    process_legendary_cards
)
from exceptions import (
    CSVFileNotFoundError,
    ColorFilterError,
    CommanderValidationError,
    DataFrameProcessingError,
    MTGJSONDownloadError
)

# Create logger for this module
logger = logging_util.logging.getLogger(__name__)
logger.setLevel(logging_util.LOG_LEVEL)
logger.addHandler(logging_util.file_handler)
logger.addHandler(logging_util.stream_handler)

# Create CSV directory if it doesn't exist
if not os.path.exists(CSV_DIRECTORY):
    os.makedirs(CSV_DIRECTORY)

class Setup:
    def __init__(self, surface: pygame.Surface):
        """Initialize Setup class with display surface and setup menu."""
        self.display_surface = surface
        self.setup_menu = SetupMenu(surface)
        self.running = True
        self.return_to_main = False

    def run(self) -> bool:
        """Run the setup menu loop.
        
        Returns:
            bool: True if should return to main menu, False otherwise
        """
        self.return_to_main = False
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.setup_menu.handle_keyboard_navigation('up')
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.setup_menu.handle_keyboard_navigation('down')
                    elif event.key == pygame.K_RETURN:
                        action = self.setup_menu.handle_selection()
                        if action:
                            logger.info(f'Selected menu item: {action}')
                            self.handle_menu_action(action)
                
                if event.type == pygame.MOUSEMOTION:
                    self.setup_menu.update(event.pos)
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        action = self.setup_menu.handle_click(event.pos)
                        if action:
                            logger.info(f'Selected menu item: {action}')
                            self.handle_menu_action(action)

            self.draw()
            pygame.display.update()
            if self.return_to_main:
                return True
        
        return False

    def handle_menu_action(self, action: str) -> None:
        """Handle the selected menu action.

        Args:
            action (str): The selected menu action
        """
        if action == 'Initial Setup':
            self.perform_initial_setup()
        elif action == 'Regenerate CSV':
            self.regenerate_csv()
        elif action == 'Main Menu':
            logger.info('Returning to Main Menu')
            self.return_to_main = True

    def perform_initial_setup(self) -> None:
        """Perform initial setup operations."""
        logger.info('Performing initial setup...')
        progress_bar = PyGameProgressBar(
            self.display_surface
        )
        progress_bar.set_text('Performing Initial Setup')
        
        self.initial_setup(progress_bar)
        
        logger.info('Initial setup completed')

    def regenerate_csv(self) -> None:
        """Regenerate CSV files."""
        logger.info('Regenerating CSV files...')
        progress_bar = PyGameProgressBar(
            self.display_surface
        )
        progress_bar.set_text('Regenerating CSV Files')
        
        self.regenerate_csvs_all(progress_bar)
        logger.info('CSV regeneration completed')

    def draw(self) -> None:
        """Draw the setup menu."""
        self.display_surface.fill(PYGAME_COLORS['black'])
        self.setup_menu.render()
    
    def check_csv_exists(self, file_path: Union[str, Path]) -> bool:
        """Check if a CSV file exists at the specified path.
    
        Args:
            file_path: Path to the CSV file to check
            
        Returns:
            bool: True if file exists, False otherwise
            
        Raises:
            CSVFileNotFoundError: If there are issues accessing the file path
        """
        try:
            with open(file_path, 'r', encoding='utf-8'):
                return True
        except FileNotFoundError:
            return False
        except Exception as e:
            raise CSVFileNotFoundError(f'Error checking CSV file: {str(e)}')
    
    def initial_setup(self, progress_bar: PyGameProgressBar) -> None:
        """Perform initial setup by downloading card data and creating filtered CSV files.
        
        Downloads the latest card data from MTGJSON if needed, creates color-filtered CSV files,
        and generates commander-eligible cards list. Uses utility functions from setup_utils.py
        for file operations and data processing.
        
        Raises:
            CSVFileNotFoundError: If required CSV files cannot be found
            MTGJSONDownloadError: If card data download fails
            DataFrameProcessingError: If data processing fails
            ColorFilterError: If color filtering fails
        """
        logger.info('Checking for cards.csv file')
        
        try:
            progress_bar.show()
            progress_bar.set_text('Checking for cards.csv')
            progress_bar.update(0, 100)
            progress_bar.draw()
            pygame.display.flip()

            cards_file = f'{CSV_DIRECTORY}/cards.csv'
            total_steps = len(SETUP_COLORS) + 3  # Download, load CSV, color files, commanders
            current_step = 0
            try:
                with open(cards_file, 'r', encoding='utf-8'):
                    logger.info('cards.csv exists')
            except FileNotFoundError:
                logger.info('cards.csv not found, downloading from mtgjson')
                download_cards_csv(MTGJSON_API_URL, cards_file, progress_bar)

            current_step += 1
            progress_bar.set_text('Loading card data')
            progress_bar.update(current_step, total_steps)
            progress_bar.draw()
            pygame.display.flip()

            df = pd.read_csv(cards_file, low_memory=False)
            df['colorIdentity'] = df['colorIdentity'].fillna('Colorless')
            pygame.event.pump()
            logger.info('Checking for color identity sorted files')
            for i in range(min(len(SETUP_COLORS), len(COLOR_ABRV))):
                # Handle pygame events to keep window responsive
                pygame.event.pump()

                current_step += 1
                if progress_bar:
                    progress_bar.set_text(f'Processing {SETUP_COLORS[i].capitalize()} cards')
                    progress_bar.update(current_step, total_steps)
                    progress_bar.draw()
                    pygame.display.flip()

                logger.info(f'Checking for {SETUP_COLORS[i]}_cards.csv')
                try:
                    with open(f'{CSV_DIRECTORY}/{SETUP_COLORS[i]}_cards.csv', 'r', encoding='utf-8'):
                        logger.info(f'{SETUP_COLORS[i]}_cards.csv exists')
                except FileNotFoundError:
                    logger.info(f'{SETUP_COLORS[i]}_cards.csv not found, creating one')
                    self.filter_by_color(df, 'colorIdentity', COLOR_ABRV[i], f'{CSV_DIRECTORY}/{SETUP_COLORS[i]}_cards.csv')

            # Generate commander list
            current_step += 1
            if progress_bar:
                progress_bar.set_text('Generating commander list')
                progress_bar.update(current_step, total_steps)
                progress_bar.draw()
                pygame.display.flip()

            self.determine_commanders()
        
        except Exception as e:
            logger.error(f'Error during initial setup: {str(e)}')
            if progress_bar:
                progress_bar.hide()
            raise

        if progress_bar:
            progress_bar.update(total_steps, total_steps)
            progress_bar.draw()
            pygame.display.flip()
            pygame.time.wait(500)  # Show completed progress briefly
            progress_bar.hide()
    
    def filter_by_color(self, df: pd.DataFrame, column_name: str, value: str, new_csv_name: Union[str, Path]) -> None:
        """Filter DataFrame by color identity and save to CSV.
        
        Args:
            df: DataFrame to filter
            column_name: Column to filter on (should be 'colorIdentity')
            value: Color identity value to filter for
            new_csv_name: Path to save filtered CSV
            
        Raises:
            ColorFilterError: If filtering fails
            DataFrameProcessingError: If DataFrame processing fails
            CSVFileNotFoundError: If CSV file operations fail
        """
        try:
            # Check if target CSV already exists
            if self.check_csv_exists(new_csv_name):
                logger.info(f'{new_csv_name} already exists, will be overwritten')
                
            filtered_df = filter_by_color_identity(df, value)
            filtered_df.to_csv(new_csv_name, index=False)
            logger.info(f'Successfully created {new_csv_name}')
        except (ColorFilterError, DataFrameProcessingError, CSVFileNotFoundError) as e:
            logger.error(f'Failed to filter by color {value}: {str(e)}')
            raise

    def determine_commanders(self, progress_bar: Optional[PyGameProgressBar] = None) -> None:
        """Generate commander_cards.csv containing all cards eligible to be commanders.
        
        This function processes the card database to identify and validate commander-eligible cards,
        applying comprehensive validation steps and filtering criteria.
        
        Raises:
            CSVFileNotFoundError: If cards.csv is missing and cannot be downloaded
            MTGJSONDownloadError: If downloading cards data fails
            CommanderValidationError: If commander validation fails
            DataFrameProcessingError: If data processing operations fail
        """
        logger.info('Starting commander card generation process')
        
        try:
            # Check for cards.csv with progress tracking
            cards_file = f'{CSV_DIRECTORY}/cards.csv'
            if not self.check_csv_exists(cards_file):
                logger.info('cards.csv not found, initiating download')
                download_cards_csv(MTGJSON_API_URL, cards_file, progress_bar)
            else:
                logger.info('cards.csv found, proceeding with processing')
                
            # Load and process cards data
            logger.info('Loading card data from CSV')
            df = pd.read_csv(cards_file, low_memory=False)
            df['colorIdentity'] = df['colorIdentity'].fillna('Colorless')
            
            # Process legendary cards with validation
            logger.info('Processing and validating legendary cards')
            try:
                filtered_df = process_legendary_cards(df)
            except CommanderValidationError as e:
                logger.error(f'Commander validation failed: {str(e)}')
                raise
            
            # Apply standard filters
            logger.info('Applying standard card filters')
            filtered_df = filter_dataframe(filtered_df, BANNED_CARDS)
            
            # Save commander cards
            logger.info('Saving validated commander cards')
            filtered_df.to_csv(f'{CSV_DIRECTORY}/commander_cards.csv', index=False)
            
            logger.info('Commander card generation completed successfully')
            
        except (CSVFileNotFoundError, MTGJSONDownloadError) as e:
            logger.error(f'File operation error: {str(e)}')
            raise
        except CommanderValidationError as e:
            logger.error(f'Commander validation error: {str(e)}')
            raise
        except Exception as e:
            logger.error(f'Unexpected error during commander generation: {str(e)}')
            raise
    
    def regenerate_csvs_all(self, progress_bar: PyGameProgressBar) -> None:
        """Regenerate all color-filtered CSV files from latest card data.
        
        Downloads fresh card data and recreates all color-filtered CSV files.
        Useful for updating the card database when new sets are released.
        
        Raises:
            MTGJSONDownloadError: If card data download fails
            DataFrameProcessingError: If data processing fails
            ColorFilterError: If color filtering fails
        """
        try:
            progress_bar.show()
            progress_bar.set_text('Downloading latest card data')
            progress_bar.update(0, 100)
            progress_bar.draw()
            pygame.display.flip()
            logger.info('Downloading latest card data from MTGJSON')
            download_cards_csv(MTGJSON_API_URL, f'{CSV_DIRECTORY}/cards.csv', progress_bar)
            
            total_steps = len(SETUP_COLORS) + 3  # Download, load, colors, commanders
            current_step = 1

            progress_bar.set_text('Loading card data')
            progress_bar.update(current_step, total_steps)
            progress_bar.draw()
            pygame.display.flip()

            logger.info('Loading and processing card data')
            df = pd.read_csv(f'{CSV_DIRECTORY}/cards.csv', low_memory=False)
            df['colorIdentity'] = df['colorIdentity'].fillna('Colorless')
            logger.info('Regenerating color identity sorted files')
            for i in range(min(len(SETUP_COLORS), len(COLOR_ABRV))):
                # Handle pygame events to keep window responsive
                pygame.event.pump()

                current_step += 1
                if progress_bar:
                    progress_bar.set_text(f'Processing {SETUP_COLORS[i].capitalize()} cards')
                    progress_bar.update(current_step, total_steps)
                    progress_bar.draw()
                    pygame.display.flip()

                color = SETUP_COLORS[i]
                color_id = COLOR_ABRV[i]
                logger.info(f'Processing {color} cards')
                self.filter_by_color(df, 'colorIdentity', color_id, f'{CSV_DIRECTORY}/{color}_cards.csv')
                
            logger.info('Regenerating commander cards')
            if progress_bar:
                progress_bar.set_text('Generating commander list')
                progress_bar.update(total_steps - 1, total_steps)
                progress_bar.draw()
                pygame.display.flip()

            self.determine_commanders()
            
            logger.info('Card database regeneration complete')
            
        except Exception as e:
            logger.error(f'Failed to regenerate card database: {str(e)}')
            if progress_bar:
                progress_bar.hide()
            raise

        if progress_bar:
            progress_bar.update(total_steps, total_steps)
            progress_bar.draw()
            pygame.display.flip()
            pygame.time.wait(500)  # Show completed progress briefly
            progress_bar.hide()

    def regenerate_csv_by_color(self, color: str) -> None:
        """Regenerate CSV file for a specific color identity.
        
        Args:
            color: Color name to regenerate CSV for (e.g. 'white', 'blue')
            
        Raises:
            ValueError: If color is not valid
            MTGJSONDownloadError: If card data download fails
            DataFrameProcessingError: If data processing fails
            ColorFilterError: If color filtering fails
        """
        try:
            if color not in SETUP_COLORS:
                raise ValueError(f'Invalid color: {color}')
                
            color_abv = COLOR_ABRV[SETUP_COLORS.index(color)]
            
            logger.info(f'Downloading latest card data for {color} cards')
            download_cards_csv(MTGJSON_API_URL, f'{CSV_DIRECTORY}/cards.csv')
            
            logger.info('Loading and processing card data')
            df = pd.read_csv(f'{CSV_DIRECTORY}/cards.csv', low_memory=False)
            df['colorIdentity'] = df['colorIdentity'].fillna('Colorless')
            
            logger.info(f'Regenerating {color} cards CSV')
            self.filter_by_color(df, 'colorIdentity', color_abv, f'{CSV_DIRECTORY}/{color}_cards.csv')
            
            logger.info(f'Successfully regenerated {color} cards database')
            
        except Exception as e:
            logger.error(f'Failed to regenerate {color} cards: {str(e)}')
            raise
    
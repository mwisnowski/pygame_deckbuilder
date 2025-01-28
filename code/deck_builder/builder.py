from __future__ import annotations

import math
import numpy as np
import os
import subprocess
import random
import sys
import time
from functools import lru_cache
from typing import Dict, List, Optional, Union

import pandas as pd
import pprint
from fuzzywuzzy import process
from tqdm import tqdm
import pygame

from settings import CSV_DIRECTORY, MULTIPLE_COPY_CARDS, UI_DIMENSIONS
from .builder_constants import (
    BASIC_LANDS, CARD_TYPES, DEFAULT_NON_BASIC_LAND_SLOTS,
    COMMANDER_CSV_PATH, FUZZY_MATCH_THRESHOLD, MAX_FUZZY_CHOICES, FETCH_LAND_DEFAULT_COUNT,
    COMMANDER_POWER_DEFAULT, COMMANDER_TOUGHNESS_DEFAULT, COMMANDER_MANA_COST_DEFAULT,
    COMMANDER_MANA_VALUE_DEFAULT, COMMANDER_TYPE_DEFAULT, COMMANDER_TEXT_DEFAULT, 
    THEME_PRIORITY_BONUS, THEME_POOL_SIZE_MULTIPLIER, DECK_DIRECTORY,
    COMMANDER_COLOR_IDENTITY_DEFAULT, COMMANDER_COLORS_DEFAULT, COMMANDER_TAGS_DEFAULT, 
    COMMANDER_THEMES_DEFAULT, COMMANDER_CREATURE_TYPES_DEFAULT, DUAL_LAND_TYPE_MAP,
    CSV_READ_TIMEOUT, CSV_PROCESSING_BATCH_SIZE, CSV_VALIDATION_RULES, CSV_REQUIRED_COLUMNS,
    STAPLE_LAND_CONDITIONS, TRIPLE_LAND_TYPE_MAP, MISC_LAND_MAX_COUNT, MISC_LAND_MIN_COUNT,
    MISC_LAND_POOL_SIZE, LAND_REMOVAL_MAX_ATTEMPTS, PROTECTED_LANDS,
    MANA_COLORS, MANA_PIP_PATTERNS, THEME_WEIGHT_MULTIPLIER
)
from . import builder_utils
from file_setup import setup_utils
from .input_handler import InputHandler
from exceptions import (
    BasicLandCountError,
    BasicLandError,
    CommanderMoveError,
    CardTypeCountError,
    CommanderColorError,
    CommanderSelectionError, 
    CommanderValidationError,
    CSVError,
    CSVReadError,
    CSVTimeoutError,
    CSVValidationError,
    DataFrameValidationError,
    DuplicateCardError,
    DeckBuilderError,
    EmptyDataFrameError,
    FetchLandSelectionError,
    FetchLandValidationError,
    IdealDeterminationError,
    LandRemovalError,
    LibraryOrganizationError,
    LibrarySortError,
    PriceAPIError,
    PriceConfigurationError,
    PriceLimitError, 
    PriceTimeoutError,
    PriceValidationError,
    ThemeSelectionError,
    ThemeWeightError,
    StapleLandError,
    ManaPipError,
    ThemeTagError,
    ThemeWeightingError,
    ThemePoolError
)
from type_definitions import (
    CommanderDict,
    CardLibraryDF,
    CommanderDF,
    LandDF,
    ArtifactDF,
    CreatureDF,
    NonCreatureDF,
    PlaneswalkerDF,
    NonPlaneswalkerDF)
import logging_util

# Create logger for this module
logger = logging_util.logging.getLogger(__name__)
logger.setLevel(logging_util.LOG_LEVEL)
logger.addHandler(logging_util.file_handler)
logger.addHandler(logging_util.stream_handler)

try:
    import scrython
    from .price_check import PriceChecker
    use_scrython = True
except ImportError:
    logger.info("Attempting to install scrython package...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "scrython"])
        import scrython
        from .price_check import PriceChecker
        use_scrython = True
    except Exception as e:
        logger.warning("Failed to install scrython. Please install it manually using 'pip install --user scrython'.")
        logger.warning(f"Error: {str(e)}")
        raise

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', 50)

def new_line(num_lines: int = 1) -> None:
    """Print specified number of newlines for formatting output.

    Args:
        num_lines (int): Number of newlines to print. Defaults to 1.

    Returns:
        None
    """
    if num_lines < 0:
        raise ValueError("Number of lines cannot be negative")
    print('\n' * num_lines)
class DeckBuilder:
    def __init__(self) -> None:
        """Initialize DeckBuilder with empty dataframes and default attributes."""
        # Initialize dataframes with type hints
        self.card_library: CardLibraryDF = pd.DataFrame({
            'Card Name': pd.Series(dtype='str'),
            'Card Type': pd.Series(dtype='str'), 
            'Mana Cost': pd.Series(dtype='str'),
            'Mana Value': pd.Series(dtype='int'),
            'Creature Types': pd.Series(dtype='object'),
            'Themes': pd.Series(dtype='object'),
            'Commander': pd.Series(dtype='bool'),
        })
        
        # Initialize component dataframes
        self.commander_df: CommanderDF = pd.DataFrame()
        self.land_df: LandDF = pd.DataFrame()
        self.artifact_df: ArtifactDF = pd.DataFrame()
        self.creature_df: CreatureDF = pd.DataFrame()
        self.noncreature_df: NonCreatureDF = pd.DataFrame()
        self.nonplaneswalker_df: NonPlaneswalkerDF = pd.DataFrame()
        # Initialize other attributes with type hints
        self.commander_info: Dict = {}
        self.max_card_price: Optional[float] = None
        self.commander_dict: CommanderDict = {}
        self.commander: str = ''
        self.commander_type: str = ''
        self.commander_text: str = ''
        self.commander_power: int = 0
        self.commander_toughness: int = 0
        self.commander_mana_cost: str = ''
        self.commander_mana_value: int = 0
        self.color_identity: Union[str, List[str]] = ''
        self.color_identity_full: str = ''
        self.colors: List[str] = []
        self.creature_types: str = ''
        self.commander_tags: List[str] = []
        self.themes: List[str] = []
        
        # Initialize handlers
        self.price_checker = PriceChecker() if PriceChecker else None
        self.input_handler = InputHandler()
        
        # Initialize input state
        self.waiting_for_input = False
        self.input_complete = False
        self.input_result = None
    
    def pause_with_message(self, message: str = "Press Enter to continue...") -> None:
        """Display a message and wait for user input.
        
        Args:
            message: Message to display before pausing
        """
        self.waiting_for_input = True
        self.input_complete = False
        self.input_handler.setup_ui(
            UI_DIMENSIONS['padding'],
            UI_DIMENSIONS['padding'],
            message
        )

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle PyGame events for the deck builder.

        Args:
            events: List of PyGame events to process
        """
        if self.waiting_for_input:
            for event in events:
                if self.input_handler.handle_event(event):
                    if self.input_handler.submitted:
                        self.input_complete = True
                        self.input_result = self.input_handler.result
                        self.waiting_for_input = False
                    return True
        return False
"""MTG Python Deckbuilder setup utilities.

This module provides utility functions for setting up and managing the MTG Python Deckbuilder
application. It handles tasks such as downloading card data, filtering cards by various criteria,
and processing legendary creatures for commander format.

Key Features:
    - Card data download from MTGJSON
    - DataFrame filtering and processing
    - Color identity filtering
    - Commander validation
    - CSV file management

The module integrates with settings.py for configuration and exceptions.py for error handling.
"""

from __future__ import annotations

# Standard library imports
import logging
import os
import requests
from pathlib import Path
from typing import List, Optional, Union, TypedDict

# Third-party imports
import pygame
import pandas as pd

# Local application imports
from setup_constants import (
    CSV_PROCESSING_COLUMNS,
    CARD_TYPES_TO_EXCLUDE,
    NON_LEGAL_SETS,
    LEGENDARY_OPTIONS,
    SORT_CONFIG,
    FILTER_CONFIG,
    COLUMN_ORDER,
    TAGGED_COLUMN_ORDER
)
from exceptions import (
    MTGJSONDownloadError,
    DataFrameProcessingError,
    ColorFilterError,
    CommanderValidationError
)
from type_definitions import CardLibraryDF
from settings import FILL_NA_COLUMNS
import logging_util
from pygame_progress_bar import PyGameProgressBar

# Create logger for this module
logger = logging_util.logging.getLogger(__name__)
logger.setLevel(logging_util.LOG_LEVEL)

# Add handlers to logger
logger.addHandler(logging_util.file_handler)
logger.addHandler(logging_util.stream_handler)

# Type definitions
class FilterRule(TypedDict):
    """Type definition for filter rules configuration."""
    exclude: Optional[List[str]]
    require: Optional[List[str]]

class FilterConfig(TypedDict):
    """Type definition for complete filter configuration."""
    layout: FilterRule
    availability: FilterRule
    promoTypes: FilterRule
    securityStamp: FilterRule

def download_cards_csv(url: str, output_path: str, progress_bar: Optional['PyGameProgressBar'] = None) -> None:
    """Download cards data from MTGJSON and save to CSV.

    Downloads card data from the specified MTGJSON URL and saves it to a local CSV file.
    Args:
        url: URL to download cards data from (typically MTGJSON API endpoint)
        output_path: Path where the downloaded CSV file will be saved
        progress_bar: Optional PyGameProgressBar instance for progress tracking.
    Raises:
        MTGJSONDownloadError: If download fails due to network issues or invalid response
    Example:
        >>> download_cards_csv('https://mtgjson.com/api/v5/cards.csv', 'cards.csv')
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        current_size = 0

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                size = f.write(chunk)
                current_size += size

                # Update progress bar if provided
                if progress_bar:
                    progress_bar.update(current_size, total_size if total_size else 0)
                    progress_bar.render()
                
                # Keep the UI responsive
                pygame.event.pump()
                
    except requests.RequestException as e:
        logger.error(f'Failed to download cards data from {url}')
        raise MTGJSONDownloadError(
            "Failed to download cards data",
            url,
            getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
        ) from e
    logger.info(f"Successfully downloaded file to {output_path}")

def filter_dataframe(df: pd.DataFrame, banned_cards: List[str], progress_bar: Optional['PyGameProgressBar'] = None) -> pd.DataFrame:
    """Apply standard filters to the cards DataFrame using configuration from settings.

    Applies a series of filters to the cards DataFrame based on configuration from settings.py.
    This includes handling null values, applying basic filters, removing illegal sets and banned cards,
    and processing special card types.

    Args:
        df: pandas DataFrame containing card data to filter
        banned_cards: List of card names that are banned and should be excluded
        progress_bar: Optional progress bar for tracking

    Returns:
        pd.DataFrame: A new DataFrame containing only the cards that pass all filters

    Raises:
        DataFrameProcessingError: If any filtering operation fails

    Example:
        >>> filtered_df = filter_dataframe(cards_df, ['Channel', 'Black Lotus'])
    """
    try:
        logger.info('Starting standard DataFrame filtering')
        total_steps = 6  # Number of filtering operations
        current_step = 0

        # Fill null values according to configuration
        for col, fill_value in FILL_NA_COLUMNS.items():
            if col == 'faceName':
                fill_value = df['name']
            df[col] = df[col].fillna(fill_value)
            logger.debug(f'Filled NA values in {col} with {fill_value}')
            
        current_step += 1
        if progress_bar:
            progress_bar.update(current_step, total_steps)
            progress_bar.render()
        pygame.event.pump()
        
        # Apply basic filters from configuration
        filtered_df = df.copy()
        filter_config: FilterConfig = FILTER_CONFIG  # Type hint for configuration
        for field, rules in filter_config.items():
            for rule_type, values in rules.items():
                if rule_type == 'exclude':
                    for value in values:
                        filtered_df = filtered_df[~filtered_df[field].str.contains(value, na=False)]
                elif rule_type == 'require':
                    for value in values:
                        filtered_df = filtered_df[filtered_df[field].str.contains(value, na=False)]
                logger.debug(f'Applied {rule_type} filter for {field}: {values}')
                
        current_step += 1
        if progress_bar:
            progress_bar.update(current_step, total_steps)
            progress_bar.render()
        pygame.event.pump()
        
        # Remove illegal sets
        for set_code in NON_LEGAL_SETS:
            filtered_df = filtered_df[~filtered_df['printings'].str.contains(set_code, na=False)]
        logger.debug('Removed illegal sets')
        
        current_step += 1
        if progress_bar:
            progress_bar.update(current_step, total_steps)
            progress_bar.render()
        pygame.event.pump()
        
        # Remove banned cards
        for card in banned_cards:
            filtered_df = filtered_df[~filtered_df['name'].str.contains(card, na=False)]
        logger.debug('Removed banned cards')
        
        current_step += 1
        if progress_bar:
            progress_bar.update(current_step, total_steps)
            progress_bar.render()
        pygame.event.pump()

        # Remove special card types
        for card_type in CARD_TYPES_TO_EXCLUDE:
            filtered_df = filtered_df[~filtered_df['type'].str.contains(card_type, na=False)]
        logger.debug('Removed special card types')
        
        current_step += 1
        if progress_bar:
            progress_bar.update(current_step, total_steps)
            progress_bar.render()
        pygame.event.pump()

        # Select columns, sort, and drop duplicates
        filtered_df = filtered_df[CSV_PROCESSING_COLUMNS]
        filtered_df = filtered_df.sort_values(
            by=SORT_CONFIG['columns'],
            key=lambda col: col.str.lower() if not SORT_CONFIG['case_sensitive'] else col
        )
        filtered_df = filtered_df.drop_duplicates(subset='faceName', keep='first')
        logger.info('Completed standard DataFrame filtering')
        
        return filtered_df

    except Exception as e:
        raise DataFrameProcessingError(f'Error filtering DataFrame: {str(e)}')

def filter_by_color_identity(df: pd.DataFrame, color_identity: str, progress_bar: Optional['PyGameProgressBar'] = None) -> pd.DataFrame:
    """Filter DataFrame by color identity with additional color-specific processing.

    This function extends the base filter_dataframe functionality with color-specific
    filtering logic. It is used by setup.py's filter_by_color function but provides
    a more robust and configurable implementation.

    Args:
        df: DataFrame to filter
        color_identity: Color identity to filter by (e.g., 'W', 'U, B', 'Colorless')
        progress_bar: Optional progress bar for tracking

    Returns:
        DataFrame filtered by color identity

    Raises:
        ColorFilterError: If color identity is invalid or filtering fails
        DataFrameProcessingError: If general filtering operations fail
    """
    try:
        logger.info(f'Filtering cards for color identity: {color_identity}')
        
        # Define total steps for progress tracking
        total_steps = 4  # Validation, base filtering, color filtering, additional processing
        current_step = 0

        # Validate color identity
        if not isinstance(color_identity, str):
            raise ColorFilterError(
                "Invalid color identity type",
                str(color_identity),
                "Color identity must be a string"
            )
        current_step += 1
        if progress_bar:
            progress_bar.update(current_step, total_steps)
            progress_bar.render()
        pygame.event.pump()
            
        # Apply base filtering
        filtered_df = filter_dataframe(df, [])
        current_step += 1
        if progress_bar:
            progress_bar.update(current_step, total_steps)
            progress_bar.render()
        pygame.event.pump()
            
        # Filter by color identity
        filtered_df = filtered_df[filtered_df['colorIdentity'] == color_identity]
        logger.debug(f'Applied color identity filter: {color_identity}')
        current_step += 1
        if progress_bar:
            progress_bar.update(current_step, total_steps)
            progress_bar.render()
        pygame.event.pump()
            
        # Additional color-specific processing
        # Placeholder for future color-specific processing
        current_step += 1
        if progress_bar:
            progress_bar.update(current_step, total_steps)
            progress_bar.render()
        pygame.event.pump()

        logger.info(f'Completed color identity filtering for {color_identity}')
        return filtered_df
        
    except DataFrameProcessingError as e:
        raise ColorFilterError(
            "Color filtering failed",
            color_identity,
            str(e)
        ) from e
    except Exception as e:
        raise ColorFilterError(
            "Unexpected error during color filtering",
            color_identity,
            str(e)
        ) from e
def process_legendary_cards(df: pd.DataFrame, progress_bar: Optional['PyGameProgressBar'] = None) -> pd.DataFrame:
    """Process and filter legendary cards for commander eligibility with comprehensive validation.

    Args:
        df: DataFrame containing all cards
        progress_bar: Optional progress bar for tracking

    Returns:
        DataFrame containing only commander-eligible cards

    Raises:
        CommanderValidationError: If validation fails for legendary status, special cases, or set legality
        DataFrameProcessingError: If general processing fails
    """
    try:
        logger.info('Starting commander validation process')

        filtered_df = df.copy()
        # Initialize progress tracking
        total_steps = 3  # Three main processing steps
        current_step = 0

        # Step 1: Check legendary status
        try:
            mask = filtered_df['type'].str.contains('|'.join(LEGENDARY_OPTIONS), na=False)
            if not mask.any():
                raise CommanderValidationError(
                    "No legendary creatures found",
                    "legendary_check",
                    "DataFrame contains no cards matching legendary criteria"
                )
            filtered_df = filtered_df[mask].copy()
            logger.debug(f'Found {len(filtered_df)} legendary cards')
            
            current_step += 1
            if progress_bar:
                progress_bar.update(current_step, total_steps)
                progress_bar.render()
                pygame.event.pump()

        except Exception as e:
            raise CommanderValidationError(
                "Legendary status check failed",
                "legendary_check",
                str(e)
            ) from e

        # Step 2: Validate special cases
        try:
            special_cases = df['text'].str.contains('can be your commander', na=False)
            special_commanders = df[special_cases].copy()
            filtered_df = pd.concat([filtered_df, special_commanders]).drop_duplicates()
            logger.debug(f'Added {len(special_commanders)} special commander cards')
            
            current_step += 1
            if progress_bar:
                progress_bar.update(current_step, total_steps)
                progress_bar.render()
                pygame.event.pump()

        except Exception as e:
            raise CommanderValidationError(
                "Special case validation failed",
                "special_cases",
                str(e)
            ) from e

        # Step 3: Verify set legality
        try:
            initial_count = len(filtered_df)
            for set_code in NON_LEGAL_SETS:
                filtered_df = filtered_df[
                    ~filtered_df['printings'].str.contains(set_code, na=False)
                ]
            removed_count = initial_count - len(filtered_df)
            logger.debug(f'Removed {removed_count} cards from illegal sets')
            
            current_step += 1
            if progress_bar:
                progress_bar.update(current_step, total_steps)
                progress_bar.render()
                pygame.event.pump()

        except Exception as e:
            raise CommanderValidationError(
                "Set legality verification failed",
                "set_legality",
                str(e)
            ) from e
        logger.info(f'Commander validation complete. {len(filtered_df)} valid commanders found')
        return filtered_df

    except CommanderValidationError:
        raise
    except Exception as e:
        raise DataFrameProcessingError(
            "Failed to process legendary cards",
            "commander_processing",
            str(e)
        ) from e
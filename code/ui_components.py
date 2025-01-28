"""UI components module for MTG Python Deckbuilder."""

from __future__ import annotations

import pygame
from pygame import Surface, Rect
from pygame.font import Font
import time
from typing import Optional, Tuple, List, Callable

from settings import (
    UI_COLORS,
    UI_DIMENSIONS,
    INPUT_SETTINGS,
    DEFAULT_FONT_PATH,
    DEFAULT_FONT_SIZE
)

class UIComponent:
    """Base class for UI components."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize UI component.
        
        Args:
            x: X coordinate
            y: Y coordinate
            width: Component width
            height: Component height
        """
        self.rect = Rect(x, y, width, height)
        self.active = False
        self.hovered = False
        self._surface = Surface((width, height))
        self.font = Font(DEFAULT_FONT_PATH, DEFAULT_FONT_SIZE)
        
    def draw(self, surface: Surface) -> None:
        """Draw component on surface.
        
        Args:
            surface: Surface to draw on
        """
        surface.blit(self._surface, self.rect)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame event.
        
        Args:
            event: PyGame event to handle
            
        Returns:
            True if event was handled
        """
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        return False

class TextBox(UIComponent):
    """Text input component."""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int = UI_DIMENSIONS['textbox_width'],
        height: int = UI_DIMENSIONS['textbox_height'],
        placeholder: str = ''
    ):
        """Initialize text box.
        
        Args:
            x: X coordinate
            y: Y coordinate
            width: Box width
            height: Box height
            placeholder: Placeholder text
        """
        super().__init__(x, y, width, height)
        self.text = ''
        self.placeholder = placeholder
        self.cursor_pos = 0
        self.cursor_visible = True
        self.last_cursor_toggle = time.time()
        self.selection_start = None
        self.selection_end = None
        
    def _render(self) -> None:
        """Render text box surface."""
        # Background
        self._surface.fill(pygame.Color(UI_COLORS['textbox']))
        
        # Border
        border_color = (UI_COLORS['button'] if self.active 
                       else UI_COLORS['textbox_border'])
        pygame.draw.rect(
            self._surface,
            pygame.Color(border_color),
            (0, 0, self.rect.width, self.rect.height),
            UI_DIMENSIONS['border_width']
        )
        
        # Text
        if self.text:
            text_surface = self.font.render(
                self.text,
                True,
                pygame.Color(UI_COLORS['text'])
            )
        elif not self.active:
            text_surface = self.font.render(
                self.placeholder,
                True,
                pygame.Color(UI_COLORS['text_inactive'])
            )
        else:
            text_surface = self.font.render('', True, pygame.Color(UI_COLORS['text']))
            
        # Center text vertically
        text_y = (self.rect.height - text_surface.get_height()) // 2
        self._surface.blit(text_surface, (UI_DIMENSIONS['padding'], text_y))
        
        # Cursor
        if self.active and self.cursor_visible:
            cursor_x = (UI_DIMENSIONS['padding'] + 
                       self.font.size(self.text[:self.cursor_pos])[0])
            pygame.draw.line(
                self._surface,
                pygame.Color(UI_COLORS['text']),
                (cursor_x, text_y),
                (cursor_x, text_y + text_surface.get_height()),
                2
            )
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle text box events.
        
        Args:
            event: PyGame event to handle
            
        Returns:
            True if event was handled
        """
        super().handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                mouse_x = event.pos[0] - self.rect.x - UI_DIMENSIONS['padding']
                self.cursor_pos = len(self.text)
                for i, char in enumerate(self.text):
                    if self.font.size(self.text[:i])[0] > mouse_x:
                        self.cursor_pos = i - 1
                        break
            return True
            
        if not self.active:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.active = False
                return True
                
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = (self.text[:self.cursor_pos-1] + 
                               self.text[self.cursor_pos:])
                    self.cursor_pos -= 1
                return True
                
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                direction = 1 if event.key == pygame.K_RIGHT else -1
                self.cursor_pos = max(0, min(len(self.text),
                                           self.cursor_pos + direction))
                return True
                
            if event.unicode and len(self.text) < INPUT_SETTINGS['max_chars']:
                self.text = (self.text[:self.cursor_pos] + event.unicode + 
                           self.text[self.cursor_pos:])
                self.cursor_pos += 1
                return True
                
        return False
        
    def draw(self, surface: Surface) -> None:
        """Draw text box.
        
        Args:
            surface: Surface to draw on
        """
        if time.time() - self.last_cursor_toggle > INPUT_SETTINGS['cursor_blink_time'] / 1000:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = time.time()
            
        self._render()
        super().draw(surface)

class Button(UIComponent):
    """Clickable button component."""
    
    def __init__(
        self,
        x: int,
        y: int,
        text: str,
        width: int = UI_DIMENSIONS['button_width'],
        height: int = UI_DIMENSIONS['button_height'],
        on_click: Optional[Callable] = None,
        enabled: bool = True
    ):
        """Initialize button.
        
        Args:
            x: X coordinate
            y: Y coordinate
            text: Button text
            width: Button width
            height: Button height
            on_click: Click callback function
            enabled: Whether button is enabled
        """
        super().__init__(x, y, width, height)
        self.text = text
        self.on_click = on_click
        self.enabled = enabled
        
    def _render(self) -> None:
        """Render button surface."""
        if not self.enabled:
            color = UI_COLORS['button_disabled']
        elif self.hovered:
            color = UI_COLORS['button_hover']
        else:
            color = UI_COLORS['button']
            
        self._surface.fill(pygame.Color(color))
        
        # Border
        pygame.draw.rect(
            self._surface,
            pygame.Color(UI_COLORS['button_hover']),
            (0, 0, self.rect.width, self.rect.height),
            UI_DIMENSIONS['border_width'],
            UI_DIMENSIONS['border_radius']
        )
        
        # Text
        text_surface = self.font.render(
            self.text,
            True,
            pygame.Color(UI_COLORS['background'])
        )
        
        # Center text
        text_x = (self.rect.width - text_surface.get_width()) // 2
        text_y = (self.rect.height - text_surface.get_height()) // 2
        self._surface.blit(text_surface, (text_x, text_y))
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle button events.
        
        Args:
            event: PyGame event to handle
            
        Returns:
            True if event was handled
        """
        super().handle_event(event)
        
        if (event.type == pygame.MOUSEBUTTONDOWN and
            event.button == 1 and
            self.enabled and
            self.hovered and
            self.on_click):
            self.on_click()
            return True
            
        return False
        
    def draw(self, surface: Surface) -> None:
        """Draw button.
        
        Args:
            surface: Surface to draw on
        """
        self._render()
        super().draw(surface)

class Label(UIComponent):
    """Text label component."""
    
    def __init__(
        self,
        x: int,
        y: int,
        text: str,
        width: int = UI_DIMENSIONS['textbox_width'],
        height: int = UI_DIMENSIONS['textbox_height'],
        color: str = UI_COLORS['text']
    ):
        """Initialize label.
        
        Args:
            x: X coordinate
            y: Y coordinate
            text: Label text
            width: Label width
            height: Label height
            color: Text color
        """
        super().__init__(x, y, width, height)
        self.text = text
        self.color = color
        
    def _render(self) -> None:
        """Render label surface."""
        self._surface.fill(pygame.Color(UI_COLORS['background']))
        text_surface = self.font.render(
            self.text,
            True,
            pygame.Color(self.color)
        )
        
        # Center text
        text_x = (self.rect.width - text_surface.get_width()) // 2
        text_y = (self.rect.height - text_surface.get_height()) // 2
        self._surface.blit(text_surface, (text_x, text_y))
        
    def draw(self, surface: Surface) -> None:
        """Draw label.
        
        Args:
            surface: Surface to draw on
        """
        self._render()
        super().draw(surface)
import pygame
import pygame.freetype
from typing import List, Optional, Tuple, Dict, Any

class BuilderMenu:
    def __init__(self, screen: pygame.Surface, font_size: int = 32) -> None:
        """Initialize the builder menu.
        
        Args:
            screen: PyGame surface to render on
            font_size: Base font size for text
        """
        self.screen = screen
        self.font_size = font_size
        self.font = pygame.freetype.SysFont('Arial', font_size)
        self.input_text = ""
        self.active = False
        self.current_state = "commander_select"
        self.messages: List[str] = []
        self.choices: List[str] = []
        self.selected_choice = 0
        self.input_rect = pygame.Rect(100, 100, 400, 50)
        
    def display_message(self, message: str) -> None:
        """Display a message to the user.
        
        Args:
            message: Message to display
        """
        self.messages.append(message)
        if len(self.messages) > 5:  # Keep only last 5 messages
            self.messages.pop(0)
            
    def get_commander_input(self) -> str:
        """Get commander name input from user.
        
        Returns:
            Entered commander name
        """
        self.input_text = ""
        self.active = True
        
        while self.active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return ""
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.active = False
                        return self.input_text
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        self.input_text += event.unicode
                        
            self._render_input_screen()
            pygame.display.flip()
            
        return self.input_text
    
    def get_commander_choice(self, choices: List[str]) -> str:
        """Get commander selection from list of choices.
        
        Args:
            choices: List of commander options
            
        Returns:
            Selected commander name
        """
        self.choices = choices
        self.selected_choice = 0
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return ""
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_choice = (self.selected_choice - 1) % len(self.choices)
                    elif event.key == pygame.K_DOWN:
                        self.selected_choice = (self.selected_choice + 1) % len(self.choices)
                    elif event.key == pygame.K_RETURN:
                        return self.choices[self.selected_choice]
                        
            self._render_choice_screen()
            pygame.display.flip()
            
    def _render_input_screen(self) -> None:
        """Render the input screen with text field."""
        self.screen.fill((0, 0, 0))
        
        # Draw input box
        pygame.draw.rect(self.screen, (255, 255, 255), self.input_rect, 2)
        
        # Render input text
        text_surface, _ = self.font.render(self.input_text, (255, 255, 255))
        self.screen.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
        
        # Render messages
        message_y = self.input_rect.bottom + 20
        for message in self.messages:
            text_surface, _ = self.font.render(message, (255, 255, 255))
            self.screen.blit(text_surface, (100, message_y))
            message_y += 40
            
    def _render_choice_screen(self) -> None:
        """Render the choice selection screen."""
        self.screen.fill((0, 0, 0))
        
        # Render choices
        choice_y = 100
        for i, choice in enumerate(self.choices):
            color = (255, 255, 0) if i == self.selected_choice else (255, 255, 255)
            text_surface, _ = self.font.render(choice, color)
            self.screen.blit(text_surface, (100, choice_y))
            choice_y += 40
            
        # Render messages
        message_y = choice_y + 20
        for message in self.messages:
            text_surface, _ = self.font.render(message, (255, 255, 255))
            self.screen.blit(text_surface, (100, message_y))
            message_y += 40
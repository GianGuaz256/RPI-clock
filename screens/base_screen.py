"""
Base screen class for the Raspberry Pi Dashboard.
"""

import pygame
from typing import Tuple, Any
from utils.constants import (
    BLACK, WHITE, STATUS_COLORS, 
    FONT_LARGE, FONT_MEDIUM, FONT_SMALL
)


class BaseScreen:
    """Base class for all dashboard screens."""
    
    def __init__(self, app):
        """
        Initialize base screen.
        
        Args:
            app: Reference to main application instance
        """
        self.app = app
        self.name = self.__class__.__name__
        
        # Initialize fonts
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
        # Screen state
        self.is_active = False
        self.last_update = 0
        
    def activate(self) -> None:
        """Called when screen becomes active."""
        self.is_active = True
        print(f"Activated screen: {self.name}")
    
    def deactivate(self) -> None:
        """Called when screen becomes inactive."""
        self.is_active = False
    
    def update(self) -> None:
        """
        Update screen data and state.
        Override in subclasses for specific update logic.
        """
        pass
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw screen content.
        Must be implemented by subclasses.
        
        Args:
            screen: Pygame surface to draw on
        """
        screen.fill(BLACK)
        self.draw_title(screen, "Base Screen", 30)
    
    def draw_text(self, screen: pygame.Surface, text: str, pos: Tuple[int, int], 
                  font: pygame.font.Font, color: Tuple[int, int, int] = WHITE, 
                  center: bool = False) -> pygame.Rect:
        """
        Helper method to draw text on screen.
        
        Args:
            screen: Pygame surface to draw on
            text: Text to draw
            pos: Position (x, y)
            font: Font to use
            color: Text color (RGB tuple)
            center: Whether to center text at position
            
        Returns:
            Rectangle of drawn text
        """
        text_surface = font.render(str(text), True, color)
        
        if center:
            text_rect = text_surface.get_rect(center=pos)
            screen.blit(text_surface, text_rect)
            return text_rect
        else:
            screen.blit(text_surface, pos)
            return pygame.Rect(pos[0], pos[1], text_surface.get_width(), text_surface.get_height())
    
    def draw_title(self, screen: pygame.Surface, title: str, y_pos: int, size: int = None) -> None:
        """
        Draw screen title at top of screen.
        
        Args:
            screen: Pygame surface to draw on
            title: Title text
            y_pos: Y position for title
            size: Optional font size (uses medium font by default)
        """
        screen_width = screen.get_width()
        
        # Choose font based on size parameter
        if size is not None:
            font = pygame.font.Font(None, size)
        else:
            font = self.font_medium
            
        self.draw_text(screen, title, (screen_width // 2, y_pos), 
                      font, WHITE, center=True)
    
    def draw_status_indicator(self, screen: pygame.Surface, status: str, 
                            pos: Tuple[int, int], radius: int = 5) -> None:
        """
        Draw status indicator circle.
        
        Args:
            screen: Pygame surface to draw on
            status: Status string ('success', 'cached', 'error', etc.)
            pos: Position (x, y)
            radius: Circle radius
        """
        color = STATUS_COLORS.get(status, STATUS_COLORS['unknown'])
        pygame.draw.circle(screen, color, pos, radius)
    
    def draw_progress_bar(self, screen: pygame.Surface, pos: Tuple[int, int], 
                         size: Tuple[int, int], value: float, max_value: float = 100,
                         bg_color: Tuple[int, int, int] = (64, 64, 64),
                         fill_color: Tuple[int, int, int] = WHITE) -> None:
        """
        Draw a progress bar.
        
        Args:
            screen: Pygame surface to draw on
            pos: Position (x, y)
            size: Size (width, height)
            value: Current value
            max_value: Maximum value
            bg_color: Background color
            fill_color: Fill color
        """
        x, y = pos
        width, height = size
        
        # Draw background
        pygame.draw.rect(screen, bg_color, (x, y, width, height))
        
        # Draw fill
        fill_width = int((value / max_value) * width) if max_value > 0 else 0
        if fill_width > 0:
            pygame.draw.rect(screen, fill_color, (x, y, fill_width, height))
        
        # Draw border
        pygame.draw.rect(screen, WHITE, (x, y, width, height), 1)
    
    def draw_centered_content(self, screen: pygame.Surface, content_height: int) -> int:
        """
        Calculate Y position for vertically centered content.
        
        Args:
            screen: Pygame surface
            content_height: Height of content to center
            
        Returns:
            Y position for centered content
        """
        screen_height = screen.get_height()
        return (screen_height - content_height) // 2
    
    def get_wrapped_text(self, text: str, font: pygame.font.Font, 
                        max_width: int) -> list:
        """
        Wrap text to fit within specified width.
        
        Args:
            text: Text to wrap
            font: Font to use for measuring
            max_width: Maximum width in pixels
            
        Returns:
            List of text lines
        """
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Test if adding this word would exceed max width
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, add it anyway
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def draw_error_message(self, screen: pygame.Surface, error: str, 
                          y_pos: int = None) -> None:
        """
        Draw error message on screen.
        
        Args:
            screen: Pygame surface to draw on
            error: Error message
            y_pos: Y position (default: center of screen)
        """
        if y_pos is None:
            y_pos = screen.get_height() // 2
        
        screen_width = screen.get_width()
        
        # Draw error title
        self.draw_text(screen, "Error", (screen_width // 2, y_pos), 
                      self.font_medium, STATUS_COLORS['error'], center=True)
        
        # Draw error message (wrapped if needed)
        error_lines = self.get_wrapped_text(error, self.font_small, screen_width - 40)
        for i, line in enumerate(error_lines[:3]):  # Show max 3 lines
            self.draw_text(screen, line, (screen_width // 2, y_pos + 40 + i * 25), 
                          self.font_small, STATUS_COLORS['error'], center=True)
    
    def handle_touch(self, pos: Tuple[int, int]) -> bool:
        """
        Handle touch input on this screen.
        Override in subclasses for custom touch handling.
        
        Args:
            pos: Touch position (x, y)
            
        Returns:
            True if touch was handled, False otherwise
        """
        return False
    
    def get_screen_info(self) -> dict:
        """
        Get information about this screen.
        
        Returns:
            Dictionary with screen information
        """
        return {
            'name': self.name,
            'is_active': self.is_active,
            'last_update': self.last_update
        } 
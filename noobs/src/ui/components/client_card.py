import pygame
import math
from ..constants import PANEL_COLOR, HIGHLIGHT_COLOR, TEXT_COLOR, CLIENT_COLOR
from .button import Button
from .animation import Animation

class ClientCard:
    """Client card UI component for displaying client information"""
    def __init__(self, x, y, width, height, client, index, small_font=None, click_sound = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.client = client
        self.index = index
        self.small_font = small_font
        self.button = Button(
            x + width - 120, 
            y + height - 50, 
            100, 
            40, 
            "Select", 
            font=small_font,
            click_sound = click_sound
        )
        self.selected = False
        self.animation = Animation(0.5)
        self.y_offset = 0
    
    def update(self, mouse_pos):
        self.button.update(mouse_pos)
        
        if self.animation.running:
            progress = self.animation.update()
            self.y_offset = -20 * math.sin(progress * math.pi)
    
    def draw(self, surface):
        # Draw card with highlight if selected
        card_rect = pygame.Rect(
            self.rect.x,
            self.rect.y + self.y_offset,
            self.rect.width,
            self.rect.height
        )
        
        pygame.draw.rect(surface, PANEL_COLOR, card_rect, border_radius=10)
        if self.selected:
            pygame.draw.rect(surface, HIGHLIGHT_COLOR, card_rect, width=3, border_radius=10)
        
        # Draw client number
        num_surf = self.button.font.render(f"#{self.index}", True, CLIENT_COLOR)
        surface.blit(num_surf, (card_rect.x + 15, card_rect.y + 15))
        
        # Draw client description with word wrap - SHOW FULL TEXT
        desc = self.client['description']
        words = desc.split(' ')
        lines = []
        line = ""
        for word in words:
            test_line = line + word + " "
            # Check if the line would be too long
            if self.small_font.size(test_line)[0] < self.rect.width - 40:
                line = test_line
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)
        
        # Show as many lines as fit within the card height, adjusting card height if needed
        y_offset = 60
        bottom_margin = 60  # Space for the button
        max_text_height = self.rect.height - y_offset - bottom_margin
        line_height = 25
        
        # Draw all lines that fit
        for line in lines:
            text_surf = self.small_font.render(line, True, TEXT_COLOR)
            surface.blit(text_surf, (card_rect.x + 15, card_rect.y + y_offset))
            y_offset += line_height
            
            # If we're about to go past the button, adjust card height
            if y_offset > self.rect.height - bottom_margin and line != lines[-1]:
                # Draw remaining text indicator
                text_surf = self.small_font.render("See full description in selection.", True, HIGHLIGHT_COLOR)
                surface.blit(text_surf, (card_rect.x + 15, card_rect.y + y_offset))
                break
        
        # Draw button
        self.button.draw(surface)
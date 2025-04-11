import pygame
import math
from ..constants import BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR 
from .animation import Animation

class Button:
    """Button UI component with hover effects"""
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=BUTTON_TEXT_COLOR, font=None, border_radius=10, click_sound = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.border_radius = border_radius
        self.is_hovered = False
        self.animation = Animation(0.3)
        self.scale = 1.0
        self.click_sound = click_sound
    
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if self.is_hovered and not self.animation.running:
            self.animation.start()
        elif not self.is_hovered and not self.animation.running and self.scale > 1.0:
            self.animation.start()
        
        progress = self.animation.update()
        if self.is_hovered:
            self.scale = 1.0 + (0.1 * progress)
        else:
            self.scale = 1.1 - (0.1 * progress)
    
    def draw(self, surface):
        # Draw button with scale effect when hovered
        scaled_rect = pygame.Rect(
            self.rect.x - (self.rect.width * (self.scale - 1)) / 2,
            self.rect.y - (self.rect.height * (self.scale - 1)) / 2,
            self.rect.width * self.scale,
            self.rect.height * self.scale
        )
        
        color = self.color if not self.is_hovered else self.hover_color
        pygame.draw.rect(surface, color, scaled_rect, border_radius=self.border_radius)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        surface.blit(text_surface, text_rect)
    
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.click_sound:
                    self.click_sound.play()
                return True
        return False
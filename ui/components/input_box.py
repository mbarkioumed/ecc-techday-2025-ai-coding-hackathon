import pygame
from ..constants import BUTTON_COLOR, HIGHLIGHT_COLOR, TEXT_COLOR

class InputBox:
    """Input box for text entry"""
    def __init__(self, x, y, width, height, text='', font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_inactive = BUTTON_COLOR
        self.color_active = HIGHLIGHT_COLOR
        self.color = self.color_inactive
        self.text = text
        self.font = font
        self.txt_surface = font.render(text, True, TEXT_COLOR) if font else None
        self.active = False
        self.border_radius = 10
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable
                self.active = not self.active
            else:
                self.active = False
            # Change the current color
            self.color = self.color_active if self.active else self.color_inactive
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    # Only allow numbers and decimal point
                    if event.unicode.isdigit() or event.unicode == '.':
                        self.text += event.unicode
                # Re-render the text
                self.txt_surface = self.font.render(self.text, True, TEXT_COLOR)
        return None
    
    def update(self):
        # Resize the box if the text is too long
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width
    
    def draw(self, screen):
        # Draw the rect and text
        pygame.draw.rect(screen, self.color, self.rect, border_radius=self.border_radius)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2))
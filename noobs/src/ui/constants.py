"""
Constants for the Souk King game
Contains colors, screen dimensions, and other constants
"""
import pygame

# Screen dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# Colors
BACKGROUND = (233, 196, 106)
DARK_BACKGROUND = (42, 36, 56)
TEXT_COLOR = (38, 70, 83)
HIGHLIGHT_COLOR = (231, 111, 81)
BUTTON_COLOR = (244, 162, 97)
BUTTON_HOVER_COLOR = (231, 111, 81)
BUTTON_TEXT_COLOR = (42, 36, 56)
PLAYER_COLOR = (42, 157, 143)
AI_COLOR = (231, 111, 81)
EVENT_COLOR = (138, 177, 125)
CLIENT_COLOR = (42, 36, 56)
PANEL_COLOR = (247, 236, 195)

# Game states
class GameState:
    MENU = 0
    RULES = 1     # New state for rules screen
    BIDDING = 2
    BID_RESULT = 3
    EVENT = 4
    CLIENTS = 5
    RESULTS = 6
    GAME_OVER = 7

# Initialize pygame fonts
def init_fonts():
    pygame.font.init()
    
    return {
        'title_font': pygame.font.Font(None, 72),
        'heading_font': pygame.font.Font(None, 48),
        'regular_font': pygame.font.Font(None, 32),
        'small_font': pygame.font.Font(None, 24)
    }
def render_text_with_outline(font, text, text_color, outline_color, outline_width=2):
    """Render text with an outline for better visibility"""
    # First render the outline
    outline_surfaces = []
    
    # Create outline by rendering the text multiple times with offset positions
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
        for i in range(outline_width):
            x_offset = dx * (i + 1)
            y_offset = dy * (i + 1)
            outline_surf = font.render(text, True, outline_color)
            outline_surfaces.append((outline_surf, x_offset, y_offset))
    
    # Render the actual text
    text_surface = font.render(text, True, text_color)
    
    # Create a new surface to hold both the outline and the text
    width = text_surface.get_width() + outline_width * 2
    height = text_surface.get_height() + outline_width * 2
    final_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Blit all outline surfaces first
    for surf, x_offset, y_offset in outline_surfaces:
        final_surface.blit(surf, (outline_width + x_offset, outline_width + y_offset))
    
    # Then blit the text surface on top
    final_surface.blit(text_surface, (outline_width, outline_width))
    
    return final_surface
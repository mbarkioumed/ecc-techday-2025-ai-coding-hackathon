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
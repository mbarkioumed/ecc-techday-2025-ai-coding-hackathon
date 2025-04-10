import pygame
import sys
import math
import time
from pygame.locals import *
from ui.constants import SCREEN_WIDTH, SCREEN_HEIGHT, init_fonts, GameState
from game import SoukKingGame

def load_game_images():
    """Load game images or create placeholders if files don't exist"""
    images = {}
    
    try:
        # Logo image
        logo_img = pygame.image.load("images/Souk king color.png")
        # Get original dimensions and calculate new size that preserves aspect ratio
        orig_width, orig_height = logo_img.get_size()
        target_width = 400
        target_height = int(orig_height * (target_width / orig_width))
        images['logo_img'] = pygame.transform.smoothscale(logo_img, (target_width, target_height))
        
        # Player and AI images
        images['human_img'] = pygame.image.load("images/human.png")
        images['human_img'] = pygame.transform.scale(images['human_img'], (100, 100))
        images['robot_img'] = pygame.image.load("images/robot.png")
        images['robot_img'] = pygame.transform.scale(images['robot_img'], (100, 100))
    except pygame.error:
        # Create placeholder images if files don't exist
        from ui.constants import BUTTON_COLOR, TEXT_COLOR, PLAYER_COLOR, AI_COLOR
        
        images['logo_img'] = pygame.Surface((400, 200), pygame.SRCALPHA)
        images['logo_img'].fill((0, 0, 0, 0))
        pygame.draw.rect(images['logo_img'], BUTTON_COLOR, (0, 0, 400, 200), border_radius=20)
        title_font = pygame.font.Font(None, 72)
        logo_text = title_font.render("SOUK KING", True, TEXT_COLOR)
        images['logo_img'].blit(logo_text, (80, 70))
        
        images['human_img'] = pygame.Surface((100, 100), pygame.SRCALPHA)
        images['human_img'].fill((0, 0, 0, 0))
        pygame.draw.circle(images['human_img'], PLAYER_COLOR, (50, 50), 45)
        
        images['robot_img'] = pygame.Surface((100, 100), pygame.SRCALPHA)
        images['robot_img'].fill((0, 0, 0, 0))
        pygame.draw.circle(images['robot_img'], AI_COLOR, (50, 50), 45)
    
    return images

def main():
    """Main game function"""
    # Initialize pygame
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    
    # Create screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Souk King")
    
    # Initialize fonts and load images
    fonts = init_fonts()
    images = load_game_images()
    
    # Create game instance
    game = SoukKingGame(screen, fonts, images)
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    game.start_time = pygame.time.get_ticks()
    game.showed_view = False
    
    while running:
        dt = clock.tick(60) / 1000.0  # Time since last frame in seconds
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle events
        for event in pygame.event.get():
            if not game.handle_event(event):
                running = False
        
        # Update game
        game.update(dt, mouse_pos)
        
        # Draw game
        game.draw()
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
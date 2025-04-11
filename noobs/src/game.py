import random
import time
import ollama
import pygame
import math
from pygame.locals import *
from data import products, clients, events
from functions import summarize_ai_memory, calculate_number_of_clients
from ui.constants import *
from ui.components.animation import Animation
from ui.components.button import Button
from ui.components.input_box import InputBox
from ui.components.client_card import ClientCard

class SoukKingGame:
    def __init__(self, screen, fonts, images):
        # Store screen and font references
        self.screen = screen
        self.fonts = fonts
        self.images = images
        
        # Game variables
        self.user_money = 300
        self.ai_money = 300
        self.event_weights = [0.15, 0.55, 0.15, 0.15]
        self.ai_memory = []
        self.start_time = 0
        self.showed_view = False
        self.selected_products = random.sample(products, 5)
        self.current_round = 0
        self.current_product = None
        self.selected_clients = []
        self.selected_event = None
        self.game_state = GameState.MENU
        self.bid_result = None
        self.user_price = 0
        self.ai_price = 0
        self.chosen_client = None
        self.transition_animation = Animation(0.1)
        self.money_animation = Animation(1.0, sound = pygame.mixer.Sound("noobs/src/ui/sounds/money.wav"))
        self.old_user_money = self.user_money
        self.old_ai_money = self.ai_money
        self.given_price = 0
        self.client_cards = []
        self.winner = None
        self.round_winners = [None, None, None, None, None]
        self.button_click_sound = pygame.mixer.Sound("noobs/src/ui/sounds/click.wav")
        self.money_sound = pygame.mixer.Sound("noobs/src/ui/sounds/money.wav")
        self.winning_sound = pygame.mixer.Sound("noobs/src/ui/sounds/goodresult.mp3")
        self.loosing_sound = pygame.mixer.Sound("noobs/src/ui/sounds/fail.mp3")
        self.winning_sound.set_volume(0.7)
        self.loosing_sound.set_volume(0.7)
        
        # Rules text
        self.rules = [
            "Welcome to Souk King!",
            "You are a merchant in a marketplace.",
            "Your goal is to make more money than the AI merchant.",
            "",
            "Game Rules:",
            "  1. Each round, you bid on a product against the AI.",
            "  2. The highest bidder gets to sell the product that day.",
            "  3. Each day has special events that affect your profits.",
            "  4. Choose clients wisely - each offers a different price!",
            "  5. After 5 rounds, whoever has the most money wins.",
            "",
            "Tips:",
            "  • Bidding too high reduces potential profit and attracts fewer clients.",
            "  • Watch out for 'Charity Days' when you donate 20% of your money.",
            "  • On 'High Demand Days' your selling price doubles!",
            "  • On 'Low Demand Days' your selling price is halved.",
        ]
        
        # UI elements
        self.create_ui()
    
    def create_ui(self):
        # Menu buttons
        self.start_button = Button(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 2 + 50,
            200,
            60,
            "Start Game",
            font=self.fonts['heading_font'],
            click_sound = self.button_click_sound
        )
        
        # Rules screen button
        self.understood_button = Button(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT - 100,
            200,
            60,
            "Understood!",
            font=self.fonts['heading_font'],
            click_sound = self.button_click_sound
        )
        
        # Bidding UI
        self.bid_input = InputBox(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 2,
            200,
            50,
            text='',
            font=self.fonts['regular_font']
        )
        
        self.place_bid_button = Button(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 2 + 80,
            200,
            60,
            "Place Bid",
            font=self.fonts['heading_font'],
            click_sound = self.button_click_sound
        )
        
        # Event/Results UI
        self.continue_button = Button(
            SCREEN_WIDTH // 1.3,
            SCREEN_HEIGHT - 100,
            200,
            60,
            "Continue",
            font=self.fonts['heading_font'],
            click_sound = self.button_click_sound
        )
        
        # Game over UI
        self.play_again_button = Button(
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT - 150,
            300,
            60,
            "Play Again",
            font=self.fonts['heading_font'],
            click_sound = self.button_click_sound
        )
    
    def reset_game(self):
        self.user_money = 300
        self.ai_money = 300
        self.ai_memory = []
        self.selected_products = random.sample(products, 5)
        self.current_round = 0
        self.game_state = GameState.MENU
        self.round_winners = [None, None, None, None, None]
    
    def next_round(self):
        # Advance to next round
        self.current_round += 1
        
        if self.current_round > len(self.selected_products):
            self.transition_to_state(GameState.GAME_OVER)
            return
        
        # Set current product
        self.current_product = self.selected_products[self.current_round - 1]
        
        if self.user_money < self.current_product['base_price'] and self.ai_money < self.current_product['base_price']:
            # Find another product that at least one player can afford
            affordable_product_found = False
            
            # Try the remaining products
            for i in range(self.current_round, len(self.selected_products)):
                potential_product = self.selected_products[i]
                if self.user_money >= potential_product['base_price'] or self.ai_money >= potential_product['base_price']:
                    # Swap the current product with this affordable one
                    self.selected_products[self.current_round - 1], self.selected_products[i] = self.selected_products[i], self.selected_products[self.current_round - 1]
                    self.current_product = self.selected_products[self.current_round - 1]
                    affordable_product_found = True
                    break
                    
            if not affordable_product_found:
                # If no affordable products remain, end the game
                self.transition_to_state(GameState.GAME_OVER)
                return
        
        # Reset bid input
        self.bid_input.text = str(self.current_product['base_price'])
        self.bid_input.txt_surface = self.bid_input.font.render(self.bid_input.text, True, TEXT_COLOR)
        
        # Reset other variables
        self.bid_result = None
        self.user_price = 0
        self.ai_price = 0
        self.chosen_client = None
        self.selected_clients = []
        self.client_cards = []
        
        if hasattr(self, 'ai_sale_animation_started'):
            delattr(self, 'ai_sale_animation_started')
        
        # Start bidding phase
        self.transition_to_state(GameState.BIDDING)
    
    def transition_to_state(self, new_state):
        #self.transition_animation.start()
        self.game_state = new_state
        
        # If transitioning from menu to game, restore original window size
        if self.game_state != GameState.MENU:
            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def place_bid(self):
        try:
            # Special case: If player can't afford base price, auto-bid 0
            if self.user_money < self.current_product['base_price']:
                self.user_price = 0
                self.get_ai_bid()
                return True
            
            user_price = float(self.bid_input.text)
            
            # Validate bid
            if user_price < self.current_product['base_price']:
                return False
            
            if user_price > self.user_money:
                return False
            
            self.user_price = user_price
            self.get_ai_bid()
            return True
            
        except ValueError:
            return False
    
    def get_ai_bid(self):
        # If AI doesn't have enough money
        if self.ai_money < self.current_product['base_price']:
            self.ai_price = -1
            self.process_bid_result()
            return
        
        # Get AI bid using ollama
        memory_summary = summarize_ai_memory(self.ai_memory)
        
        messages = [
            {"role": "system", "content": f"""
            You are an AI vendor in a negotiation game. Your goal is to make more money than the player.
            {memory_summary}

            Current situation:
            - You have {self.ai_money}$
            - The player has {self.user_money}$
            - You're bidding on: {self.current_product['name']} (Base Price: {self.current_product['base_price']}$)

            🧠 Strategy:
            - High bids help you win the product but increase risk.
            - Some days cause you to lose money (like 'Charity Day'or 'Low demand day").
            - If you overspend, you may not profit.
            - Bidding high may help you win, but it will likely result in fewer clients, reducing your potential profits.

            - You want to win by the final round.

            Respond with a **single numeric value** — your bid.
            """},
            {"role": "user", "content": f"What is your bid for {self.current_product['name']}? (Base Price: ${self.current_product['base_price']}) — You currently have {self.ai_money}$. Give just a number, no sentence no characters just the number!"}
        ]

        try:
            ollama_response = ollama.chat(model="llama3.2:latest", messages=messages)
            ollama_price = float(ollama_response['message']['content'].strip())
            
            # Validate AI bid
            if ollama_price < self.current_product['base_price'] or ollama_price > self.ai_money:
                # Try again if bid is invalid
                ollama_response = ollama.chat(model="llama3.2:latest", messages=messages)
                ollama_price = float(ollama_response['message']['content'].strip())
                
                # Use base price if still invalid
                if ollama_price < self.current_product['base_price'] or ollama_price > self.ai_money:
                    ollama_price = min(self.current_product['base_price'] * 1.2, self.ai_money)
            
            # Check for tie
            if self.user_price == ollama_price:
                ollama_price = min(ollama_price * 1.05, self.ai_money)  # Adjust AI bid slightly
            
            self.ai_price = ollama_price
            self.process_bid_result()
                
        except Exception as e:
            print(f"Error getting AI bid: {e}")
            self.ai_price = self.current_product['base_price']
            self.process_bid_result()
    
    def process_bid_result(self):
        # Determine winner
        if self.user_price > self.ai_price:
            self.bid_result = "player"
            self.round_winners[self.current_round - 1] = "player"
            self.old_user_money = self.user_money
            self.user_money -= self.user_price
            self.money_animation.start()
            self.handle_player_turn()
        else:
            self.bid_result = "ai"
            self.round_winners[self.current_round - 1] = "ai"
            self.old_ai_money = self.ai_money
            self.ai_money -= self.ai_price
            self.money_animation.start()  
            self.handle_ai_turn()
        
        self.transition_to_state(GameState.EVENT)
    
    def handle_player_turn(self):
        # Generate event
        self.selected_event = random.choices(events, weights=self.event_weights, k=1)[0]
        
        # Calculate price based on event
        today_price = self.user_price
        if self.selected_event['name'] == "High demand day":
            today_price *= 2
        elif self.selected_event['name'] == "Low demand day":
            today_price /= 2
        
        # Generate clients
        self.selected_clients = random.sample(clients, calculate_number_of_clients(self.current_product["base_price"], self.user_price))
        
        # Create client cards
        self.create_client_cards()
    
    def handle_ai_turn(self):
        # Generate event
        self.selected_event = random.choices(events, weights=self.event_weights, k=1)[0]
        
        # Calculate price based on event
        today_price = self.ai_price
        if self.selected_event['name'] == "High demand day":
            today_price *= 2
        elif self.selected_event['name'] == "Low demand day":
            today_price /= 2
        
        # Generate clients
        self.selected_clients = random.sample(clients, calculate_number_of_clients(self.current_product["base_price"], self.ai_price))
        
        # AI chooses client
        if len(self.selected_clients) == 1:
            self.chosen_client = self.selected_clients[0]
        else:
            try:
                ollama_responseChoice = ollama.chat(
                    model="llama3.2:latest",
                    messages=[
                        {"role": "system", "content": "You are an AI vendor analyzing clients to find who will offer the highest price."
                        " Read the descriptions and predict who'll give the highest price.Do NOT assume everyone pays equally — your goal is to **rank them based on likelihood to pay more**. Return only the number 1, 2 or 3."},
                        {"role": "user", "content": (
                        "Read the client descriptions below and choose the ONE most likely to offer the highest price.\n"
                        "⚠️ Respond ONLY with the number of the client you have chosen. DO NOT write anything else.\n\n" +
                        "\n".join([f"Client {i}: {client['description']}" for i, client in enumerate(self.selected_clients, 1)])
                        )}
                    ]
                )
                ollama_prediction = ollama_responseChoice['message']['content'].strip()
                
                # Validate the prediction
                try:
                    pred_num = int(ollama_prediction)
                    if 1 <= pred_num <= len(self.selected_clients):
                        self.chosen_client = self.selected_clients[pred_num - 1]
                    else:
                        self.chosen_client = self.selected_clients[0]
                except ValueError:
                    self.chosen_client = self.selected_clients[0]
            except Exception:
                self.chosen_client = self.selected_clients[0]
        # Calculate sale price
        today_price = self.ai_price
        if self.selected_event['name'] == "High demand day":
            today_price *= 2
        elif self.selected_event['name'] == "Low demand day":
            today_price /= 2
        
        # Calculate the price but don't add it yet
        self.given_price = self.chosen_client['offer_percentage'] * today_price
        
        # Store the final amount AI will have, but don't apply it yet
        self.final_ai_money = self.ai_money + self.given_price
        if self.selected_event['name'] == "Charity day":
            self.final_ai_money -= self.final_ai_money * 0.2
        
        # Don't update self.ai_money yet - keep it at the post-bid value
        
        # Update AI memory
        self.ai_memory.append({
            "round": self.current_round,
            "event": self.selected_event['name'],
            "ai": {
                "bought_for": self.ai_price,
                "sold_for": self.given_price,
                "profit": self.given_price - self.ai_price
            },
            "player": {
                "bought_for": None,
                "sold_for": None,
                "profit": 0,
                "note": "Lost to AI"
            }
        })
        
        # Create client cards for display
        self.create_client_cards()
    
    def create_client_cards(self):
        self.client_cards = []
        card_width = 320  # Increased from 300
        card_height = 280  # Increased from 200
        
        if len(self.selected_clients) == 1:
            # Single client centered
            x = (SCREEN_WIDTH - card_width) // 2
            y = 320  # Moved up from 400
            card = ClientCard(x, y, card_width, card_height, self.selected_clients[0], 1, small_font=self.fonts['small_font'], click_sound = self.button_click_sound)
            self.client_cards.append(card)
        elif len(self.selected_clients) == 2:
            # Two clients side by side
            spacing = 40
            total_width = (card_width * 2) + spacing
            start_x = (SCREEN_WIDTH - total_width) // 2
            y = 320  # Moved up from 400
            
            for i, client in enumerate(self.selected_clients):
                x = start_x + (i * (card_width + spacing))
                card = ClientCard(x, y, card_width, card_height, client, i+1, small_font=self.fonts['small_font'], click_sound = self.button_click_sound)
                self.client_cards.append(card)
        else:
            # Three clients in a horizontal row
            spacing = 20
            total_width = (card_width * 3) + (spacing * 2)
            start_x = (SCREEN_WIDTH - total_width) // 2
            y = 320  # Moved up from 400
            
            for i, client in enumerate(self.selected_clients):
                x = start_x + (i * (card_width + spacing))
                card = ClientCard(x, y, card_width, card_height, client, i+1, small_font=self.fonts['small_font'])
                self.client_cards.append(card)
    
    def select_client(self, client_card):
        self.chosen_client = client_card.client
        
        # Calculate sale price
        today_price = self.user_price
        if self.selected_event['name'] == "High demand day":
            today_price *= 2
        elif self.selected_event['name'] == "Low demand day":
            today_price /= 2
        
        self.given_price = self.chosen_client['offer_percentage'] * today_price
        self.old_user_money = self.user_money
        self.user_money += self.given_price
        
        if self.selected_event['name'] == "Charity day":
            self.user_money -= self.user_money * 0.2
        
        # Update AI memory
        self.ai_memory.append({
            "round": self.current_round,
            "event": self.selected_event['name'],
            "ai": {
                "bought_for": None,
                "sold_for": None,
                "profit": 0,
                "note": "Lost to player"
            },
            "player": {
                "bought_for": self.user_price,
                "sold_for": self.given_price,
                "profit": self.given_price - self.user_price
            }
        })
        
        self.money_animation.start()
        self.transition_to_state(GameState.RESULTS)
    
    def draw_menu(self):
        # Draw background - use the same background as rules screen
        self.screen.fill(BACKGROUND)
        self.screen.blit(self.images['background_img'], (0, 0))
        
        # Draw title
        title = render_text_with_outline(
            self.fonts['title_font'],
            "SOUK KING", 
            TEXT_COLOR,
            (255, 255, 255),  # white outline
            2  # outline thickness
        )
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)
        
        # Draw rules text - same as rules screen
        y_offset = 120
        line_height = 30
        
        for rule in self.rules:
            if rule == "":  # Empty line for spacing
                y_offset += line_height
                continue
                
            # Use heading font for section titles
            if rule in ["Game Rules:", "Tips:"]:
                text = render_text_with_outline(
                    self.fonts['heading_font'],
                    rule, 
                    HIGHLIGHT_COLOR,
                    (255, 255, 255),  # white outline
                    1  # outline thickness
                )
            else:
                text = render_text_with_outline(
                    self.fonts['regular_font'],
                    rule, 
                    TEXT_COLOR,
                    (255, 255, 255),  # white outline
                    1  # outline thickness
                )
                
            text_rect = text.get_rect(midleft=(SCREEN_WIDTH // 12, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += line_height
        
        # Draw start button at the bottom - same position as the understood button
        self.start_button.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        self.start_button.draw(self.screen)
        
    def draw_bidding(self):
        # Draw background
        self.screen.fill(BACKGROUND)
        self.screen.blit(self.images['background_img'], (0, 0))
        
        # Draw round info
        round_text = render_text_with_outline(
            self.fonts['heading_font'],
            f"Round {self.current_round} of 5", 
            TEXT_COLOR,
            (255, 255, 255),  # white outline
            2  # outline thickness
        )
        self.screen.blit(round_text, (20, 20))
        
        # Draw money with outlines
        player_money = render_text_with_outline(
            self.fonts['regular_font'],
            f"Your Money: ${self.user_money:.2f}", 
            PLAYER_COLOR,
            (255, 255, 255),  # white outline
            2  # outline thickness
        )
        self.screen.blit(player_money, (20, 70))
        
        ai_money = render_text_with_outline(
            self.fonts['regular_font'],
            f"AI Money: ${self.ai_money:.2f}", 
            AI_COLOR,
            (255, 255, 255),  # white outline
            2  # outline thickness
        )
        self.screen.blit(ai_money, (SCREEN_WIDTH - 250, 70))
        
        # Draw product panel
        panel_rect = pygame.Rect(50, 120, SCREEN_WIDTH - 100, 180)
        pygame.draw.rect(self.screen, PANEL_COLOR, panel_rect, border_radius=10)
        
        # Draw product info
        product_name = self.fonts['heading_font'].render(self.current_product['name'], True, TEXT_COLOR)
        self.screen.blit(product_name, (panel_rect.x + 20, panel_rect.y + 20))
        
        product_price = self.fonts['regular_font'].render(f"Base Price: ${self.current_product['base_price']}", True, TEXT_COLOR)
        self.screen.blit(product_price, (panel_rect.x + 20, panel_rect.y + 70))
        
        # Draw product description with word wrap
        desc = self.current_product['description']
        words = desc.split(' ')
        lines = []
        line = ""
        for word in words:
            test_line = line + word + " "
            if self.fonts['small_font'].size(test_line)[0] < panel_rect.width - 40:
                line = test_line
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)
        
        y_offset = 110
        for line in lines:
            text_surf = self.fonts['small_font'].render(line, True, TEXT_COLOR)
            self.screen.blit(text_surf, (panel_rect.x + 20, panel_rect.y + y_offset))
            y_offset += 25
        
        # Draw bidding panel
        bid_text = render_text_with_outline(
            self.fonts['heading_font'],
            "Place Your Bid", 
            TEXT_COLOR,
            (255, 255, 255),  # white outline
            2  # outline thickness
        )
        bid_rect = bid_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(bid_text, bid_rect)
        
        # Draw input box and button
        self.bid_input.draw(self.screen)
        self.place_bid_button.draw(self.screen)
    
    def draw_event(self):
        # Draw background
        self.screen.fill(BACKGROUND)
        self.screen.blit(self.images['background_img'], (0, 0))
        
        # Draw round info
        round_text = render_text_with_outline(
            self.fonts['heading_font'],
            f"Round {self.current_round} of 5", 
            TEXT_COLOR,
            (255, 255, 255),  # white outline
            2  # outline thickness
        )
        self.screen.blit(round_text, (20, 20))
        
        # Money display logic with animations - add outlines
        if hasattr(self, 'ai_sale_animation') and self.ai_sale_animation.running:
            # If AI sale animation is running, use that for AI money display
            progress = self.ai_sale_animation.update()
            display_ai_money = self.old_ai_money + (progress * (self.final_ai_money - self.old_ai_money))
            ai_money = render_text_with_outline(
                self.fonts['regular_font'],
                f"AI Money: ${display_ai_money:.2f}", 
                AI_COLOR,
                (255, 255, 255),  # white outline
                2  # outline thickness
            )
            player_money = render_text_with_outline(
                self.fonts['regular_font'],
                f"Your Money: ${self.user_money:.2f}", 
                PLAYER_COLOR,
                (255, 255, 255),  # white outline
                2  # outline thickness
            )
            
            # When sale animation is complete, update the actual AI money
            if not self.ai_sale_animation.running:
                self.ai_money = self.final_ai_money
        elif self.money_animation.running:
            # Initial bid animation
            progress = self.money_animation.update()
            if self.bid_result == "player":
                display_money = self.old_user_money - (progress * (self.old_user_money - self.user_money))
                player_money = render_text_with_outline(
                    self.fonts['regular_font'],
                    f"Your Money: ${display_money:.2f}", 
                    PLAYER_COLOR,
                    (255, 255, 255),  # white outline
                    2  # outline thickness
                )
            else:
                player_money = render_text_with_outline(
                    self.fonts['regular_font'],
                    f"Your Money: ${self.user_money:.2f}", 
                    PLAYER_COLOR,
                    (255, 255, 255),  # white outline
                    2  # outline thickness
                )
            
            if self.bid_result == "ai":
                display_ai_money = self.old_ai_money - (progress * (self.old_ai_money - self.ai_money))
                ai_money = render_text_with_outline(
                    self.fonts['regular_font'],
                    f"AI Money: ${display_ai_money:.2f}", 
                    AI_COLOR,
                    (255, 255, 255),  # white outline
                    2  # outline thickness
                )
            else:
                ai_money = render_text_with_outline(
                    self.fonts['regular_font'],
                    f"AI Money: ${self.ai_money:.2f}", 
                    AI_COLOR,
                    (255, 255, 255),  # white outline
                    2  # outline thickness
                )
        else:
            player_money = render_text_with_outline(
                self.fonts['regular_font'],
                f"Your Money: ${self.user_money:.2f}", 
                PLAYER_COLOR,
                (255, 255, 255),  # white outline
                2  # outline thickness
            )
            ai_money = render_text_with_outline(
                self.fonts['regular_font'],
                f"AI Money: ${self.ai_money:.2f}", 
                AI_COLOR,
                (255, 255, 255),  # white outline
                2  # outline thickness
            )
        
        # Always display money at the top
        self.screen.blit(player_money, (20, 70))
        self.screen.blit(ai_money, (SCREEN_WIDTH - 250, 70))
        
        if pygame.time.get_ticks() - self.start_time < 2000:
            # Display user and AI logos
            user_logo_rect = self.images['human_img'].get_rect(center=(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
            ai_logo_rect = self.images['robot_img'].get_rect(center=(3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
            self.screen.blit(self.images['human_img'], user_logo_rect)
            self.screen.blit(self.images['robot_img'], ai_logo_rect)
            
            # Display user bid
            user_bid_text = render_text_with_outline(
                self.fonts['title_font'],
                f"Your Bid: ${self.user_price:.2f}", 
                PLAYER_COLOR,
                (255, 255, 255),  # white outline
                2  # outline thickness
            )
            user_bid_rect = user_bid_text.get_rect(center=(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 100))
            self.screen.blit(user_bid_text, user_bid_rect)
            
            # Display AI bid
            ai_bid_text = render_text_with_outline(
                self.fonts['title_font'],
                f"AI Bid: ${self.ai_price:.2f}", 
                AI_COLOR,
                (255, 255, 255),  # white outline
                2  # outline thickness
            )
            ai_bid_rect = ai_bid_text.get_rect(center=(3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 100))
            self.screen.blit(ai_bid_text, ai_bid_rect)
            
            # Display who won the item
            if self.bid_result == "player":
                winner_text = render_text_with_outline(
                    self.fonts['title_font'],
                    "You won the item!", 
                    PLAYER_COLOR,
                    (255, 255, 255),  # white outline
                    2  # outline thickness
                )
            else:
                winner_text = render_text_with_outline(
                    self.fonts['title_font'],
                    "AI won the item!", 
                    AI_COLOR,
                    (255, 255, 255),  # white outline
                    2  # outline thickness
                )
            winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(winner_text, winner_rect)
        
        if pygame.time.get_ticks() - self.start_time >= 2000:
            # Draw bid result left-aligned instead of centered - MOVED DOWN BY 10 PIXELS
            if self.bid_result == "player":
                result_text = render_text_with_outline(
                    self.fonts['heading_font'],
                    f"You bought the {self.current_product['name']} for ${self.user_price:.2f}", 
                    PLAYER_COLOR,
                    (255, 255, 255),  # white outline
                    2  # outline thickness
                )
                winner_img = self.images['human_img']
            else:
                result_text = render_text_with_outline(
                    self.fonts['heading_font'],
                    f"AI bought the {self.current_product['name']} for ${self.ai_price:.2f}", 
                    AI_COLOR,
                    (255, 255, 255),  # white outline
                    2  # outline thickness
                )
                winner_img = self.images['robot_img']

            # Position image and text at the left side of screen - MOVED DOWN FROM 130 TO 140
            icon_rect = winner_img.get_rect(midleft=(50, 140))
            result_rect = result_text.get_rect(midleft=(icon_rect.right + 10, 140))

            # Draw them side by side
            self.screen.blit(winner_img, icon_rect)
            self.screen.blit(result_text, result_rect)
            
            # Determine event panel color based on the day type
            if self.selected_event['name'] == "High demand day":
                event_color = PLAYER_COLOR  # Match the Money text color
            elif self.selected_event['name'] in ["Charity day", "Low demand day"]:
                event_color = (255, 0, 0)  # Red
            else:
                event_color = (173, 216, 230)  # Baby blue

            # Draw event panel with background - REDUCED WIDTH from SCREEN_WIDTH - 100 to 400
            event_width = 600  # Narrower width
            event_panel = pygame.Rect((SCREEN_WIDTH - event_width) // 2, 180, event_width, 80)
            pygame.draw.rect(self.screen, event_color, event_panel, border_radius=10)

            # Draw event info on the panel - name at the top
            event_text = self.fonts['regular_font'].render(f"Today is {self.selected_event['name']}", True, TEXT_COLOR)
            event_rect = event_text.get_rect(center=(event_panel.centerx, event_panel.y + 20))  # Position near top
            self.screen.blit(event_text, event_rect)

            # Draw event description inside the panel
            event_desc = self.fonts['small_font'].render(self.selected_event['description'], True, TEXT_COLOR)
            event_desc_rect = event_desc.get_rect(center=(event_panel.centerx, event_panel.y + 55))  # Position below name
            self.screen.blit(event_desc, event_desc_rect)

            # Draw client selection instructions after the event panel
            if self.bid_result == "player":
                # For player's turn
                instruction = render_text_with_outline(
                    self.fonts['heading_font'],
                    "Choose a client to sell to:", 
                    TEXT_COLOR,
                    (255, 255, 255),  # white outline
                    2  # outline thickness
                )
                instruction_rect = instruction.get_rect(topleft=(50, event_panel.bottom + 20))  # Position after panel
                self.screen.blit(instruction, instruction_rect)
                
                # Draw client cards - no need to draw event description again
                for card in self.client_cards:
                    card.draw(self.screen)
            else:
                # If AI's turn, show AI's choice
                if self.chosen_client:
                    if pygame.time.get_ticks() - self.start_time < 4000:
                        # Draw client cards with AI's choice highlighted
                        for i, card in enumerate(self.client_cards):
                            card.draw(self.screen)
                    elif pygame.time.get_ticks() - self.start_time < 5000:
                        # Transition phase: gradually highlight the AI's chosen client and fade out others
                        fade_progress = (pygame.time.get_ticks() - self.start_time - 4000) / 800  # 0 to 1 over 2 seconds
                        
                        # Draw all client cards
                        for card in self.client_cards:
                            # Mark the chosen card as selected
                            card.selected = (card.client == self.chosen_client)
                            # Draw the card
                            card.draw(self.screen)
                        
                        # Create fade effect for non-selected cards
                        for card in self.client_cards:
                            if card.client != self.chosen_client:
                                # Create a fading overlay on non-selected cards
                                card_rect = pygame.Rect(
                                    card.rect.x,
                                    card.rect.y + card.y_offset,
                                    card.rect.width,
                                    card.rect.height
                                )
                                overlay = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
                                overlay_alpha = int(180 * fade_progress)  # Gradually increase opacity to 70%
                                overlay.fill((BACKGROUND[0], BACKGROUND[1], BACKGROUND[2], overlay_alpha))
                                self.screen.blit(overlay, card_rect)
                    elif pygame.time.get_ticks() - self.start_time >= 5000:
                        # Now draw "AI chose this client" text AFTER the event section
                        instruction = render_text_with_outline(
                            self.fonts['heading_font'],
                            "AI chose this client:", 
                            TEXT_COLOR,
                            (255, 255, 255), #outline
                            2
                            )
                        instruction_rect = instruction.get_rect(topleft=(50, event_panel.bottom + 20))  # Position after panel
                        self.screen.blit(instruction, instruction_rect)
                        for i, card in enumerate(self.client_cards):
                            if self.chosen_client == card.client:
                                card.selected = True
                                card.draw(self.screen)
                    # Show the sale price after a short delay
                    if pygame.time.get_ticks() - self.start_time >= 5000:
                        if self.bid_result == "ai" and self.chosen_client:
                            sale_text = render_text_with_outline(
                                self.fonts['heading_font'],
                                f"Item Sold for: ${self.given_price:.2f}", 
                                AI_COLOR,
                                (255, 255, 255),  # white outline
                                2  # outline thickness
                            )
                            sale_rect = sale_text.get_rect(center=(SCREEN_WIDTH // 2, 700))
                            self.screen.blit(sale_text, sale_rect)
                                # Draw continue button
                            if pygame.time.get_ticks() - self.start_time >= 5100:    
                                self.continue_button.draw(self.screen)
                        
                        # Start the money animation for adding the sale price to AI money
                        if hasattr(self, 'final_ai_money') and not hasattr(self, 'ai_sale_animation_started'):
                            self.old_ai_money = self.ai_money  # Current money (after bid subtracted)
                            self.ai_sale_animation = Animation(1.0, sound = self.money_sound)
                            self.ai_sale_animation.start()
                            self.ai_sale_animation_started = True
                else:
                    # AI is still choosing
                    instruction = self.fonts['heading_font'].render("AI is choosing a client...", True, TEXT_COLOR)
                    instruction_rect = instruction.get_rect(topleft=(50, event_panel.bottom + 20))  # Position after panel
                    self.screen.blit(instruction, instruction_rect)
                    
                    # Draw client cards
                    for card in self.client_cards:
                        card.draw(self.screen)
    
    def draw_results(self):
        # Draw background
        self.screen.fill(BACKGROUND)
        self.screen.blit(self.images['background_img'], (0, 0))
        
        # Draw round and money info
        round_text = render_text_with_outline(
            self.fonts['heading_font'],
            f"Round {self.current_round} of 5", 
            TEXT_COLOR,
            (255, 255, 255),  # white outline
            2  # outline thickness
        )
        self.screen.blit(round_text, (20, 20))
        
        # Animate money changes with outline
        if self.money_animation.running:
            progress = self.money_animation.update()
            display_money = self.old_user_money + (progress * (self.user_money - self.old_user_money))
            player_money = render_text_with_outline(
                self.fonts['regular_font'],
                f"Your Money: ${display_money:.2f}", 
                PLAYER_COLOR,
                (255, 255, 255),  # white outline
                2  # outline thickness
            )
        else:
            player_money = render_text_with_outline(
                self.fonts['regular_font'],
                f"Your Money: ${self.user_money:.2f}", 
                PLAYER_COLOR,
                (255, 255, 255),  # white outline
                2  # outline thickness
            )
        
        ai_money = render_text_with_outline(
            self.fonts['regular_font'],
            f"AI Money: ${self.ai_money:.2f}", 
            AI_COLOR,
            (255, 255, 255),  # white outline
            2  # outline thickness
        )
        self.screen.blit(player_money, (20, 70))
        self.screen.blit(ai_money, (SCREEN_WIDTH - 250, 70))
        
        # Draw sale result
        result_text = render_text_with_outline(
            self.fonts['heading_font'],
            f"You sold the {self.current_product['name']} for ${self.given_price:.2f}", 
            PLAYER_COLOR,
            (255, 255, 255),  # white outline
            2  # outline thickness
        )
        result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(result_text, result_rect)
        
        # Draw profit calculation
        profit = self.given_price - self.user_price
        if profit > 0:
            profit_text = render_text_with_outline(
            self.fonts['heading_font'],
            f"Profit: +${profit:.2f}", 
            PLAYER_COLOR,
            (255, 255, 255),  # white outline
            2  # outline thickness
            )
        else:
            profit_text = render_text_with_outline(
            self.fonts['heading_font'],
            f"Loss: -${-profit:.2f}", 
            HIGHLIGHT_COLOR,
            (255, 255, 255),  # white outline
            2  # outline thickness
            )
        
        profit_rect = profit_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(profit_text, profit_rect)
        
        # Draw client info
        client_panel = pygame.Rect(50, 250, SCREEN_WIDTH - 100, 200)
        pygame.draw.rect(self.screen, PANEL_COLOR, client_panel, border_radius=10)
        
        client_title = self.fonts['heading_font'].render(f"Client #{self.client_cards.index(next((c for c in self.client_cards if c.client == self.chosen_client), self.client_cards[0])) + 1}", True, TEXT_COLOR)
        self.screen.blit(client_title, (client_panel.x + 20, client_panel.y + 20))
        
        # Draw client description with word wrap
        desc = self.chosen_client['description']
        words = desc.split(' ')
        lines = []
        line = ""
        for word in words:
            test_line = line + word + " "
            if self.fonts['small_font'].size(test_line)[0] < client_panel.width - 40:
                line = test_line
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)
        
        y_offset = 70
        for line in lines:
            text_surf = self.fonts['small_font'].render(line, True, TEXT_COLOR)
            self.screen.blit(text_surf, (client_panel.x + 20, client_panel.y + y_offset))
            y_offset += 25
        
        # Draw continue button
        self.continue_button.draw(self.screen)
    
    def draw_game_over(self):
        # Draw background
        self.screen.fill(DARK_BACKGROUND)
        
        # Draw game over text
        game_over = self.fonts['title_font'].render("GAME OVER", True, BUTTON_COLOR)
        game_over_rect = game_over.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(game_over, game_over_rect)
        
        # Draw final scores
        player_score = self.fonts['heading_font'].render(f"Your Money: ${self.user_money:.2f}", True, PLAYER_COLOR)
        player_score_rect = player_score.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(player_score, player_score_rect)
        
        ai_score = self.fonts['heading_font'].render(f"AI Money: ${self.ai_money:.2f}", True, AI_COLOR)
        ai_score_rect = ai_score.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(ai_score, ai_score_rect)
        
        # Draw winner
        if self.user_money > self.ai_money:
            winner_text = self.fonts['title_font'].render("YOU WIN!", True, PLAYER_COLOR)
            self.winner = "player"
            self.winning_sound.play()
        elif self.ai_money > self.user_money:
            winner_text = self.fonts['title_font'].render("AI WINS!", True, AI_COLOR)
            self.winner = "ai"
            self.loosing_sound.play()
        else:
            winner_text = self.fonts['title_font'].render("IT'S A TIE!", True, HIGHLIGHT_COLOR)
            self.winner = "tie"
        
        winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        self.screen.blit(winner_text, winner_rect)
        
        # Draw winner image
        if self.winner == "player":
            winner_img_rect = self.images['human_img'].get_rect(center=(SCREEN_WIDTH // 2, 450))
            self.screen.blit(self.images['human_img'], winner_img_rect)
        elif self.winner == "ai":
            winner_img_rect = self.images['robot_img'].get_rect(center=(SCREEN_WIDTH // 2, 450))
            self.screen.blit(self.images['robot_img'], winner_img_rect)
        else:
            # For a tie, show both images
            human_rect = self.images['human_img'].get_rect(center=(SCREEN_WIDTH // 2 - 80, 450))
            robot_rect = self.images['robot_img'].get_rect(center=(SCREEN_WIDTH // 2 + 80, 450))
            self.screen.blit(self.images['human_img'], human_rect)
            self.screen.blit(self.images['robot_img'], robot_rect)
        
        # Draw play again button
        self.play_again_button.draw(self.screen)
    
    def draw_transition(self, progress):
        # Draw a transition effect (fade in/out)
        transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        alpha = int(255 * (0.5 - abs(0.5 - progress)) * 2)  # Fade in then out
        transition_surface.fill((0, 0, 0, alpha))
        self.screen.blit(transition_surface, (0, 0))
    
    def draw_round_history(self):
        # Skip drawing history on menu and rules screens
        if self.game_state == GameState.MENU:
            return
            
        # Draw 5 circles representing rounds
        circle_radius = 20
        spacing = 15
        total_width = (circle_radius * 2 * 5) + (spacing * 4)
        start_x = (SCREEN_WIDTH - total_width) // 2
        y = 20  # Position at the top
        
        for i in range(5):
            x = start_x + (i * (circle_radius * 2 + spacing))
            circle_pos = (x + circle_radius, y + circle_radius)
            
            # Highlight current round
            if i + 1 == self.current_round:
                pygame.draw.circle(self.screen, HIGHLIGHT_COLOR, circle_pos, circle_radius + 3, 2)
            
            # Draw circle border
            pygame.draw.circle(self.screen, (211, 182, 156), circle_pos, circle_radius, 2)
            
            # If this round has a winner, draw the corresponding image
            if i < len(self.round_winners) and self.round_winners[i] is not None:
                if self.round_winners[i] == "player":
                    # Scale down the player image to fit in the circle
                    scaled_img = pygame.transform.smoothscale(self.images['human_img'], (circle_radius*2-4, circle_radius*2-4))
                    img_rect = scaled_img.get_rect(center=circle_pos)
                    self.screen.blit(scaled_img, img_rect)
                elif self.round_winners[i] == "ai":
                    # Scale down the AI image to fit in the circle
                    scaled_img = pygame.transform.smoothscale(self.images['robot_img'], (circle_radius*2-4, circle_radius*2-4))
                    img_rect = scaled_img.get_rect(center=circle_pos)
                    self.screen.blit(scaled_img, img_rect)
            else:
                # If no winner yet, just show the round number
                round_num = self.fonts['small_font'].render(str(i + 1), True, (211, 182, 156))
                round_rect = round_num.get_rect(center=circle_pos)
                self.screen.blit(round_num, round_rect)
    
    def draw_rules(self):
        # Draw background
        self.screen.fill(BACKGROUND)
        self.screen.blit(self.images['background_img'], (0, 0))
        
        # Draw title
        title = render_text_with_outline(
            self.fonts['title_font'],
            "Game Rules", 
            TEXT_COLOR,
            (255, 255, 255),  # white outline
            2  # outline thickness
        )
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)
        
        # Draw rules text
        y_offset = 120
        line_height = 30
        
        for rule in self.rules:
            if rule == "":  # Empty line for spacing
                y_offset += line_height
                continue
                
            # Use heading font for section titles
            if rule in ["Game Rules:", "Tips:"]:
                text = render_text_with_outline(
                    self.fonts['heading_font'],
                    rule, 
                    HIGHLIGHT_COLOR,
                    (255, 255, 255),  # white outline
                    1  # outline thickness
                )
            else:
                text = render_text_with_outline(
                    self.fonts['regular_font'],
                    rule, 
                    TEXT_COLOR,
                    (255, 255, 255),  # white outline
                    1  # outline thickness
                )
                
            text_rect = text.get_rect(midleft=(SCREEN_WIDTH // 12, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += line_height
        
        # Draw understood button
        self.understood_button.draw(self.screen)
    
    def draw(self):
        # Draw current game state
        if self.game_state == GameState.MENU:
            self.draw_menu()
        elif self.game_state == GameState.BIDDING:
            self.draw_bidding()
        elif self.game_state == GameState.EVENT:
            self.draw_event()
        elif self.game_state == GameState.RESULTS:
            self.draw_results()
        elif self.game_state == GameState.GAME_OVER:
            self.draw_game_over()
            
        self.draw_round_history()
        
        # Draw transition if active
        if self.transition_animation.running:
            progress = self.transition_animation.update()
            self.draw_transition(progress)
    
    def update(self, dt, mouse_pos):
        # Update UI elements based on current state
        if self.game_state == GameState.MENU:
            self.start_button.update(mouse_pos)
        elif self.game_state == GameState.BIDDING:
            self.bid_input.update()
            self.place_bid_button.update(mouse_pos)
            #self.ai_sale_animation_started = False
            self.showed_view = False
        elif self.game_state == GameState.EVENT:
            if self.showed_view == False:
                self.start_time = pygame.time.get_ticks()
                self.showed_view = True
            if self.bid_result == "player":
                # Update client cards
                for card in self.client_cards:
                    card.update(mouse_pos)
            elif self.chosen_client:
                self.continue_button.update(mouse_pos)
        elif self.game_state == GameState.RESULTS:
            self.continue_button.update(mouse_pos)
        elif self.game_state == GameState.GAME_OVER:
            self.play_again_button.update(mouse_pos)
    
    def handle_event(self, event):
        # Handle events based on current state
        if event.type == QUIT:
            return False
        
        if self.game_state == GameState.MENU:
            if self.start_button.is_clicked(event):
                self.next_round()  # Go directly to first round instead of rules
        elif self.game_state == GameState.BIDDING:
            # Handle bid input
            bid_result = self.bid_input.handle_event(event)
            if bid_result is not None:
                # Enter was pressed
                if self.place_bid():
                    self.transition_to_state(GameState.EVENT)
            
            # Handle place bid button
            if self.place_bid_button.is_clicked(event):
                if self.place_bid():
                    self.transition_to_state(GameState.EVENT)
        elif self.game_state == GameState.EVENT:
            # If player's turn, handle client selection
            if self.bid_result == "player":
                for card in self.client_cards:
                    if card.button.is_clicked(event):
                        self.select_client(card)
                        break
            # If AI's turn and has chosen client, continue button
            elif self.chosen_client and self.continue_button.is_clicked(event):
                self.next_round()
        elif self.game_state == GameState.RESULTS:
            if self.continue_button.is_clicked(event):
                self.next_round()
        elif self.game_state == GameState.GAME_OVER:
            if self.play_again_button.is_clicked(event):
                self.reset_game()
                self.next_round()
        
        return True
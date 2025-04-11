# Souk King - Technical Documentation

---

## 1. Introduction

**Souk King** is a single-player turn-based negotiation and trading simulation game implemented using Python and the Pygame library. The player competes against an AI opponent over five rounds to maximize their profit by bidding on products and selling them to clients in a virtual marketplace (**souk**). The game incorporates random events that affect gameplay and utilizes the Ollama library to power the AI's decision-making process for bidding and client selection.

The game is at it’s core a competition between the AI and the player in language comprehension and risk reward management. Which would at first glance appear to give the human an advantage. However as you play the game you might come to realize that this isn’t always the case :).

This document details the technical aspects of the game, including its architecture, components, core logic, data structures, and setup instructions.

## 2. General Overview

Souk King is a competitive trading game where you face off against an AI opponent in a bustling marketplace setting. The primary goal is to end the game with more money than the AI after five rounds of play. Each round centers around acquiring a unique product through a secret bidding process. Both you and the AI submit bids, and the higher bidder wins the right to sell that product for the round, paying the amount they bid.

Once a player wins the bid, the game introduces a random daily event. These events can significantly impact the round, such as doubling the selling price on a "High Demand Day," halving it on a "Low Demand Day," or even forcing a donation on a "Charity Day." The player who won the bid then gets presented with a small selection of potential clients, each with their own personality and willingness to pay. The number of clients available is influenced by how high the winning bid was compared to the product's base price – bidding excessively high might win the item but attract fewer buyers.

Choosing the right client is crucial for maximizing profit. The player manually selects who they think will offer the best price based on descriptions, while the AI uses its underlying language model to analyze the clients and make its choice. After the sale, the profit (or loss) is calculated, money totals are updated, and the game progresses to the next round's bidding phase. After the fifth round concludes, the player with the most money is declared the Souk King.

## 3. System Architecture

The game follows a modular structure primarily organized into three Python files:

1. **`main.py`**: The main entry point of the application. It handles game initialization (Pygame, fonts, images), instantiates the core game class, and manages the main game loop (event handling, updates, drawing).
2. **`game.py`**: Contains the `SoukKingGame` class, which encapsulates the entire game state, logic, and UI management. This includes round progression, bidding, event handling, client interaction, AI integration, and drawing different game screens.
3. **`functions.py`**: Provides utility functions used by `game.py`, specifically for calculating the number of available clients based on pricing and summarizing the AI's past performance (memory) for input into the AI model.

Additionally, the project relies on:

- **`data.py`** (Implicit): Although not provided, this file is referenced and presumably contains lists of dictionaries defining `products`, `clients`, and `events` used within the game.
- **`ui/` directory**: Contains UI-related code:
    - `constants.py`: Defines constants like screen dimensions, colors, game states (`GameState` Enum), and helper functions like `init_fonts` and `render_text_with_outline`.
    - `components/`: Contains reusable UI element classes (`Animation`, `Button`, `InputBox`, `ClientCard`).
- **External Libraries**:
    - `pygame`: Used for graphics rendering, event handling, timing, and basic UI.
    - `ollama`: Used to interact with a local Large Language Model (LLM) instance (specifically `llama3.2:latest` as configured) to generate AI bids and client choices.
- **Assets (`noobs/src/images/`)**: Contains image files used for the game's visual elements (background, logos, player/AI icons).

The game operates based on a **State Machine** pattern, managed by the `game_state` variable within the `SoukKingGame` class (using the `GameState` Enum from `ui.constants`). The game transitions between states like `MENU`, `BIDDING`, `EVENT`, `RESULTS`, and `GAME_OVER`, with different logic, UI elements, and event handling active in each state.

## 4. File Breakdown

### 4.1. `main.py`

- **Purpose**: Application entry point, initialization, and main game loop orchestration.
- **Key Components**:
    - `load_game_images()`:
        - Loads necessary image assets (`logo`, `human`, `robot`, `background`).
        - Resizes images appropriately.
        - Includes error handling (`try...except pygame.error`) to create placeholder surfaces if image files are missing, ensuring the game can still run visually.
    - `main()`:
        - Initializes Pygame modules (`pygame.init`, `pygame.font.init`, `pygame.mixer.init`).
        - Sets up the display window (`pygame.display.set_mode`, `pygame.display.set_caption`).
        - Initializes fonts using `init_fonts()` from `ui.constants`.
        - Loads images using `load_game_images()`.
        - Creates an instance of the `SoukKingGame` class.
        - Runs the main game loop:
            - Manages frame rate using `pygame.time.Clock`.
            - Calculates delta time (`dt`).
            - Gets mouse position.
            - Handles Pygame events by calling `game.handle_event()`.
            - Updates game state by calling `game.update()`.
            - Draws the current game screen by calling `game.draw()`.
            - Updates the display (`pygame.display.flip()`).
        - Handles game exit (`pygame.quit`, `sys.exit`).
- **Dependencies**: `pygame`, `sys`, `game.SoukKingGame`, `ui.constants`, `ui.components`.

### 4.2. `functions.py`

- **Purpose**: Contains standalone helper functions for game logic calculations.
- **Key Components**:
    - `calculate_number_of_clients(base_price, resale_price)`:
        - Calculates the profit margin `(resale_price - base_price) / base_price`.
        - Returns the number of clients (1, 2, or 3) based on margin thresholds:
            - `margin <= 0.70`: 3 clients (reasonable price)
            - `0.70 < margin <= 1.1`: 2 clients (slightly high price)
            - `margin > 1.1`: 1 client (high price)
        - This simulates the effect of pricing on market demand.
    - `summarize_ai_memory(memory)`:
        - Takes the `ai_memory` list (a list of dictionaries, each representing a past round) as input.
        - Formats the memory into a natural language string summarizing previous rounds from the AI's perspective.
        - Includes round number, event, who won the bid, and the financial outcome (profit/loss) for the winner.
        - Handles the case of an empty memory (first round).
        - This summary is crucial for providing context to the Ollama LLM when it makes decisions.
- **Dependencies**: None external to standard Python.

### 4.3. `game.py`

- **Purpose**: Defines the main `SoukKingGame` class, managing all core game logic, state, and rendering.
- **Class: `SoukKingGame`**:
    - **`__init__(self, screen, fonts, images)`**:
        - Initializes game variables: `user_money`, `ai_money`, event weights, `ai_memory`, timing variables, product/client selections, game state (`GameState.MENU`), round tracking, bidding results, UI elements, etc.
        - Stores references to the screen, fonts, and images.
        - Defines the `rules` text list.
        - Calls `create_ui()` to instantiate UI components.
    - **`create_ui(self)`**:
        - Instantiates all necessary `Button` and `InputBox` objects for different game states.
    - **`reset_game(self)`**:
        - Resets game variables to their initial state for starting a new game.
    - **`next_round(self)`**:
        - Increments `current_round`.
        - Checks for game over condition (5 rounds completed).
        - Selects the `current_product` for the round.
        - Includes logic to find an affordable product if both players lack funds for the initially selected one; ends the game if no affordable products remain.
        - Resets round-specific variables (`bid_result`, prices, clients, UI states).
        - Transitions state to `GameState.BIDDING`.
    - **`transition_to_state(self, new_state)`**:
        - Changes the `self.game_state`.
        - (Commented out) Potentially starts a transition animation.
    - **`place_bid(self)`**:
        - Handles the player submitting a bid via the `InputBox`.
        - Validates the bid (numeric, >= base price, <= player money).
        - Handles the edge case where the player cannot afford the base price (auto-bids 0).
        - If valid, stores `self.user_price` and calls `get_ai_bid()`.
        - Returns `True` on success, `False` on validation failure.
    - **`get_ai_bid(self)`**:
        - Handles the AI determining its bid.
        - Checks if AI can afford the base price; bids -1 if not.
        - Summarizes past rounds using `summarize_ai_memory(self.ai_memory)`.
        - Constructs a detailed prompt for the Ollama LLM (`llama3.2:latest`) including game state, AI money, player money, product details, strategy hints, and the memory summary.
        - Sends the prompt to Ollama via `ollama.chat`.
        - Parses the numeric bid from the response.
        - Includes validation and fallback logic for the AI's bid (must be >= base price, <= AI money; retries once, then defaults to a safe bid).
        - Adjusts AI bid slightly to avoid exact ties with the player.
        - Stores `self.ai_price` and calls `process_bid_result()`.
        - Includes basic error handling for the Ollama call.
    - **`process_bid_result(self)`**:
        - Compares `self.user_price` and `self.ai_price` to determine the `bid_result` ("player" or "ai").
        - Updates the `round_winners` list.
        - Deducts the winning bid amount from the winner's money, storing the old value and starting the `money_animation`.
        - Calls either `handle_player_turn()` or `handle_ai_turn()` based on the winner.
        - Transitions state to `GameState.EVENT`.
    - **`handle_player_turn(self)`**:
        - Randomly selects an `event` using `random.choices` and `event_weights`.
        - Calculates the effective selling price based on the event ("High demand day" doubles, "Low demand day" halves).
        - Generates the number of clients using `calculate_number_of_clients()`.
        - Randomly selects clients from the `clients` list.
        - Calls `create_client_cards()` to prepare the UI.
    - **`handle_ai_turn(self)`**:
        - Similar to `handle_player_turn` for event selection and client generation.
        - Uses Ollama (`llama3.2:latest`) with a specific prompt to choose the client most likely to offer the highest price based on descriptions. Includes validation and fallback for the choice.
        - Calculates the `given_price` the chosen client will offer based on the event and client's `offer_percentage`.
        - Calculates the `final_ai_money` *after* the sale and potential event effects (like "Charity day" deduction), but **does not update `self.ai_money` yet**. The update happens visually via animation later.
        - Appends a detailed record of the round to `self.ai_memory`.
        - Calls `create_client_cards()` for display purposes.
    - **`create_client_cards(self)`**:
        - Creates `ClientCard` instances for the `selected_clients`.
        - Dynamically calculates positions to display 1, 2, or 3 cards neatly centered horizontally.
    - **`select_client(self, client_card)`**:
        - Called when the player clicks a client card button.
        - Sets `self.chosen_client`.
        - Calculates the final `given_price` based on event and client percentage.
        - Updates `self.user_money`, applying event effects ("Charity day"). Stores old value and starts `money_animation`.
        - Appends the round outcome to `self.ai_memory`.
        - Transitions state to `GameState.RESULTS`.
    - **Drawing Methods (`draw_menu`, `draw_bidding`, `draw_event`, `draw_results`, `draw_game_over`, `draw_rules`, `draw_round_history`, `draw_transition`)**:
        - Each method is responsible for rendering a specific game screen or UI element.
        - They utilize `pygame.draw` functions and render text using `fonts` (often with `render_text_with_outline`).
        - Display game state info (round, money).
        - Integrate with `money_animation` and `ai_sale_animation` to show smooth money transitions.
        - Draw UI components (`Button`, `InputBox`, `ClientCard`).
        - `draw_event` includes logic to show bid results initially, then event info, then client selection/AI choice presentation with timing delays (`pygame.time.get_ticks()`).
        - `draw_round_history` displays the progress through the 5 rounds and indicates the winner of each completed round.
    - **`draw(self)`**:
        - The main drawing dispatcher. Calls the appropriate `draw_*` method based on `self.game_state`.
        - Always calls `draw_round_history`.
        - Draws the transition overlay if `self.transition_animation` is running.
    - **`update(self, dt, mouse_pos)`**:
        - Called each frame in the main loop.
        - Updates active UI elements (checking for hover/clicks) based on the current `game_state`.
        - Manages timing flags (`start_time`, `showed_view`) for the `EVENT` state display sequence.
        - Updates running animations (`money_animation`, potentially `transition_animation` and `ai_sale_animation`).
    - **`handle_event(self, event)`**:
        - Processes Pygame events passed from the main loop.
        - Handles `QUIT` events.
        - Routes input (clicks, key presses for `InputBox`) to the relevant UI elements or game logic functions based on the current `game_state`.
        - Triggers state transitions or actions (e.g., placing bid, selecting client, continuing, playing again).
- **Dependencies**: `pygame`, `random`, `ollama`, `functions`, `data`, `ui.constants`, `ui.components`.

## 5. Key Concepts and Mechanics

- **Game Flow**: The game progresses through 5 rounds. Each round typically follows the state sequence: `BIDDING` -> `EVENT` -> (`RESULTS` if player won bid) -> `BIDDING` (next round). The game starts in `MENU` and ends in `GAME_OVER`.
- **Bidding**: Players bid secretly. The highest bidder wins the product for the round and pays their bid amount. Ties are broken by slightly increasing the AI's bid during calculation. Bidding higher increases the chance of winning but reduces potential profit margin and the number of clients available (via `calculate_number_of_clients`).
- **Events**: Random events (`Normal day`, `High demand day`, `Low demand day`, `Charity day`) occur each round after bidding, influencing the final selling price or causing money deductions.
- **Client System**: The winner of the bid gets to sell to clients. The number of clients depends on the bid price relative to the base price. Each client has a unique description and an `offer_percentage` modifying the final sale price.
    - **Player Choice**: The player manually selects a client.
    - **AI Choice**: The AI uses Ollama to analyze client descriptions and predict which one will offer the best price.
- **AI (Ollama Integration)**:
    - **Bidding**: The AI receives context (current money, player money, product info, past round summary) and is prompted to provide a strategic bid.
    - **Client Selection**: The AI receives client descriptions and is prompted to choose the one most likely to pay the highest price.
    - **Dependency**: Requires a running local Ollama instance serving the `llama3.2:latest` model. Network latency or model issues can affect gameplay smoothness or AI behavior.
- **Money Management**: Player and AI money are tracked. Changes are animated smoothly using the `Animation` class and temporary storage of old values (`old_user_money`, `old_ai_money`).
- **State Management**: The `game_state` variable controls which part of the game logic is active and what is drawn on the screen.
- **UI**: Custom classes for Buttons, Input Boxes, and Client Cards provide interactive elements. Animations add visual feedback for money changes. Text rendering uses outlines for better visibility against the background.

## 6. Data Structures

- **`products` (List of Dicts)**: stored in `data.py`. Each dictionary represents a product:
    - `name`: `str` (e.g., "Ancient Vase")
    - `base_price`: `float` or `int` (e.g., 50)
    - `description`: `str` (e.g., "A dusty pot from forgotten times.")
- **`clients` (List of Dicts)**: stored in `data.py`. Each dictionary represents a potential client:
    - `description`: `str` (e.g., "A wealthy collector looking for rare items.")
    - `offer_percentage`: `float` (e.g., 1.2 for 120% of the calculated price)
- **`events` (List of Dicts)**: stored in `data.py`. Each dictionary represents a possible daily event:
    - `name`: `str` (e.g., "High demand day")
    - `description`: `str` (e.g., "Everyone wants what you're selling! Price doubles!")
    - *(Implicit)* Associated effect logic implemented in `handle_player_turn`/`handle_ai_turn`/`select_client`.
- **`ai_memory` (List of Dicts)**: Managed within `SoukKingGame`. Each dictionary stores data about a completed round:
    - `round`: `int`
    - `event`: `str` (Name of the event)
    - `ai`: `dict` containing AI's actions/results (`bought_for`, `sold_for`, `profit`, `note` like "Lost to player")
    - `player`: `dict` containing Player's actions/results (`bought_for`, `sold_for`, `profit`, `note` like "Lost to AI")

## 7. UI Components (`ui/components/`)

- **`Animation(duration)`**: A simple timer class to manage animations over a set `duration`. Tracks `start_time` and `running` status. `update()` returns progress (0.0 to 1.0).
- **`Button(x, y, width, height, text, font)`**: A clickable button component. Handles drawing, hover effects, and click detection (`is_clicked`).
- **`InputBox(x, y, w, h, text, font)`**: A text input field. Handles user text input (typing, backspace), rendering the text, and indicating active state. `handle_event` manages key presses and returns text on Enter.
- **`ClientCard(x, y, width, height, client, number, small_font)`**: Displays information about a client, including their description and number. Contains a nested `Button` for selection. Manages hover effects (slight vertical offset) and selection state (`selected`).

## 8. External Dependencies

- **Python 3**: The programming language used.
- **Pygame**: `pip install pygame` - For graphics, sound (mixer initialized but not used), input, and windowing.
- **Ollama**: `pip install ollama` - Python client library to interact with the Ollama service.
- **Ollama Service**: A running instance of Ollama is required on the host machine.
- **Ollama Model**: The specific LLM used (`llama3.2:latest` by default) must be pulled/available within the Ollama service (`ollama pull llama3.2:latest`).

## 9. Setup and Running

1. **Install Python**: Ensure Python 3 is installed.
2. **Install Dependencies**:
    
    ```bash
    pip install pygame ollama
    ```
    
3. **Set up Ollama**:
    - Install Ollama from [ollama.com](https://ollama.com/).
    - Ensure the Ollama service is running in the background.
    - Pull the required model:
        
        ```bash
        ollama pull llama3.2:latest
        ```
        
4. **Get Game Files**: Place `main.py`, `game.py`, `functions.py`, `data.py` (if separate), and the `ui/` directory with its contents in the same project folder.
5. **Get Assets**: Create the `noobs/src/images/` path relative to where you run the script, or adjust the paths in `main.py`, and place the required image files (`Souk king color.png`, `human.png`, `robot.png`, `blurred_bg.jpg`) inside.
6. **Run the Game**:
    
    ```bash
    python main.py
    ```
    

## 10. Potential Improvements and Future Work

- **AI Strategy**: Enhance AI prompts for more sophisticated bidding and client selection strategies (e.g., considering remaining rounds, player's financial state, risk assessment).
- **Error Handling**: More robust error handling for Ollama API calls (timeouts, connection errors, unexpected responses). Provide user feedback if AI fails.
- **UI/UX**:
    - Add visual feedback for invalid bids.
    - Implement smoother screen transitions (using `transition_animation`).
    - Add sound effects and background music.
    - Improve visual clarity of different game states.
    - Show client `offer_percentage` potential more clearly (perhaps after selection).
- **Gameplay**:
    - Add more diverse products, clients, and events.
    - Implement items or abilities players could acquire.
    - Introduce difficulty levels (affecting AI aggressiveness or starting money).
    - Consider a simple market fluctuation mechanic affecting base prices.
- **Persistence**: Add functionality to save and load game progress.
- **Configuration**: Allow configuration of AI model, starting money, or number of rounds via a config file or menu options.
- **Code Refactoring**: Potentially break down the large `SoukKingGame` class further if complexity increases significantly. Improve separation of concerns between game logic and drawing.

## 11. Conclusion

Souk King provides a functional framework for a Pygame-based trading simulation game featuring LLM-powered AI decision-making. The code is structured modularly, utilizing a state machine and custom UI components. This documentation provides a comprehensive overview of its technical implementation, serving as a guide for understanding and future development.

---
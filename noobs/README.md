PS : the demo provided contains some lag because the computer we were running it on was slow and didnt have a gpu which is necessary for the model to run on.


# Souk King

Souk King is a simple marketplace simulation game built with Pygame. Players compete against an AI merchant (powered by a local Ollama instance) in a Moroccan souk setting. The goal is to buy products through bidding and sell them to clients for the highest profit over 5 rounds.

## Features

*   Bid against an AI for unique Moroccan-themed products.
*   Sell acquired products to different clients, each offering varying prices based on their profile.
*   Navigate random daily events that impact gameplay (e.g., high/low demand, charity day).
*   Manage your money wisely over 5 rounds to become the Souk King.
*   Simple graphical interface using Pygame.
*   AI decision-making (bidding and client selection) powered by a local Ollama instance.
*   Basic sound effects for interactions and game outcomes.

## Requirements

*   Python 3.x
*   Pygame library: `pip install pygame`
*   Ollama Python library: `pip install ollama`
*   A running local [Ollama](https://ollama.com/) instance.
*   A suitable Ollama model pulled (the code uses `llama3.2:latest`). You can pull it using: `ollama pull llama3.2`

## Setup

1.  **Clone the repository** or download the source files (`main.py`, `game.py`, `functions.py`, `data.py`, and the `ui/` and `noobs/` directories).
2.  **Install Python libraries**:
    ```bash
    pip install pygame ollama
    ```
3.  **Install Ollama**: Follow the instructions on [ollama.com](https://ollama.com/).
4.  **Pull the AI model**: Open your terminal and run:
    ```bash
    ollama pull llama3.2
    ```
5.  **Run Ollama**: Ensure the Ollama application/server is running in the background *before* starting the game.
6.  **File Structure**: Make sure the directory structure is maintained, especially the paths to images and sounds (`noobs/src/images/`, `noobs/src/ui/sounds/`). The script expects these relative paths to exist.

## How to Run

1.  Make sure your local Ollama instance is running with the `llama3.2` model available.
2.  Navigate to the directory containing `main.py` in your terminal.
3.  Run the game using:
    ```bash
    python main.py
    ```

## File Overview

*   `main.py`: The main entry point for the game. Initializes Pygame, loads assets, and starts the game loop.
*   `game.py`: Contains the core `SoukKingGame` class, handling game states, logic, UI drawing, event handling, and interaction with Ollama.
*   `functions.py`: Includes helper functions like `summarize_ai_memory` and `calculate_number_of_clients`.
*   `data.py`: Stores the list of products, clients, and events used in the game.
*   `ui/`: Directory containing UI components (`constants.py`, `button.py`, `input_box.py`, `client_card.py`, `animation.py`).
*   `noobs/src/`: Directory containing game assets (images in `images/`, sounds in `ui/sounds/`).

Enjoy playing Souk King!

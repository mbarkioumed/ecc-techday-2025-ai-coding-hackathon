# Souk King - Technical Documentation

## 1. Overview of Technologies and Design Choices

### 1.1 Core Technologies

**Souk King** is a turn-based trading game built using the following technologies:

-   **Python (3.x)**: Primary programming language for game logic and application structure
-   **Pygame (2.x)**: Game development library for handling graphics, input, and window management
-   **Ollama**: API wrapper for running local LLM inference, enabling AI decision-making
-   **Llama 3.2**: Foundation large language model powering the AI opponent's strategic decisions

### 1.2 Design Philosophy

The game follows several key design principles:

-   **Accessibility**: Simple UI with clear visual feedback and intuitive controls
-   **Strategic Depth**: Complex economic mechanics balanced with straightforward gameplay
-   **Fairness**: The AI opponent uses the same rule constraints as the human player
-   **Visual Clarity**: Information hierarchy and game state are clearly communicated
-   **Modularity**: Code structured to allow easy extension and modification

## 2. Architecture

### 2.1 Code Organization

The codebase follows a modular structure inspired by the Model-View-Controller (MVC) pattern:

```
souk-king/
├── main.py                 # Entry point and initialization
├── game.py                 # Core game logic and state management
├── data.py                 # Game data (products, clients, events)
├── functions.py            # Utility functions and helpers
├── ui/
│   ├── constants.py        # UI constants and shared resources
│   ├── components/         # Reusable UI elements
│       ├── animation.py    # Animation system
│       ├── button.py       # Interactive button component
│       ├── input_box.py    # Text input component
│       └── client_card.py  # Client display component
└── images/                 # Game assets and images
```

### 2.2 State Management

The game uses a state machine pattern with the following primary states:

```python
class GameState:
    MENU = 0      # Start menu and rules display
    BIDDING = 1   # Player placing bids on products
    EVENT = 2     # Day's event and bidding results
    RESULTS = 3   # Showing results of player's sales
    GAME_OVER = 4 # End game state with final scores
```

State transitions are handled through the `transition_to_state()` method, which manages cleanup and initialization between states.

### 2.3 Rendering Pipeline

The rendering system uses layered drawing for compositing the interface:

1. Background layer (solid color or background image)
2. Game state-specific elements (panels, cards, text)
3. UI components (buttons, input fields)
4. Overlay elements (animations, transitions)
5. HUD elements (money display, round indicators)

This layering approach ensures consistent visual hierarchy and allows for isolated component updates.

## 3. AI Implementation

### 3.1 AI Bidding Strategy

The AI opponent uses the Llama 3.2 model through Ollama to make strategic bidding decisions with the following approach:

```python
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
```

The AI receives:

-   A memory summary of previous rounds
-   Current game state (money, product details)
-   Strategic considerations
-   A clear instruction to output only a numeric bid value

This enables the AI to make contextually appropriate decisions that adapt to the game state.

### 3.2 AI Client Selection

For client selection, the AI analyzes client descriptions to determine which client is likely to offer the highest price:

```python
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
```

The AI evaluates semantic cues in the descriptions to identify clients with higher willingness to pay.

### 3.3 Memory and Learning System

The AI maintains a memory of previous rounds to inform future decisions:

```python
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
```

This memory tracking allows the AI to:

1. Learn from profitable/unprofitable decisions
2. Adapt to player bidding patterns
3. Consider the impact of different events
4. Optimize its strategy in later rounds

## 4. Game Mechanics and Algorithms

### 4.1 Bidding System

The bidding system implements the following logic:

-   Players must bid at least the base price of the product
-   The highest bidder wins the product
-   Bid validation ensures the player has sufficient funds
-   Special handling for cases where player/AI cannot afford the base price
-   Tie-breaking mechanism (AI slightly increases bid)

### 4.2 Client Generation Algorithm

```python
def calculate_number_of_clients(base_price, bid_price):
    """Calculate number of clients based on bid price relative to base price"""
    if bid_price <= base_price:
        return 1

    ratio = bid_price / base_price

    if ratio < 1.2:
        return 3  # Low markup = many clients
    elif ratio < 1.5:
        return 2  # Medium markup = fewer clients
    else:
        return 1  # High markup = very few clients
```

This algorithm implements a key economic mechanic: higher bids reduce the number of potential clients, creating a risk/reward tradeoff.

### 4.3 Event System

Events modify gameplay through a weighted random selection system:

```python
self.event_weights = [0.15, 0.55, 0.15, 0.15]
self.selected_event = random.choices(events, weights=self.event_weights, k=1)[0]
```

Available events include:

-   **Normal day** (55% chance): Standard trading conditions
-   **High demand day** (15% chance): Selling price doubles
-   **Low demand day** (15% chance): Selling price halves
-   **Charity day** (15% chance): Player donates 20% of their money

### 4.4 Animation System

The game uses a time-based animation system for smooth transitions:

```python
class Animation:
    """Animation class for smooth transitions"""
    def __init__(self, duration=1.0):
        self.duration = duration
        self.start_time = None
        self.progress = 0
        self.running = False

    def start(self):
        self.start_time = time.time()
        self.running = True
        self.progress = 0

    def update(self):
        if not self.running:
            return 1

        elapsed = time.time() - self.start_time
        self.progress = min(elapsed / self.duration, 1)

        if self.progress >= 1:
            self.running = False

        return self.progress
```

This system powers several visual effects:

-   Money value changes
-   Card fading transitions
-   Screen transitions between game states

## 5. UI Components

### 5.1 Button Component

```python
class Button:
    def __init__(self, x, y, width, height, text, font=None, color=BUTTON_COLOR, text_color=TEXT_COLOR):
        # Initialization code...

    def update(self, mouse_pos):
        # Hover detection
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        # Click detection with event handling
        return event.type == MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

    def draw(self, surface):
        # Visual rendering with hover effects
```

The button component implements:

-   Hover state detection and visual feedback
-   Click detection with event filtering
-   Consistent styling and positioning

### 5.2 Client Card Component

```python
class ClientCard:
    def __init__(self, x, y, width, height, client, number, small_font=None):
        # Setup code

    def update(self, mouse_pos):
        # Card interaction logic
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.y_offset = -10 if self.hovered else 0
        self.button.update(mouse_pos)

    def draw(self, surface):
        # Card rendering with animations and state changes
```

The client card component features:

-   Hover animations (vertical offset)
-   Selected state visualization
-   Interactive select button
-   Description text with word wrapping

### 5.3 Text Rendering with Outlines

```python
def render_text_with_outline(font, text, text_color, outline_color, outline_width=2):
    # Render text with an outline for better visibility on varied backgrounds
    outline_surfaces = []

    # Create outline by rendering the text multiple times with offset positions
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
        for i in range(outline_width):
            x_offset = dx * (i + 1)
            y_offset = dy * (i + 1)
            outline_surf = font.render(text, True, outline_color)
            outline_surfaces.append((outline_surf, x_offset, y_offset))

    # Render the actual text and composite
    # ...
```

This custom rendering function improves text readability against complex backgrounds through an outline effect.

## 6. Performance Optimizations

Several performance considerations are implemented:

1. **Limited animations**: Animations only run when needed and with appropriate durations
2. **Efficient rendering**: Only drawing what's necessary for the current game state
3. **Asset caching**: Images and fonts loaded once at initialization
4. **Lightweight UI**: Simple shapes and minimal effects to reduce rendering overhead
5. **LLM optimization**: Carefully crafted prompts to minimize token usage and response time

## 7. Future Development Considerations

The architecture supports several potential enhancements:

1. **Additional game modes**: The state-based design facilitates new gameplay variants
2. **Extended AI capabilities**: The AI system could be enhanced with more sophisticated strategies
3. **Multiplayer support**: The client-server model could be adapted for online play
4. **Expanded content**: Additional products, clients, and events could be added
5. **Save/load functionality**: Game state serialization for persistent gameplay

---

This documentation provides a comprehensive overview of the technical implementation of Souk King, highlighting the integration of traditional game development approaches with modern AI capabilities to create an engaging and challenging trading game.

Similar code found with 2 license types

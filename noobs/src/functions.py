def calculate_number_of_clients(base_price, resale_price):
    """
    Returns a number of clients (between 1 and 3) based on the difference between the base price and the resale price.
    """
    margin = (resale_price - base_price) / base_price

    if margin <= 0.70:
        return 3  # Reasonable price → 3 clients
    elif margin <= 1.1:
        return 2  # Slightly high → 2 clients
    else:
        return 1  # Too high → 1 client only


def summarize_ai_memory(memory):
    # If there is no memory (empty list), return a message indicating it's the first round.
    if not memory:
        return "This is the first round."

    # Initialize an empty string to store the summary of each round.
    summary = ""

    # Loop through each round's entry in the memory.
    for entry in memory:
        round_num = entry['round']  # The round number.
        event = entry['event']      # The event that occurred in this round.

        ai_data = entry['ai']       # Data related to the AI's performance (buying/selling).
        player_data = entry['player']  # Data related to the player's performance (buying/selling).

        # Create the base summary for the current round, including the round number and event.
        round_summary = f"Round {round_num} , event of the day: ({event}) "

        # Check if the AI lost to the player (based on the note).
        if ai_data.get("note") == "Lost to player":
            round_summary += "You lost the product to the player."
            
            # If the player made a profit, include details of their buying/selling actions.
            if player_data["profit"] > 0:
                round_summary += (f" The player bought it for {player_data['bought_for']}$, sold it for {player_data['sold_for']}$, "
                                  f"and made a profit of {player_data['profit']:.2f}$.")
            # If the player lost money, include details of their buying/selling actions.
            elif player_data["profit"] < 0:
                round_summary += (f" The player bought it for {player_data['bought_for']}$, sold it for {player_data['sold_for']}$, "
                                  f"but lost {-player_data['profit']:.2f}$.")
            # If the player broke even (no profit or loss), state that.
            else:
                round_summary += (f" The player broke even after buying for {player_data['bought_for']}$ "
                                  f"and selling for {player_data['sold_for']}$.")
        
        # Check if the player lost to the AI (based on the note).
        elif player_data.get("note") == "Lost to AI":
            round_summary += "You won the product."
            
            # If the AI made a profit, include details of their buying/selling actions.
            if ai_data["profit"] > 0:
                round_summary += (f" You bought it for {ai_data['bought_for']}$, sold it for {ai_data['sold_for']}$, "
                                  f"and made a profit of {ai_data['profit']:.2f}$.")
            # If the AI lost money, include details of their buying/selling actions.
            elif ai_data["profit"] < 0:
                round_summary += (f" You bought it for {ai_data['bought_for']}$, sold it for {ai_data['sold_for']}$, "
                                  f"but lost {-ai_data['profit']:.2f}$.")
            # If the AI broke even (no profit or loss), state that.
            else:
                round_summary += (f" You broke even after buying for {ai_data['bought_for']}$ "
                                  f"and selling for {ai_data['sold_for']}$.")
        
        # If neither the AI nor the player has a note (meaning there's no clear winner), state that data is incomplete.
        else:
            round_summary += "Data was incomplete."

        # Add the round's summary to the final summary string.
        summary += round_summary + "\n"

    # Return the complete summary, removing any extra spaces at the end.
    return summary.strip()

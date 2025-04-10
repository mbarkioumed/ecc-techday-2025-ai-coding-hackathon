import random
import time
import ollama
from data import products, clients, events

user_money = 300
ai_money = 300
event_weights = [0.2, 0.5, 0.15, 0.15]
ai_memory = []

def summarize_ai_memory(memory):
   
    if not memory:
        return "This is the first round."

    summary = ""


    for entry in memory:
        round_num = entry['round']
        event = entry['event']
        

        ai_data = entry['ai']
        player_data = entry['player']

        round_summary = f"Round {round_num} , event of the day: ({event}) "

        if ai_data.get("note") == "Lost to player":
            round_summary += "You lost the product to the player."
            if player_data["profit"] > 0:
                round_summary += (f" The player bought it for {player_data['bought_for']}$, sold it for {player_data['sold_for']}$, "
                                  f"and made a profit of {player_data['profit']:.2f}$.")
            elif player_data["profit"] < 0:
                round_summary += (f" The player bought it for {player_data['bought_for']}$, sold it for {player_data['sold_for']}$, "
                                  f"but lost {-player_data['profit']:.2f}$.")
            else:
                round_summary += (f" The player broke even after buying for {player_data['bought_for']}$ "
                                  f"and selling for {player_data['sold_for']}$.")
        elif player_data.get("note") == "Lost to AI":
            round_summary += "You won the product."
            if ai_data["profit"] > 0:
                round_summary += (f" You bought it for {ai_data['bought_for']}$, sold it for {ai_data['sold_for']}$, "
                                  f"and made a profit of {ai_data['profit']:.2f}$.")
            elif ai_data["profit"] < 0:
                round_summary += (f" You bought it for {ai_data['bought_for']}$, sold it for {ai_data['sold_for']}$, "
                                  f"but lost {-ai_data['profit']:.2f}$.")
            else:
                round_summary += (f" You broke even after buying for {ai_data['bought_for']}$ "
                                  f"and selling for {ai_data['sold_for']}$.")
        else:
            round_summary += "Data was incomplete."

        summary += round_summary + "\n"

    return summary.strip()



# Pick 5 random products for this round
selected_products = random.sample(products, 5)

# round execution
for round_num, product in enumerate(selected_products, 1):
    print(f"\n==== ROUND {round_num} ====")
    print(f"You have {user_money:.2f}$.")
    print(f"AI Vendor has {ai_money:.2f}$.")
    print(f"\n🛒 Product: {product['name']} (Base Price: {product['base_price']}$)")

    memory_summary = summarize_ai_memory(ai_memory)

    messages = [
        {"role": "system", "content": f"""
You are an AI vendor in a negotiation game. Your goal is to make more money than the player.
{memory_summary}

Current situation:
- You have {ai_money}$
- The player has {user_money}$
- You're bidding on: {product['name']} (Base Price: {product['base_price']}$)

🧠 Strategy:
- High bids help you win the product but increase risk.
- Some days cause you to lose money (like 'Charity Day').
- If you overspend, you may not profit.
- You want to win by the final round.

Respond with a **single numeric value** — your bid.
"""},

        {"role": "user", "content": f"What is your bid for {product['name']}? (Base Price: ${product['base_price']}) — You currently have {ai_money}$. Give just a number, no sentence no characters just the number!"}
    ]

    if user_money < product['base_price'] and ai_money < product['base_price']:
        print("Both of you cannot buy this product, moving to next round.")
        continue

    if user_money > product['base_price']:
        user_price = float(input("Enter your price for this product: "))
        while user_price<product['base_price'] or user_price > user_money:
            user_price = float(input("Enter a reasonable price for this product:"))
            
    else:
        user_price = -1

    if ai_money > product['base_price']:
        ollama_response = ollama.chat(model="llama3.2:latest", messages=messages)
        ollama_price = float(ollama_response['message']['content'].strip())
        while ollama_price<product['base_price'] or ollama_price > ai_money:
            ollama_response = ollama.chat(model="llama3.2:latest", messages=messages)
            ollama_price = float(ollama_response['message']['content'].strip())
            
    else:
        ollama_price = -1

   

    print(f"You offered {user_price:.2f}$.")
    time.sleep(2)
    print(f"AI vendor offered {ollama_price:.2f}$.")

    if ollama_price > user_price:
        ai_money -= ollama_price
        print("AI vendor buys the product.")
        selected_event = random.choices(events, weights=event_weights, k=1)[0]
        time.sleep(2)
        print(f"Today is {selected_event['name']}.")
        time.sleep(2)
        print(selected_event['description'])

        today_price = ollama_price
        if selected_event['name'] == "High demand day":
            today_price *= 2
        elif selected_event['name'] == "Low demand day":
            today_price /= 2

        selected_clients = random.sample(clients, 3)
        time.sleep(2)
        for i, client in enumerate(selected_clients, 1):
            print(f"{i}. {client['description']}")

        ollama_responseChoice = ollama.chat(
            model="llama3.2:latest",
            messages=[
                {"role": "system", "content": "You are an AI vendor analyzing clients to find who will offer the highest price."
                " Read the descriptions and predict who'll give the highest price.Do NOT assume everyone pays equally — your goal is to **rank them based on likelihood to pay more**. Return only the number 1, 2 or 3."},
                {"role": "user", "content": (
                "Read the 3 client descriptions below and choose the ONE most likely to offer the highest price.\n"
                "⚠️ Respond ONLY with a single number: 1, 2, or 3. DO NOT write anything else.\n\n" +
                "\n".join([f"Client {i}: {client['description']}" for i, client in enumerate(selected_clients, 1)])
                )}
            ]
        )

        ollama_prediction = ollama_responseChoice['message']['content'].strip()
        if ollama_prediction in ["1", "2", "3"]:
            chosen_client = selected_clients[int(ollama_prediction) - 1]
            time.sleep(2)
            print(f"AI predicts Client {ollama_prediction} will offer the highest price.")
            time.sleep(2)
            given_price = chosen_client['offer_percentage'] * today_price
            print(f"AI made a deal of {given_price:.2f}$.")
            time.sleep(2)
            ai_money += given_price
            if selected_event['name'] == "Charity day":
                ai_money -= ai_money * 0.2
            print(f"AI vendor reaches {ai_money:.2f}$.")
        else: 
         
          chosen_client = selected_clients[0]  
          ollama_prediction = "1"
          print("default behavior due to error in prediction")
        
        ai_memory.append({
            "round": round_num,
            "event": selected_event['name'],
            "ai": {
            "bought_for": ollama_price,
            "sold_for": given_price,
            "profit": given_price - ollama_price
               },
            "player": {
            "bought_for": None,
            "sold_for": None,
            "profit": 0,
            "note": "Lost to AI"
              }
          })


    elif user_price > ollama_price:
        user_money -= user_price
        time.sleep(2)
        print("You buy the product.")
        selected_event = random.choices(events, weights=event_weights, k=1)[0]
        time.sleep(2)
        print(f"Today is {selected_event['name']}.")
        time.sleep(2)
        print(selected_event['description'])

        today_price = user_price
        if selected_event['name'] == "High demand day":
            today_price *= 2
        elif selected_event['name'] == "Low demand day":
            today_price /= 2

        selected_clients = random.sample(clients, 3)
        for i, client in enumerate(selected_clients, 1):
            print(f"{i}. {client['description']}")

        chosen_client_number = int(input("Choose the client you want to make the deal with (1, 2, or 3): "))
        if chosen_client_number in [1, 2, 3]:
            chosen_client = selected_clients[chosen_client_number - 1]
            time.sleep(2)
            given_price = chosen_client['offer_percentage'] * today_price
            user_money += given_price
            if selected_event['name'] == "Charity day":
                user_money -= user_money * 0.2
            print(f"You made the deal for {given_price:.2f}$.")
            time.sleep(2)
            print(f"You reach {user_money:.2f}$.")
            ai_memory.append({
            "round": round_num,
            "event": selected_event['name'],
            "ai": {
            "bought_for": None,
            "sold_for": None,
            "profit": 0,
            "note": "Lost to player"
             },
            "player": {
            "bought_for": user_price,
            "sold_for": given_price,
            "profit": given_price - user_price
    }
})


    elif user_price == ollama_price and user_price != -1:
        time.sleep(2)
        print("Same offer, try again.")
        user_price = float(input("Enter your new price for this product: "))
        while user_price > user_money or user_price<product['base_price']:
         user_price = float(input("Enter a reasonable price for this product : "))
         

        ollama_response = ollama.chat(model="llama3.2:latest", messages=messages)
        ollama_price = float(ollama_response['message']['content'].strip())
        while ollama_price<product['base_price'] or ollama_price > ai_money:
          ollama_response = ollama.chat(model="llama3.2:latest", messages=messages)
          ollama_price = float(ollama_response['message']['content'].strip())
         

        time.sleep(2)
        print(f"You offered {user_price:.2f}$.")
        time.sleep(2)
        print(f"AI vendor offered {ollama_price:.2f}$.")

# Final results
print("\n===== GAME OVER =====")
if user_money > ai_money:
    time.sleep(2)
    print(f"You won! You made {user_money:.2f}$ and AI vendor made {ai_money:.2f}$.")
elif ai_money > user_money:
    time.sleep(2)
    print(f"AI won! You made {user_money:.2f}$ and AI vendor made {ai_money:.2f}$.")
else:
    print(f"Fair play! Both of you made {user_money:.2f}$.")


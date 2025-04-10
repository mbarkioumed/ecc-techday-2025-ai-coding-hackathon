import random
import time
import ollama
from data import products, clients, events
from functions import summarize_ai_memory,calculate_number_of_clients

user_money = 300
ai_money = 300
event_weights = [0.15, 0.55, 0.15, 0.15]
ai_memory = []




# Pick 5 random products for this round
selected_products = random.sample(products, 5)

# round execution
for round_num, product in enumerate(selected_products, 1):
    print(f"\n==== ROUND {round_num} ====")
    print(f"You have {user_money:.2f}$.")
    print(f"AI Vendor has {ai_money:.2f}$.")
    print(f"\n🛒 Product: {product['name']} (Base Price: {product['base_price']}$)")

   # summarizing memory of previous rounds 
    memory_summary = summarize_ai_memory(ai_memory)

   #  the messages that we'll prompt the llm with contain the rounds' history + game strategy 

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
- Some days cause you to lose money (like 'Charity Day'or 'Low demand day").
- If you overspend, you may not profit.
-Bidding high may help you win, but it will likely result in fewer clients, reducing your potential profits.

- You want to win by the final round.

Respond with a **single numeric value** — your bid.
"""},

        {"role": "user", "content": f"What is your bid for {product['name']}? (Base Price: ${product['base_price']}) — You currently have {ai_money}$. Give just a number, no sentence no characters just the number!"}
    ]
    


   #  If the user and the ai don't have enough money to play this round, we skip it
    if user_money < product['base_price'] and ai_money < product['base_price']:
        print("Both of you cannot buy this product, moving to next round.")
        continue
    

   #  checks if user can buy the product and offers a price higher than base price and lower than his earnings
    if user_money > product['base_price']:
        user_price = float(input("Enter your price for this product: "))
        while user_price<product['base_price'] or user_price > user_money:
            user_price = float(input("Enter a reasonable price for this product:"))
    else:
        user_price = -1
            
   
   
   #  checks if ai can buy the product and offers a price higher than base price and lower than its earnings

    if ai_money > product['base_price']:
        ollama_response = ollama.chat(model="llama3.2:latest", messages=messages)
        ollama_price = float(ollama_response['message']['content'].strip())
        while ollama_price<product['base_price'] or ollama_price > ai_money:
            ollama_response = ollama.chat(model="llama3.2:latest", messages=messages)
            ollama_price = float(ollama_response['message']['content'].strip())
            
    else:
        ollama_price = -1
   # Making sure the two offers are different

    if user_price == ollama_price and user_price != -1:
        time.sleep(2)
        print("Both players offered the same price , try again.")
        user_price = float(input("Enter your new price for this product: "))
        while user_price > user_money or user_price<product['base_price']:
         user_price = float(input("Enter a reasonable price for this product : ")) 
         

        ollama_response = ollama.chat(model="llama3.2:latest", messages=messages)
        ollama_price = float(ollama_response['message']['content'].strip())
        while ollama_price<product['base_price'] or ollama_price > ai_money:
          ollama_response = ollama.chat(model="llama3.2:latest", messages=messages)
          ollama_price = float(ollama_response['message']['content'].strip())
         


    print(f"You offered {user_price:.2f}$.")
    time.sleep(2)
    print(f"AI vendor offered {ollama_price:.2f}$.")
    


   # if ai offers more than user , it plays the round
    if ollama_price > user_price:
        ai_money -= ollama_price
        print("AI vendor buys the product.")
      #   selecting randomly an event for the day
        selected_event = random.choices(events, weights=event_weights, k=1)[0]
        time.sleep(2)
        print(f"Today is {selected_event['name']}.")
        time.sleep(2)
        print(selected_event['description'])

        today_price = ollama_price
      #   the number of clients is determined by the marge between the product's base price and resale price
        selected_clients = random.sample(clients, calculate_number_of_clients(product["base_price"],today_price))
      #   determining the event's effect on resale price , events have no effect over the number of clients !
        if selected_event['name'] == "High demand day":
            today_price *= 2
        elif selected_event['name'] == "Low demand day":
            today_price /= 2

        time.sleep(2)
        for i, client in enumerate(selected_clients, 1):
            print(f"{i}. {client['description']}")
        if len(selected_clients)==1 :
            chosen_client = selected_clients[0]
            ollama_prediction = "1"


        else :
             ollama_responseChoice = ollama.chat(
             model="llama3.2:latest",
             messages=[
                {"role": "system", "content": "You are an AI vendor analyzing clients to find who will offer the highest price."
                " Read the descriptions and predict who'll give the highest price.Do NOT assume everyone pays equally — your goal is to **rank them based on likelihood to pay more**. Return only the number 1, 2 or 3."},
                {"role": "user", "content": (
                "Read the 3 client descriptions below and choose the ONE most likely to offer the highest price.\n"
                "⚠️ Respond ONLY with the number of the client you have chosen. DO NOT write anything else.\n\n" +
                "\n".join([f"Client {i}: {client['description']}" for i, client in enumerate(selected_clients, 1)])
                )}
            ]
        )

             ollama_prediction = ollama_responseChoice['message']['content'].strip()
             if ollama_prediction in range(1,len(selected_clients)+1):
                chosen_client = selected_clients[int(ollama_prediction) - 1]
             else: 
         # attributing default behavior in case of a wrong format prediction
               chosen_client = selected_clients[0]  
               ollama_prediction = "1"
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
        
      #   updating ai_memory 
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




   # If user offers more than AI, it plays the round
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
        
        selected_clients = random.sample(clients, calculate_number_of_clients(product["base_price"],today_price))
        # Adjusting price based on event
        if selected_event['name'] == "High demand day":
            today_price *= 2
        elif selected_event['name'] == "Low demand day":
            today_price /= 2

        for i, client in enumerate(selected_clients, 1):
            print(f"{i}. {client['description']}")
        if len(selected_clients)==1:
            chosen_client_number=1
        else :
          chosen_client_number = int(input("Enter the number of the client you want to make the deal with : "))
          # Ensuring valid input for client selection
          while chosen_client_number not in range(1,len(selected_clients)+1):
              chosen_client_number = int(input("Enter the number of the client you want to make the deal with : "))

        
       
        chosen_client = selected_clients[chosen_client_number - 1]
        time.sleep(2)
        given_price = chosen_client['offer_percentage'] * today_price
        user_money += given_price
        if selected_event['name'] == "Charity day":
            user_money -= user_money * 0.2
        print(f"You made the deal for {given_price:.2f}$.")
        time.sleep(2)
        print(f"You reach {user_money:.2f}$.")
        # Updating memory for ai
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


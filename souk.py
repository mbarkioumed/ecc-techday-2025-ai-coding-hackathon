import random
import time
import ollama
from data import products, clients, events

user_money = 300
ai_money = 300
event_weights = [0.2, 0.5, 0.15, 0.15]


# Pick 5 random products for this round
selected_products = random.sample(products, 5)
# round execution
for round_num,product in enumerate(selected_products,1):
    
    print(f"====ROUND {round_num}====")
    print(f"You have {user_money}$.")
    print(f"AI Vendor has {ai_money}$.")
    print(f"\n🛒 Product: {product['name']} (Base Price: {product['base_price']})")
    # AI or user giving price while making sure they can afford the product 
    if user_money>product['base_price']:
       user_price = float(input("Enter your price for this product: "))
    else : 
       user_price=-1
    while user_price>user_money:
       user_price = float(input("Enter your price for this product: "))
    if ai_money>product['base_price']:
        ollama_response = ollama.chat(
        model="llama3.2:latest", 
        messages=[
        {"role": "system", "content": f"You are an AI vendor trying to buy a product to sell it later, to buy the product you should give a higher price than the base price of the product and than the one given by the competing vendor. You have this amount of money ${ai_money} you cannot give a price superior to the amount of money you have.Please give me only the numeric price.No symbol no text just the number."},
        {"role": "user", "content": f"What price are you willing to give for {product['name']} (base price ${product['base_price']})?You have this amount of money ${ai_money} you cannot give a price superior to the amount of money you have.Please give me only the numeric price.No symbol no text just the number.Take into consideration the fact that you can lose more by giving a very high price due to events that may occur like charity day or low demand day, or being tricked by a client giving you a lower price."}
        ]
        )
        ollama_price = float(ollama_response['message']['content'].strip())
    else:
       ollama_price=-1
      

   

    

    while ollama_price>ai_money:
       ollama_response = ollama.chat(
       model="llama3.2:latest", 
       messages=[
        {"role": "system", "content": f"You are an AI vendor trying to buy a product to sell it later, to buy the product you should give a higher price than the base price of the product and than the one given by the competing vendor. You have this amount of money ${ai_money} you cannot give a price superior to the amount of money you have.Please give me only the numeric price.No symbol no text just the number."},
        {"role": "user", "content": f"What price are you willing to give for {product['name']} (base price ${product['base_price']})?You have this amount of money ${ai_money} you cannot give a price superior to the amount of money you have.Please give me only the numeric price.No symbol no text just the number.Take into consideration the fact that you can lose more by giving a very high price due to events that may occur like charity day or low demand day, or being tricked by a client giving you a lower price."}
       ]
       )

   


       ollama_price = float(ollama_response['message']['content'].strip())
       
   
    print(f"You offered {user_price:.2f}$.")
    time.sleep(2)
    print(f"AI vendor offered {ollama_price:.2f}$.")
   
    


     #  buying product
    if ollama_price>user_price :
        ai_money-=ollama_price
        print("AI vendor buys the product.")
         # Today's event
        selected_event = random.choices(events, weights=event_weights, k=1)[0]
        time.sleep(2)
        print(f"Today is {selected_event['name']}.")
        time.sleep(2)
        print(selected_event['description'])
        today_price=ollama_price
        if selected_event['name']=="High demand day":
           today_price=ollama_price*2
        elif selected_event['name']=="Low demand day":
           today_price=ollama_price/2
        elif selected_event['name']=="Simple day":
           today_price=ollama_price
        
        # displaying clients
        selected_clients = random.sample(clients, 3)
        time.sleep(2)
        for i, client in enumerate(selected_clients, 1):
            print(f"{i}. {client['description']}")
        # AI choosing client
        ollama_responseChoice = ollama.chat(
        model="llama3.2:latest",
        messages=[
            {"role": "system", "content": "You are an AI vendor analyzing clients to find who will offer the highest price.Read the descriptions and predict who'll give the highest price.Return only his number 1, 2 or 3 no text no characters."},
            {"role": "user", "content": 
                "\n".join([f"Client {i}: {client['description']}" for i, client in enumerate(selected_clients, 1)]) + 
                "\nWho will offer the highest price? Respond with the client number (1, 2, or 3)."}
        ]
        )

    #  Interpret Ollama's response
        ollama_prediction = ollama_responseChoice['message']['content'].strip()  # Ollama's response should be "1", "2", or "3"

    #  Check Ollama's prediction
        if ollama_prediction in ["1", "2", "3"]:
         chosen_client = selected_clients[int(ollama_prediction) - 1]
         time.sleep(2)
         print(f"AI predicts Client {ollama_prediction} will offer the highest price.")
         time.sleep(2)
         givenPrice=chosen_client['offer_percentage']*today_price
         print(f"AI made a deal of {givenPrice:.2f}$.") 
         time.sleep(2)
         ai_money+=givenPrice 
         if selected_event['name']=="Charity day":
            ai_money-=ai_money*0.2
         print(f"AI vendor reaches {ai_money:.2f}$.")
        
    elif ollama_price<user_price : 
       user_money-=user_price
       time.sleep(2)
       print("You buy the product.")
       time.sleep(2)
     # Today's event
       selected_event = random.choices(events, weights=event_weights, k=1)[0]
       time.sleep(2)
       print(f"Today is {selected_event['name']}.")
       time.sleep(2)
       print(selected_event['description'])
       if selected_event['name']=="High demand day":
           today_price=ollama_price*2
       elif selected_event['name']=="Low demand day":
           today_price=ollama_price/2
       elif selected_event['name']=="Simple day":
           today_price=ollama_price
       
           
       
        # displaying clients
       selected_clients = random.sample(clients, 3)
       for i, client in enumerate(selected_clients, 1):
            print(f"{i}. {client['description']}")
    #    Choose client 
       chosen_client_number=int(input("Choose the client you want to make the deal with 1, 2 or 3 :"))
       if chosen_client_number in [1,2,3] : 
          chosen_client=selected_clients[chosen_client_number-1]
       time.sleep(2)
       givenPrice=chosen_client['offer_percentage']*today_price
       user_money+=givenPrice
       if selected_event['name']=="Charity day":
            user_money-=user_money*0.2

       print(f"You made the deal for {givenPrice:.2f}$.")
       time.sleep(2)
       print(f"You reach {user_money:.2f}$.")
    elif user_price==ollama_price and user_price!=-1 :
       time.sleep(2)
       print("Same offer , try again.")
       user_price = float(input("Enter your price for this product: "))
       ollama_response = ollama.chat(
       model="llama3.2:latest", 
       messages=[
        {"role": "system", "content": f"You are an AI vendor trying to buy a product to sell it later, to buy the product you should give a higher price than the base price of the product and than the one given by the competing vendor. You have this amount of money ${ai_money}.Please give me only the numeric price.No symbol no text just the number."},
        {"role": "user", "content": f"What price are you willing to give for {product['name']} (base price ${product['base_price']})?"}
       ]
        )


       ollama_price = float(ollama_response['message']['content'].strip())
       time.sleep(2)
       print(f"You offered {user_price:.2f}$.")
       time.sleep(2)
       print(f"AI vendor offered {ollama_price:.2f}$.")
if user_money>ai_money:
   time.sleep(2)
   print(f"You won! You made {user_money:.2f}$ and AI vendor made {ai_money:.2f}$. ")
elif ai_money>user_money:
   time.sleep(2)
   print(f"AI won! You made {user_money:.2f}$ and AI vendor made {ai_money:.2f}$.")
else : 
   print(f"fair play! both of you made {user_money:.2f}$.")
       

   


       

        

    




import random
import time

blackjack_strategy = {
    "hard": {
        (5, 6, 7): {2: "H", 3: "H", 4: "H", 5: "H", 6: "H", 7: "H", 8: "H", 9: "H", 10: "H", "A": "H"},
        (8,): {2: "H", 3: "H", 4: "H", 5: "H", 6: "H", 7: "H", 8: "H", 9: "H", 10: "H", "A": "H"},
        (9,): {2: "H", 3: "D", 4: "D", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", "A": "H"},
        (10,): {2: "D", 3: "D", 4: "D", 5: "D", 6: "D", 7: "D", 8: "D", 9: "D", 10: "H", "A": "H"},
        (11,): {2: "D", 3: "D", 4: "D", 5: "D", 6: "D", 7: "D", 8: "D", 9: "D", 10: "D", "A": "D"},
        (12,): {2: "H", 3: "H", 4: "S", 5: "S", 6: "S", 7: "H", 8: "H", 9: "H", 10: "H", "A": "H"},
        (13, 14): {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "H", 8: "H", 9: "H", 10: "H", "A": "H"},
        (15,): {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "H", 8: "H", 9: "H", 10: "R", "A": "H"},
        (16,): {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "H", 8: "H", 9: "R", 10: "R", "A": "R"},
        (17,): {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", "A": "S"},
    },
    "soft": {
        ("A,2", "A,3"): {2: "H", 3: "H", 4: "D", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", "A": "H"},
        ("A,4", "A,5"): {2: "H", 3: "H", 4: "D", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", "A": "H"},
        ("A,6",): {2: "H", 3: "D", 4: "D", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", "A": "H"},
        ("A,7",): {2: "S", 3: "DS", 4: "DS", 5: "DS", 6: "DS", 7: "S", 8: "H", 9: "H", 10: "H", "A": "H"},
        ("A,8", "A,9"): {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", "A": "S"},
    }
}

FACE_CARDS = {'J': 10, 'Q': 10, 'K': 10, 'A': 11}
VALID_ACTIONS = {'h': 'hit', 's': 'stand', 'd': 'double'}
DELAY = 1.5

class Card:
    __slots__ = ['suit', 'value']
    
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __str__(self):
        return f"{self.value} of {self.suit}"

class Deck:
    def __init__(self):
        self.cards = [Card(s, v) for s in ['Hearts', 'Diamonds', 'Spades', 'Clubs'] 
                     for v in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']]
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop() if self.cards else None

def delay_print(message):
    print(message)
    time.sleep(DELAY)

def calculate_hand(hand):
    value = 0
    aces = 0
    
    for card in hand:
        if card.value in FACE_CARDS:
            if card.value == 'A':
                aces += 1
            else:
                value += 10
        else:
            value += int(card.value)
    
    for _ in range(aces):
        value += 11 if value + 11 <= 21 else 1
    
    return value

def get_strategy_advice(player_hand, dealer_card):
    dealer_value = FACE_CARDS.get(dealer_card.value, int(dealer_card.value))
    total = calculate_hand(player_hand)
    
    # Check for soft hands first
    if any(card.value == 'A' for card in player_hand) and total <= 21:
        non_ace = sum(FACE_CARDS.get(c.value, int(c.value)) for c in player_hand if c.value != 'A')
        soft_key = f"A,{non_ace}"
        for hands, actions in blackjack_strategy["soft"].items():
            if soft_key in hands:
                return actions[dealer_value]
    
    # Handle hard hands
    for totals, actions in blackjack_strategy["hard"].items():
        if total in totals:
            return actions[dealer_value]
    
    return 'S'

def play_blackjack():
    deck = Deck()
    player_money = 1000

    while player_money > 0:
        delay_print(f"\nYour money: ${player_money}")
        try:
            bet = int(input("Enter your bet (0 to quit): "))
            if bet == 0:
                break
            if bet > player_money:
                delay_print("Insufficient funds!")
                continue
        except ValueError:
            delay_print("Invalid bet amount!")
            continue

        player_hand = [deck.deal(), deck.deal()]
        dealer_hand = [deck.deal(), deck.deal()]
        
        delay_print(f"\nDealer shows: {dealer_hand[1]}")
        
        # Player's turn
        while True:
            current_value = calculate_hand(player_hand)
            delay_print(f"\nYour hand: {', '.join(str(card) for card in player_hand)}")
            delay_print(f"Hand value: {current_value}")
            
            if current_value > 21:
                delay_print("Bust!")
                break
                
            recommended_play = get_strategy_advice(player_hand, dealer_hand[1])
            delay_print(f"Strategy recommends: {recommended_play}")
            
            options = "(h)it, (s)tand" + (", (d)ouble" if len(player_hand) == 2 and bet * 2 <= player_money else "")
            action = input(f"What would you like to do? {options}: ").lower()
            
            if action == 'h':
                player_hand.append(deck.deal())
            elif action == 'd' and len(player_hand) == 2 and bet * 2 <= player_money:
                bet *= 2
                player_hand.append(deck.deal())
                delay_print(f"New card: {player_hand[-1]}")
                break
            elif action == 's':
                break
            else:
                delay_print("Invalid action!")
                continue

        # Dealer's turn
        delay_print("\nDealer's hand: " + ', '.join(str(card) for card in dealer_hand))
        while calculate_hand(dealer_hand) < 17:
            dealer_hand.append(deck.deal())
            delay_print("Dealer draws: " + str(dealer_hand[-1]))
        
        # Determine winner
        player_total = calculate_hand(player_hand)
        dealer_total = calculate_hand(dealer_hand)
        
        delay_print(f"Your total: {player_total}")
        delay_print(f"Dealer's total: {dealer_total}")
        
        if player_total > 21:
            delay_print("Player busts! Lost bet.")
            player_money -= bet
        elif dealer_total > 21:
            delay_print("Dealer busts! Won bet!")
            player_money += bet
        elif player_total > dealer_total:
            delay_print("Player wins!")
            player_money += bet
        elif player_total < dealer_total:
            delay_print("Dealer wins!")
            player_money -= bet
        else:
            delay_print("Push!")

    delay_print(f"\nGame over! Final money: ${player_money}")

if __name__ == "__main__":
    play_blackjack()
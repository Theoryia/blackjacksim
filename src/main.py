import random
import time
import csv

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
    def __init__(self, num_decks=6):  # Default to 6 decks like most casinos
        self.cards = []
        for _ in range(num_decks):
            self.cards.extend([Card(s, v) for s in ['Hearts', 'Diamonds', 'Spades', 'Clubs'] 
                             for v in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']])
        random.shuffle(self.cards)
        self.initial_size = len(self.cards)  # Track total cards for reshuffling
    
    def deal(self):
        # Reshuffle when about 75% of cards have been dealt
        if len(self.cards) < (self.initial_size * 0.25):
            self.__init__()
        return self.cards.pop()

def delay_print(message):
    print(message)
    time.sleep(DELAY)

def calculate_hand(hand):
    try:
        value = 0
        aces = 0
        
        for card in hand:
            if card.value in ['J', 'Q', 'K']:
                value += 10
            elif card.value == 'A':
                aces += 1
            else:
                value += int(card.value)
        
        for _ in range(aces):
            value += 11 if value + 11 <= 21 else 1
        
        return value
    except Exception as e:
        #print(f"Error in calculate_hand: {str(e)}")
        #print(f"Problem hand: {[str(c) for c in hand]}")
        raise

def get_strategy_advice(player_hand, dealer_card):
    # Convert dealer's card to strategy format
    if dealer_card.value in ['J', 'Q', 'K']:
        dealer_value = 10
    elif dealer_card.value == 'A':
        dealer_value = 'A'
    else:
        dealer_value = int(dealer_card.value)
    
    total = calculate_hand(player_hand)
    
    # Quick return for bust or high values
    if total > 21:
        return 'S'
    if total >= 17:
        return 'S'
    
    # Check for soft hands
    has_ace = any(card.value == 'A' for card in player_hand)
    if has_ace and total <= 21:
        non_ace = sum(10 if card.value in ['J', 'Q', 'K'] 
                     else int(card.value) if card.value != 'A' 
                     else 0 for card in player_hand)
        soft_key = f"A,{non_ace}"
        for hands, actions in blackjack_strategy["soft"].items():
            if soft_key in hands:
                return actions[dealer_value]
    
    # Handle hard hands
    for totals, actions in blackjack_strategy["hard"].items():
        if total in totals:
            return actions[dealer_value]
    
    return 'S'

def simulate_blackjack(iterations, bet_amount):
    deck = Deck()
    running_money = 10000
    wins = losses = pushes = 0
    
    with open('blackjack_results.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Round', 'Result', 'Running_Money', 'Debug'])
        writer.writeheader()
        
        for round_num in range(1, iterations + 1):
            try:
                # Add money check at start of round
                if running_money < bet_amount:
                    print(f"\nOut of money (${running_money}) - stopping at round {round_num}")
                    break
                
                # Check deck size and reshuffle
                #print(f"Checking deck size: {len(deck.cards)} cards")
                if len(deck.cards) < 20:
                    #print(f"Reshuffling deck at {len(deck.cards)} cards")
                    deck = Deck()
                    #print(f"New deck created with {len(deck.cards)} cards")
                
                #print("Dealing initial hands...")
                player_hand = [deck.deal(), deck.deal()]
                dealer_hand = [deck.deal(), deck.deal()]
                #print(f"Player hand: {[str(c) for c in player_hand]}")
                #print(f"Dealer hand: {[str(c) for c in dealer_hand]}")
                
                current_bet = bet_amount
                debug_info = []
                
                #print("\nStarting player's turn...")
                while True:
                    current_value = calculate_hand(player_hand)
                    #print(f"Current player hand value: {current_value}")
                    
                    if current_value > 21:
                        #print("Player bust!")
                        break
                    
                    action = get_strategy_advice(player_hand, dealer_hand[1])
                    #print(f"Strategy suggests: {action}")
                    
                    if action in ['S', 'R']:
                        #print("Standing/Surrendering")
                        break
                    elif action == 'D':  # Changed this condition
                        if len(player_hand) == 2:
                            new_card = deck.deal()
                            #print(f"Doubling down, drew: {new_card}")
                            player_hand.append(new_card)
                            current_bet *= 2
                            break
                        else:
                            # If we can't double, we should hit instead
                            #print("Can't double after hit, hitting instead")
                            new_card = deck.deal()
                            #print(f"Hitting, drew: {new_card}")
                            player_hand.append(new_card)
                    elif action == 'H':
                        new_card = deck.deal()
                        #print(f"Hitting, drew: {new_card}")
                        player_hand.append(new_card)
                
                #print("\nStarting dealer's turn...")
                player_total = calculate_hand(player_hand)
                dealer_total = calculate_hand(dealer_hand)
                #print(f"Initial dealer total: {dealer_total}")
                
                if player_total <= 21:
                    while calculate_hand(dealer_hand) < 17:
                        new_card = deck.deal()
                        #print(f"Dealer draws: {new_card}")
                        dealer_hand.append(new_card)
                        #print(f"New dealer total: {calculate_hand(dealer_hand)}")
                
                #print("\nDetermining result...")
                dealer_total = calculate_hand(dealer_hand)
                
                # Determine result
                if player_total > 21:
                    result = "Loss"
                    running_money -= current_bet
                    losses += 1
                elif dealer_total > 21:
                    result = "Win"
                    running_money += current_bet
                    wins += 1
                elif player_total > dealer_total:
                    result = "Win"
                    running_money += current_bet
                    wins += 1
                elif player_total < dealer_total:
                    result = "Loss"
                    running_money -= current_bet
                    losses += 1
                else:
                    result = "Push"
                    pushes += 1
                
                debug_info.append(f"Result: {result}, Money: ${running_money}")
                
                writer.writerow({
                    'Round': round_num,
                    'Result': result,
                    'Running_Money': running_money,
                    'Debug': ' | '.join(debug_info)
                })
                
                # Changed to #print every round instead of every 10
                #print(f"\nRound {round_num}:")
                #print(f"Current balance: ${running_money}")
                #print(f"Hand details: {' | '.join(debug_info)}")
                #print("-" * 80)
            
            except Exception as e:
                #print(f"\nError on round {round_num}:")
                print(f"Last debug info: {' | '.join(debug_info)}")
                print(f"Error message: {str(e)}")
                return wins, losses, pushes, running_money
    
    print("\nSimulation complete!")
    return wins, losses, pushes, running_money

if __name__ == "__main__":
    iterations = int(input("Enter number of hands to simulate: "))
    bet_amount = int(input("Enter bet amount per hand: "))
    initial_money = 1000  # Define initial money
    
    wins, losses, pushes, total_money = simulate_blackjack(iterations, bet_amount)
    
    hands_played = wins + losses + pushes  # Calculate actual hands played
    
    print("\nSimulation Results:")
    print(f"Hands Played: {hands_played} of {iterations}")
    print(f"Wins: {wins} ({(wins/hands_played)*100:.1f}%)")
    print(f"Losses: {losses} ({(losses/hands_played)*100:.1f}%)")
    print(f"Pushes: {pushes} ({(pushes/hands_played)*100:.1f}%)")
    print(f"Initial Money: ${initial_money}")
    print(f"Final Money: ${total_money}")
    print(f"Net Profit/Loss: ${total_money - initial_money}")
    print(f"Return Rate per Round: {((total_money - initial_money)/(bet_amount*hands_played))*100:.2f}%")
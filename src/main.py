import random
import time
import csv
import hashlib
import json
import datetime
import os

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

def simulate_blackjack(iterations, bet_amount, initial_money):
    deck = Deck()
    running_money = initial_money
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
                            # Check if we have enough money to double down
                            if running_money >= bet_amount * 2:
                                new_card = deck.deal()
                                player_hand.append(new_card)
                                current_bet *= 2
                                break
                            else:
                                # Not enough money to double, just hit instead
                                new_card = deck.deal()
                                player_hand.append(new_card)
                        else:
                            # Can't double after hit, hit instead
                            new_card = deck.deal()
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
                    # Only subtract what we have available
                    if running_money >= current_bet:
                        running_money -= current_bet
                    else:
                        running_money = 0
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
                    # Only subtract what we have available
                    if running_money >= current_bet:
                        running_money -= current_bet
                    else:
                        running_money = 0
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

def get_strategy_hash():
    """Generate a short hash of the blackjack strategy to use as identifier"""
    # Create a serializable copy of the strategy
    serializable_strategy = {
        "hard": {},
        "soft": {}
    }
    
    # Convert hard hand tuple keys to strings and dealer card values to strings
    for key_tuple, actions in blackjack_strategy["hard"].items():
        key_str = str(key_tuple)
        serializable_actions = {}
        for dealer_card, action in actions.items():
            serializable_actions[str(dealer_card)] = action
        serializable_strategy["hard"][key_str] = serializable_actions
    
    # Convert soft hand tuple keys to strings and dealer card values to strings
    for key_tuple, actions in blackjack_strategy["soft"].items():
        key_str = str(key_tuple)
        serializable_actions = {}
        for dealer_card, action in actions.items():
            serializable_actions[str(dealer_card)] = action
        serializable_strategy["soft"][key_str] = serializable_actions
    
    # Now serialize and hash
    strategy_str = json.dumps(serializable_strategy, sort_keys=True)
    return hashlib.md5(strategy_str.encode()).hexdigest()[:8]

def update_historical_results(iterations, bet_amount, wins, losses, pushes, initial_money, final_money):
    """Update historical results CSV file for the current strategy"""
    strategy_id = get_strategy_hash()
    filename = f"strategy_{strategy_id}_games.csv"
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['Iterations', 'Hands_Played', 'Bet_Amount', 'Wins', 
                     'Losses', 'Pushes', 'Initial_Money', 'Final_Money', 'Profit', 
                     'Win_Rate', 'Dealer_Win_Rate', 'Return_Rate', 'House_Edge']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        hands_played = wins + losses + pushes
        win_rate = (wins / hands_played) * 100 if hands_played > 0 else 0
        
        # Calculate dealer win rate (excluding pushes)
        dealer_win_rate = (losses / (wins + losses)) * 100 if (wins + losses) > 0 else 0
        
        # Fix return rate calculation - this should be profit per hand as a percentage of bet
        profit = final_money - initial_money
        return_rate = (profit / (bet_amount * hands_played)) * 100 if hands_played > 0 else 0
        
        # House edge is the negative of return rate (casino's advantage)
        house_edge = -return_rate
        
        writer.writerow({
            'Iterations': iterations,
            'Hands_Played': hands_played,
            'Bet_Amount': bet_amount,
            'Wins': wins,
            'Losses': losses,
            'Pushes': pushes,
            'Initial_Money': initial_money,
            'Final_Money': final_money,
            'Profit': profit,
            'Win_Rate': f"{win_rate:.1f}%",
            'Dealer_Win_Rate': f"{dealer_win_rate:.1f}%",
            'Return_Rate': f"{return_rate:.2f}%",
            'House_Edge': f"{house_edge:.2f}%"
        })

if __name__ == "__main__":
    num_games = int(input("Enter number of games to run: "))
    iterations = int(input("Enter number of hands to simulate for each game: "))
    bet_amount = int(input("Enter bet amount per hand: $"))
    initial_money = int(input("Enter starting bankroll for each game: $"))
    
    print("\nStarting simulation...")
    print(f"Running {num_games} games with: {iterations} hands, ${bet_amount} bet, ${initial_money} bankroll")
    
    for game_num in range(1, num_games + 1):
        print(f"\n--- GAME {game_num} OF {num_games} ---")
        
        wins, losses, pushes, total_money = simulate_blackjack(iterations, bet_amount, initial_money)
        
        hands_played = wins + losses + pushes
        print(f"\nGame {game_num} Results:")
        print(f"Hands Played: {hands_played} of {iterations}")
        print(f"Wins: {wins} ({(wins/hands_played)*100:.1f}%)")
        print(f"Losses: {losses} ({(losses/hands_played)*100:.1f}%)")
        print(f"Pushes: {pushes} ({(pushes/hands_played)*100:.1f}%)")
        print(f"Initial Money: ${initial_money}")
        print(f"Final Money: ${total_money}")
        print(f"Net Profit/Loss: ${total_money - initial_money}")
        print(f"Return Rate: {((total_money - initial_money)/(bet_amount*hands_played))*100:.2f}%")
        
        # Update the historical results CSV
        update_historical_results(iterations, bet_amount, wins, losses, pushes, initial_money, total_money)
    
    print("\nAll games completed!")
    print(f"Results saved to strategy_{get_strategy_hash()}_games.csv")
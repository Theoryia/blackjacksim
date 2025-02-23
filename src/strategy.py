import pandas as pd

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

def get_strategy_advice(player_hand, dealer_card):
    """Get strategy advice for a given hand"""
    # Convert dealer's card value
    if dealer_card.value in ['J', 'Q', 'K']:
        dealer_value = 10
    elif dealer_card.value == 'A':
        dealer_value = 'A'
    else:
        dealer_value = int(dealer_card.value)

    # Calculate total and check for soft hands
    total = 0
    has_ace = False
    for card in player_hand:
        if card.value == 'A':
            has_ace = True
        elif card.value in ['J', 'Q', 'K']:
            total += 10
        else:
            total += int(card.value)

    # Handle soft hands
    if has_ace and total + 11 <= 21:
        soft_key = f"A,{total}"
        for hands, actions in blackjack_strategy["soft"].items():
            if soft_key in hands:
                return actions[dealer_value]

    # Handle hard hands
    total = sum([10 if c.value in ['J', 'Q', 'K'] else 
                 11 if c.value == 'A' else 
                 int(c.value) for c in player_hand])
    for totals, actions in blackjack_strategy["hard"].items():
        if total in totals:
            return actions[dealer_value]
    
    return 'S'  # Default to stand if no strategy found

def explain_strategy(action):
    """Explain what a strategy action means"""
    explanations = {
        'H': 'Hit - Take another card',
        'S': 'Stand - Keep your current hand',
        'D': 'Double Down - Double your bet and take one more card',
        'R': 'Surrender - Give up half your bet and end hand',
        'DS': 'Double if allowed, otherwise Stand'
    }
    return explanations.get(action, 'Unknown action')


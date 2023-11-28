# Fonction pour simuler une transaction d'achat
def simulate_buy(ticker, data_with_indicators):
    entry_price = data_with_indicators['Open'].iloc[-1]
    quantity = 10  # Vous pouvez ajuster la quantité selon votre stratégie
    return entry_price, quantity

# Fonction pour simuler une transaction de vente
def simulate_sell(ticker, data_with_indicators):
    exit_price = data_with_indicators['Close'].iloc[-1]
    return exit_price
import tkinter as tk
from analysis import analyze_tickers, get_stock_data, calculate_technical_indicators
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import time

# Initialisez votre historique des trades
trade_history = []

# Créez une fenêtre Tkinter
root = tk.Tk()
root.title("Live Trade Analysis")

# Créez une fonction pour afficher les graphiques en temps réel
def show_live_trade_charts():
    plt.figure(figsize=(15, 8))
    plt.suptitle("Live Trade Charts", fontsize=16)

    for i, (ticker, chart_data) in enumerate(active_trade_charts.items()):
        plt.subplot(2, 2, i + 1)
        plt.title(f"{ticker} Trade")
        plt.plot(chart_data['Timestamp'], chart_data['Close'], label='Close Price')
        plt.scatter(chart_data['Entry Timestamp'], chart_data['Entry Price'], color='green', label='Entry Price', marker='o', s=100)
        if chart_data['Exit Timestamp'] is not None:
            plt.scatter(chart_data['Exit Timestamp'], chart_data['Exit Price'], color='red', label='Exit Price', marker='o', s=100)
        plt.legend()

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # Affichez les graphiques dans la fenêtre Tkinter
    canvas = FigureCanvasTkAgg(plt.gcf(), master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=0)

# Fonction pour simuler une transaction d'achat
def simulate_buy(ticker, data_with_indicators):
    entry_price = data_with_indicators['Open'].iloc[-1]
    quantity = 10  # Vous pouvez ajuster la quantité selon votre stratégie
    return entry_price, quantity

# Fonction pour simuler une transaction de vente
def simulate_sell(ticker, data_with_indicators):
    exit_price = data_with_indicators['Close'].iloc[-1]
    return exit_price

# Fonction pour mettre à jour les graphiques en temps réel
def update_live_trade_charts():
    while True:
        # Utiliser des dates plus récentes ou des données en temps réel
        potential_stocks = analyze_tickers()

        for ticker, reason in potential_stocks:
            print(f"Trader should consider: {ticker} because {reason}")

            # Récupérer les données pour le ticker
            data = get_stock_data(ticker)

            # Calculer les indicateurs techniques
            data_with_indicators = calculate_technical_indicators(data)

            # Simuler une transaction d'achat
            entry_price, quantity = simulate_buy(ticker, data_with_indicators)

            # Enregistrez les données du trade en cours
            if ticker not in active_trade_charts:
                active_trade_charts[ticker] = {
                    'Timestamp': [],
                    'Close': [],
                    'Entry Timestamp': [],
                    'Entry Price': [],
                    'Exit Timestamp': None,
                    'Exit Price': None
                }

            active_trade_charts[ticker]['Timestamp'].append(data_with_indicators.index[-1])
            active_trade_charts[ticker]['Close'].append(data_with_indicators['Close'].iloc[-1])
            active_trade_charts[ticker]['Entry Timestamp'].append(data_with_indicators.index[-1])

            # Attendre jusqu'à ce que le trade soit terminé (simulons 5 secondes)
            time.sleep(5)

            # Simuler une transaction de vente
            exit_price = simulate_sell(ticker, data_with_indicators)

            # Mettez à jour les données du trade en cours avec le prix de sortie
            active_trade_charts[ticker]['Exit Timestamp'] = data_with_indicators.index[-1]
            active_trade_charts[ticker]['Exit Price'] = exit_price

            # Ajouter le trade à l'historique
            trade_history.append([ticker, entry_price, exit_price, quantity, (exit_price - entry_price) * quantity])

            # Afficher les graphiques en temps réel mis à jour
            show_live_trade_charts()

# Créez une liste vide des graphiques en cours
active_trade_charts = {}

# Créez un thread pour mettre à jour les graphiques en temps réel
import threading
update_thread = threading.Thread(target=update_live_trade_charts)
update_thread.daemon = True
update_thread.start()

# Lancer la boucle principale de Tkinter
root.mainloop()

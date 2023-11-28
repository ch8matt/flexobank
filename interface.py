import tkinter as tk
from tkinter import ttk
from analysis import analyze_tickers, get_stock_data, calculate_technical_indicators
from trader import simulate_buy, simulate_sell

# Initialisez votre historique des trades
trade_history = []

# Créez une fenêtre Tkinter
root = tk.Tk()
root.title("Live Trade Analysis")

# Créez un tableau pour afficher les trades
columns = ("Ticker", "Entry Price", "Exit Price", "Quantity", "Profit/Loss")
trade_table = ttk.Treeview(root, columns=columns, show='headings')
for col in columns:
    trade_table.heading(col, text=col)
trade_table.pack(expand=True, fill='both')

def update_trade_table():
    # Récupérez et traitez les données de trading
    potential_stocks = analyze_tickers()

    for ticker, reason in potential_stocks:
        print(f"Trader should consider: {ticker} because {reason}")
        data = get_stock_data(ticker)
        data_with_indicators = calculate_technical_indicators(data)

        entry_price, quantity = simulate_buy(ticker, data_with_indicators)
        exit_price = simulate_sell(ticker, data_with_indicators)

        profit_loss = (exit_price - entry_price) * quantity
        trade_history.append([ticker, entry_price, exit_price, quantity, profit_loss])

        # Mettez à jour le tableau
        trade_table.insert("", "end", values=(ticker, entry_price, exit_price, quantity, profit_loss))

    root.after(1000, update_trade_table)  # Mise à jour toutes les 1 secondes

# Lancer la première mise à jour du tableau
update_trade_table()

# Lancer la boucle principale de Tkinter
root.mainloop()

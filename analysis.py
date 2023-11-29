import sqlite3
import pandas as pd
import ta
import tkinter as tk
from tkinter import ttk
from datetime import datetime

def connect_to_db():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect('stock_data.db')

def ask_user_decisions(potential_trades):
    def on_confirm():
        for ticker in decisions:
            decisions[ticker] = decision_vars[ticker].get()
        root.quit()  # Quit the main loop
        root.destroy()  # Destroy the window

    root = tk.Tk()
    root.title("Trade Decisions")
    decisions = {trade['ticker']: False for trade in potential_trades}
    decision_vars = {}

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    for i, trade in enumerate(potential_trades):
        decision_vars[trade['ticker']] = tk.BooleanVar(value=False)  # Initialize as opted out
        ttk.Label(frame, text=f"Ticker: {trade['ticker']}").grid(row=i, column=0, sticky=tk.W)
        ttk.Label(frame, text=f"Close Price: {trade['close']}").grid(row=i, column=1, sticky=tk.W)
        ttk.Label(frame, text=f"Analysis: {trade['action']}").grid(row=i, column=2, sticky=tk.W)
        ttk.Checkbutton(frame, text="Confirm Trade", variable=decision_vars[trade['ticker']]).grid(row=i, column=3, sticky=tk.W)

    ttk.Button(frame, text="Submit Decisions", command=on_confirm).grid(row=len(potential_trades) + 1, column=0, sticky=tk.W)

    root.mainloop()
    return decisions


def calculate_technical_indicators():
    conn = connect_to_db()
    cursor = conn.cursor()
    
    print("Calculating various technical indicators for stock data.")

    all_data = pd.DataFrame()
    potential_trades = []

    cursor.execute("SELECT DISTINCT ticker FROM minute_data")
    tickers = cursor.fetchall()
    
    for ticker in tickers:
        data = pd.read_sql_query(f"SELECT date, close, volume FROM minute_data WHERE ticker='{ticker[0]}' ORDER BY date DESC", conn)

        if not data.empty:
            data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d %H:%M:%S')

            # Calculate technical indicators
            data['SMA_50'] = ta.trend.sma_indicator(data['close'], window=50)
            data['EMA_50'] = ta.trend.ema_indicator(data['close'], window=50)
            data['RSI_14'] = ta.momentum.rsi(data['close'], window=14)
            bollinger = ta.volatility.BollingerBands(data['close'], window=20, window_dev=2)
            data['Bollinger_Mavg'] = bollinger.bollinger_mavg()
            data['Bollinger_hband'] = bollinger.bollinger_hband()
            data['Bollinger_lband'] = bollinger.bollinger_lband()
            data['On-Balance volume'] = ta.volume.on_balance_volume(data['close'], data['volume'])
            macd = ta.trend.MACD(data['close'])
            data['MACD_line'] = macd.macd()
            data['Signal_line'] = macd.macd_signal()
            data['MACD_diff'] = macd.macd_diff()

            # Collecting potential trades
            clear_signal = check_and_add_trade(data, ticker[0], potential_trades)

            # Handling the case of no clear signal
            if not clear_signal:
                new_row = pd.DataFrame({
                    'Ticker': [ticker[0]],
                    'Date': [datetime.now()],
                    'Close': [data['close'].iloc[-1]],
                    'Trade_Action': ['No'],
                    'Trade_Reason': ['No clear bullish or bearish signal']
                })
                all_data = pd.concat([all_data, new_row], ignore_index=True)

    # Ask user decisions for all potential trades at once
    user_decisions = ask_user_decisions(potential_trades)

    # Process user decisions
    for trade in potential_trades:
        ticker = trade['ticker']
        trade_action = 'Sell' if 'Bearish' in trade['action'] else 'Buy'
        trade_action = trade_action if user_decisions[ticker] else 'No'
        trade_reason = trade['action']

        new_row = pd.DataFrame({
            'Ticker': [ticker],
            'Date': [datetime.now()],
            'Close': [trade['close']],
            'Trade_Action': [trade_action],
            'Trade_Reason': [trade_reason]
        })

        all_data = pd.concat([all_data, new_row], ignore_index=True)

    all_data.to_csv('shared_data.csv', mode='a', index=False)
    print("Saved all data to shared_data.csv")

    conn.close()

def check_and_add_trade(data, ticker, potential_trades):
    clear_signal = False

    # Bullish signals
    if data['RSI_14'].iloc[-1] < 30:
        potential_trades.append({'ticker': ticker, 'close': data['close'].iloc[-1], 'action': 'RSI indicates potential underpricing (Bullish)'})
        clear_signal = True
    if data['MACD_line'].iloc[-1] > data['Signal_line'].iloc[-1]:
        potential_trades.append({'ticker': ticker, 'close': data['close'].iloc[-1], 'action': 'MACD bullish crossover (Bullish)'})
        clear_signal = True
    if data['close'].iloc[-1] < data['Bollinger_lband'].iloc[-1]:
        potential_trades.append({'ticker': ticker, 'close': data['close'].iloc[-1], 'action': 'Price near lower Bollinger Band (Bullish)'})
        clear_signal = True
    if data['close'].iloc[-1] > data['EMA_50'].iloc[-1]:
        potential_trades.append({'ticker': ticker, 'close': data['close'].iloc[-1], 'action': 'Price above EMA 50, potential uptrend (Bullish)'})
        clear_signal = True

    # Bearish signals
    if data['RSI_14'].iloc[-1] > 70:
        potential_trades.append({'ticker': ticker, 'close': data['close'].iloc[-1], 'action': 'RSI indicates potential overpricing (Bearish)'})
        clear_signal = True
    if data['MACD_line'].iloc[-1] < data['Signal_line'].iloc[-1]:
        potential_trades.append({'ticker': ticker, 'close': data['close'].iloc[-1], 'action': 'MACD bearish crossover (Bearish)'})
        clear_signal = True
    if data['close'].iloc[-1] > data['Bollinger_hband'].iloc[-1]:
        potential_trades.append({'ticker': ticker, 'close': data['close'].iloc[-1], 'action': 'Price above upper Bollinger Band (Bearish)'})
        clear_signal = True

    return clear_signal

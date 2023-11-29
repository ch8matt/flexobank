import sqlite3
import pandas as pd
import ta
import tkinter as tk
from tkinter import ttk
from datetime import datetime

def connect_to_db():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect('stock_data.db')

def calculate_technical_indicators():
    conn = connect_to_db()
    cursor = conn.cursor()
    
    print("Calculating various technical indicators for stock data.")

    all_data = pd.DataFrame()

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

            potential_stocks = []

            # Bullish signals
            if data['RSI_14'].iloc[-1] < 30:
                potential_stocks.append((ticker[0], 'RSI indicates potential underpricing (Bullish)'))
            if data['MACD_line'].iloc[-1] > data['Signal_line'].iloc[-1]:
                potential_stocks.append((ticker[0], 'MACD bullish crossover (Bullish)'))
            if data['close'].iloc[-1] < data['Bollinger_lband'].iloc[-1]:
                potential_stocks.append((ticker[0], 'Price near lower Bollinger Band (Bullish)'))
            if data['close'].iloc[-1] > data['EMA_50'].iloc[-1]:
                potential_stocks.append((ticker[0], 'Price above EMA 50, potential uptrend (Bullish)'))

            # Bearish signals
            if data['RSI_14'].iloc[-1] > 70:
                potential_stocks.append((ticker[0], 'RSI indicates potential overpricing (Bearish)'))
            if data['MACD_line'].iloc[-1] < data['Signal_line'].iloc[-1]:
                potential_stocks.append((ticker[0], 'MACD bearish crossover (Bearish)'))
            if data['close'].iloc[-1] > data['Bollinger_hband'].iloc[-1]:
                potential_stocks.append((ticker[0], 'Price above upper Bollinger Band (Bearish)'))

            if potential_stocks:
                for stock, reason in potential_stocks:
                    user_decision = ask_user_decision(stock, data['close'].iloc[-1], reason)
                    trade_action = 'Sell' if 'Bearish' in reason else 'Buy'
                    trade_action = trade_action if user_decision else 'No'
                    trade_reason = reason
            else:
                # No clear signal
                trade_action = 'No'
                trade_reason = 'No clear bullish or bearish signal'

            new_row = pd.DataFrame({
                'Ticker': [ticker[0]],
                'Date': [datetime.now()],
                'Close': [data['close'].iloc[-1]],
                'Trade_Action': [trade_action],
                'Trade_Reason': [trade_reason]
            })

            all_data = pd.concat([all_data, new_row], ignore_index=True)

    all_data.to_csv('shared_data.csv', mode='a', index=False)
    print("Saved all data to shared_data.csv")

    conn.close()

def ask_user_decision(ticker, close, action):
    def on_confirm():
        decision.set(True)
        root.destroy()

    def on_cancel():
        decision.set(False)
        root.destroy()

    root = tk.Tk()
    root.title("Trade Decision")
    decision = tk.BooleanVar()

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    ttk.Label(frame, text=f"Ticker: {ticker}").grid(row=0, column=0, sticky=tk.W)
    ttk.Label(frame, text=f"Close Price: {close}").grid(row=1, column=0, sticky=tk.W)
    ttk.Label(frame, text=f"Analysis: {action}").grid(row=2, column=0, sticky=tk.W)
    ttk.Label(frame, text=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}").grid(row=3, column=0, sticky=tk.W)

    ttk.Button(frame, text="Confirm", command=on_confirm).grid(row=4, column=0, sticky=tk.W)
    ttk.Button(frame, text="Cancel", command=on_cancel).grid(row=4, column=1, sticky=tk.W)

    root.mainloop()
    return decision.get()
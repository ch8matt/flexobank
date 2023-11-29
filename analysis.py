import sqlite3
import pandas as pd
import ta
import tkinter as tk
from tkinter import messagebox
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

            latest_data = data.iloc[0]

            buy_condition = (latest_data['close'] > latest_data['SMA_50']) and \
                            (latest_data['close'] > latest_data['EMA_50']) and \
                            (latest_data['MACD_line'] > latest_data['Signal_line']) and \
                            (latest_data['RSI_14'] < 30)

            sell_condition = (latest_data['close'] < latest_data['SMA_50']) and \
                            (latest_data['close'] < latest_data['EMA_50']) and \
                            (latest_data['MACD_line'] < latest_data['Signal_line']) and \
                            (latest_data['RSI_14'] > 70)

            if buy_condition or sell_condition:
                action = 'Buy' if buy_condition else 'Sell'
                user_decision = ask_user_decision(ticker[0], latest_data['close'], latest_data['date'], action)
                trade_action = action if user_decision else 'No'
                trade_reason = 'Buy - Above SMA_50 & RSI < 30' if buy_condition else 'Sell - Below SMA_50 & RSI > 70'
            else:
                trade_action = 'No'
                trade_reason = 'Not recommended to trade'

            new_row = pd.DataFrame({
                'Ticker': [ticker[0]],
                'Date': [datetime.now()],
                'Close': [latest_data['close']],
                'Trade_Action': [trade_action],
                'Trade_Reason': [trade_reason]
            })

            all_data = pd.concat([all_data, new_row], ignore_index=True)

    all_data.to_csv('shared_data.csv', mode='a', index=False)
    print("Saved all data to shared_data.csv")

    conn.close()

def ask_user_decision(ticker, close, date, action):
    root = tk.Tk()
    root.withdraw()  # hide the main window
    decision = messagebox.askyesno("Trade Decision", f"{action} signal for {ticker} at {close} on {date}. Execute trade?")
    root.destroy()  # close the Tkinter root window
    return decision

# Call the function
calculate_technical_indicators()

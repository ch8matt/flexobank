import sqlite3
import pandas as pd
import ta
from datetime import datetime

def connect_to_db():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect('stock_data.db')

def calculate_technical_indicators():
    conn = connect_to_db()
    cursor = conn.cursor()
    
    print("Calculating various technical indicators for stock data.")

    all_data = pd.DataFrame()
    potential_trades = []

    cursor.execute("SELECT DISTINCT ticker FROM minute_data")
    tickers = cursor.fetchall()
    
    for ticker in tickers:
        data = pd.read_sql_query(f"SELECT date, Close, Volume FROM minute_data WHERE ticker='{ticker[0]}' ORDER BY date DESC", conn)

        if not data.empty:
            if 'date' not in data.columns:
                data.reset_index(inplace=True)
                # If the date column is named differently after reset, rename it
                if 'index' in data.columns:
                    data.rename(columns={'index': 'Date'}, inplace=True)

            # Calculate technical indicators
            data['SMA_50'] = ta.trend.sma_indicator(data['Close'], window=50)
            data['EMA_50'] = ta.trend.ema_indicator(data['Close'], window=50)
            data['RSI_14'] = ta.momentum.rsi(data['Close'], window=14)
            bollinger = ta.volatility.BollingerBands(data['Close'], window=20, window_dev=2)
            data['Bollinger_Mavg'] = bollinger.bollinger_mavg()
            data['Bollinger_hband'] = bollinger.bollinger_hband()
            data['Bollinger_lband'] = bollinger.bollinger_lband()
            data['On-Balance Volume'] = ta.volume.on_balance_volume(data['Close'], data['Volume'])
            macd = ta.trend.MACD(data['Close'])
            data['MACD_line'] = macd.macd()
            data['Signal_line'] = macd.macd_signal()
            data['MACD_diff'] = macd.macd_diff()

            # Collecting potential trades
            check_and_add_trade(data, ticker[0], potential_trades)

    conn.close()
    return potential_trades

def check_and_add_trade(data, ticker, potential_trades):
    clear_signal = False

    # Bullish signals
    if data['RSI_14'].iloc[-1] < 30:
        potential_trades.append({'ticker': ticker, 'Close': data['Close'].iloc[-1], 'action': 'BUY: RSI indicates potential underpricing'})
        clear_signal = True
    if data['MACD_line'].iloc[-1] > data['Signal_line'].iloc[-1]:
        potential_trades.append({'ticker': ticker, 'Close': data['Close'].iloc[-1], 'action': 'BUY: MACD bullish crossover'})
        clear_signal = True
    if data['Close'].iloc[-1] < data['Bollinger_lband'].iloc[-1]:
        potential_trades.append({'ticker': ticker, 'Close': data['Close'].iloc[-1], 'action': 'BUY: Price near lower Bollinger Band'})
        clear_signal = True
    if data['Close'].iloc[-1] > data['EMA_50'].iloc[-1]:
        potential_trades.append({'ticker': ticker, 'Close': data['Close'].iloc[-1], 'action': 'BUY: Price above EMA 50, potential uptrend'})
        clear_signal = True

    # Bearish signals
    if data['RSI_14'].iloc[-1] > 70:
        potential_trades.append({'ticker': ticker, 'Close': data['Close'].iloc[-1], 'action': 'SELL: RSI indicates potential overpricing'})
        clear_signal = True
    if data['MACD_line'].iloc[-1] < data['Signal_line'].iloc[-1]:
        potential_trades.append({'ticker': ticker, 'Close': data['Close'].iloc[-1], 'action': 'SELL: MACD bearish crossover'})
        clear_signal = True
    if data['Close'].iloc[-1] > data['Bollinger_hband'].iloc[-1]:
        potential_trades.append({'ticker': ticker, 'Close': data['Close'].iloc[-1], 'action': 'SELL: Price above upper Bollinger Band'})
        clear_signal = True

    return clear_signal

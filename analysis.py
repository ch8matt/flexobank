from tickers import get_tickers
from datetime import datetime, timedelta

import ta
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(ticker, start_date=None, end_date=None):
    if start_date is None:
        start_date = datetime(datetime.now().year, 1, 1)
    if end_date is None:
        end_date = datetime.now()

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    all_data = pd.DataFrame()

    # Définir la date de début pour les données à la minute (au plus tôt 30 jours avant la date actuelle)
    minute_data_start_date = max(end_date - timedelta(days=29), start_date)

    # Récupérer les données quotidiennes pour la période avant les 30 derniers jours, si nécessaire
    if start_date < minute_data_start_date:
        try:
            daily_data = yf.download(ticker, start=start_date, end=minute_data_start_date, interval='1d')
            all_data = pd.concat([all_data, daily_data])
        except Exception as e:
            print(f"Error retrieving daily data for {ticker} from {start_date} to {minute_data_start_date}: {e}")

    # Récupérer les données à la minute pour les 30 derniers jours
    current_date = minute_data_start_date
    while current_date < end_date:
        period_end_date = min(current_date + timedelta(days=7), end_date)
        try:
            minute_data = yf.download(ticker, start=current_date, end=period_end_date, interval='1m')
            if not minute_data.empty:
                all_data = pd.concat([all_data, minute_data])
        except Exception as e:
            print(f"Error retrieving minute data for {ticker} from {current_date} to {period_end_date}: {e}")
        current_date = period_end_date

    return all_data

# Fonction pour calculer les indicateurs techniques
def calculate_technical_indicators(data):
    # Indicateurs de tendance
    data['SMA_50'] = ta.trend.sma_indicator(data['Close'], window=50)
    data['EMA_50'] = ta.trend.ema_indicator(data['Close'], window=50)
    
    # Indicateurs de momentum
    data['RSI_14'] = ta.momentum.rsi(data['Close'], window=14)
    
    # Indicateurs de volatilité
    bollinger = ta.volatility.BollingerBands(data['Close'], window=20, window_dev=2)
    data['Bollinger_Mavg'] = bollinger.bollinger_mavg()
    data['Bollinger_hband'] = bollinger.bollinger_hband()
    data['Bollinger_lband'] = bollinger.bollinger_lband()
    
    # Indicateurs de volume
    data['On-Balance Volume'] = ta.volume.on_balance_volume(data['Close'], data['Volume'])
    
    # Indicateurs de tendance - MACD
    macd = ta.trend.MACD(data['Close'])
    data['MACD_line'] = macd.macd()
    data['Signal_line'] = macd.macd_signal()
    data['MACD_diff'] = macd.macd_diff()
    
    return data

def analyze_tickers():
    """Analyse les tickers et sélectionne ceux avec le plus de potentiel."""
    tickers = get_tickers()
    potential_stocks = []
    
    for ticker in tickers:
        print(f"Analyzing {ticker}...")
        data = get_stock_data(ticker)
        data_with_indicators = calculate_technical_indicators(data)
        
        # Conditions pour déterminer si un ticker a du potentiel
        if data_with_indicators['RSI_14'].iloc[-1] < 30:
            potential_stocks.append((ticker, 'RSI indicates potential underpricing'))
        if data_with_indicators['MACD_line'].iloc[-1] > data_with_indicators['Signal_line'].iloc[-1]:
            potential_stocks.append((ticker, 'MACD bullish crossover'))
        if data_with_indicators['Close'].iloc[-1] < data_with_indicators['Bollinger_lband'].iloc[-1]:
            potential_stocks.append((ticker, 'Price near lower Bollinger Band'))
        if data_with_indicators['Close'].iloc[-1] > data_with_indicators['EMA_50'].iloc[-1]:
            potential_stocks.append((ticker, 'Price above EMA 50, potential uptrend'))

    return potential_stocks

# Fonction pour calculer les indicateurs techniques pour plusieurs actions
def calculate_indicators_for_multiple_stocks(tickers):
    all_data = {}

    for ticker in tickers:
        # Récupérer les données financières
        stock_data = get_stock_data(ticker)

        # Calculer les indicateurs techniques
        stock_data_with_indicators = calculate_technical_indicators(stock_data)

        # Stocker les données dans un dictionnaire
        all_data[ticker] = stock_data_with_indicators

    return all_data

if __name__ == "__main__":
    # Exemple d'utilisation de la fonction d'analyse
    print(analyze_tickers())

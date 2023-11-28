# Ce fichier effectue l'analyse technique des tickers.

import yfinance as yf
import ta

from tickers import get_tickers

def get_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

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

def analyze_tickers(start_date, end_date):
    """Analyse les tickers et sélectionne ceux avec le plus de potentiel."""
    tickers = get_tickers()
    potential_stocks = []
    
    for ticker in tickers:
        print(f"Analyzing {ticker}...")
        data = get_stock_data(ticker, start_date, end_date)
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
def calculate_indicators_for_multiple_stocks(tickers, start_date, end_date):
    all_data = {}

    for ticker in tickers:
        # Récupérer les données financières
        stock_data = get_stock_data(ticker, start_date, end_date)

        # Calculer les indicateurs techniques
        stock_data_with_indicators = calculate_technical_indicators(stock_data)

        # Stocker les données dans un dictionnaire
        all_data[ticker] = stock_data_with_indicators

    return all_data

if __name__ == "__main__":
    # Exemple d'utilisation de la fonction d'analyse
    start_date = '2022-01-01'
    end_date = '2023-01-01'
    print(analyze_tickers(start_date, end_date))

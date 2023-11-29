import sqlite3
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import time 

from tickers import get_tickers
from analysis import calculate_technical_indicators

def connect_to_db():
    """Établit une connexion à la base de données SQLite."""
    return sqlite3.connect('stock_data.db')

def clear_database():
    """Clears all data from the database if tables exist."""
    conn = connect_to_db()
    cursor = conn.cursor()

    # Check if 'daily_data' table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_data'")
    if cursor.fetchone():
        cursor.execute("DELETE FROM daily_data")
    
    # Check if 'minute_data' table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='minute_data'")
    if cursor.fetchone():
        cursor.execute("DELETE FROM minute_data")

    conn.commit()
    conn.close()

def create_tables():
    """Crée les tables nécessaires dans la base de données."""
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_data (
            ticker TEXT,
            date DATETIME,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (date, ticker)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS minute_data (
            ticker TEXT,
            date DATETIME,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (date, ticker)
        )
    ''')
    conn.commit()
    conn.close()

def get_daily_data(ticker, start_date, end_date):
    try:
        print(f"Retrieving daily data for {ticker} from {start_date} to {end_date}...")
        data = yf.download(ticker, start=start_date, end=end_date, interval='1d', progress=False)
        if not data.empty:
            conn = connect_to_db()
            data.reset_index(inplace=True)
            data = data.drop(columns=['Adj Close'])  # Drop the Adj Close column
            data['ticker'] = ticker
            data.to_sql('daily_data', conn, if_exists='append', index=False)
            conn.close()
    except Exception as e:
        print(f"Error retrieving daily data for {ticker}: {e}")


def get_minute_data(ticker, start_date, end_date):
    """Retrieve minute-level stock data in chunks of 7 days."""
    all_minute_data = []
    current_date = start_date
    while current_date < end_date:
        period_end_date = min(current_date + timedelta(days=7), end_date)
        try:
            print(f"Retrieving minute data for {ticker} from {current_date} to {period_end_date}...")
            minute_data = yf.download(ticker, start=current_date, end=period_end_date, interval='1m', progress=False)
            if not minute_data.empty:
                # Drop the 'Adj Close' column
                minute_data = minute_data.drop(columns=['Adj Close'])

                all_minute_data.append(minute_data)
        except Exception as e:
            print(f"Error retrieving minute data for {ticker}: {e}")
        current_date = period_end_date

    # Check if data was retrieved and append to the database
    if all_minute_data:
        conn = connect_to_db()
        concatenated_data = pd.concat(all_minute_data, ignore_index=True)
        concatenated_data['ticker'] = ticker
        concatenated_data.to_sql('minute_data', conn, if_exists='append', index=False)
        conn.close()


def continuous_analysis():
    """Effectue une analyse continue, en mettant à jour la base de données régulièrement."""
    tickers = get_tickers()
    end_date = datetime.now()
    start_date_daily = end_date - timedelta(days=1*365)  # 1 ans
    start_date_minute = end_date - timedelta(days=29)  # 29 jours

    # Récupération initiale des données
    for ticker in tickers:
        get_daily_data(ticker, start_date_daily, end_date)
        get_minute_data(ticker, start_date_minute, end_date)

    # Mise à jour continue
    while True:
        current_time = datetime.now()
        for ticker in tickers:
            get_minute_data(ticker, current_time - timedelta(days=1), current_time)
        calculate_technical_indicators()
        time.sleep(60)


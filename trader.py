# trader.py

from analysis import analyze_tickers

def advise_trader():
    """Conseille le trader fictif sur les actions à considérer."""
    start_date = '2022-01-01'
    end_date = '2023-01-01'
    potential_stocks = analyze_tickers(start_date, end_date)

    for ticker, reason in potential_stocks:
        print(f"Trader should consider: {ticker} because {reason}")

if __name__ == "__main__":
    advise_trader()

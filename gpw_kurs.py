#!/usr/bin/env python3
"""
Program for fetching stock prices from GPW (Warsaw Stock Exchange)
Usage: python gpw_kurs.py STOCKS_FILE
Example: python gpw_kurs.py akcje.txt
Program checks prices every configurable interval and displays them on screen.
"""

import sys
import yfinance as yf
import time
import os
from datetime import datetime
from collections import defaultdict
import configparser
try:
    import plotext as plt
except ImportError:
    print("Installing plotext library...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotext"])
    import plotext as plt

# ANSI colors
COLOR_GREEN = '\033[92m'
COLOR_RED = '\033[91m'
COLOR_RESET = '\033[0m'


def load_config():
    """
    Loads configuration from config.ini file.
    
    Returns:
        Dictionary with configuration settings
    """
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    
    # Default values
    defaults = {
        'refresh_interval': 30,
        'max_history': 50,
        'plot_width': 100,
        'plot_height': 20
    }
    
    if os.path.exists(config_path):
        try:
            config.read(config_path)
            return {
                'refresh_interval': config.getint('Settings', 'refresh_interval', fallback=defaults['refresh_interval']),
                'max_history': config.getint('Settings', 'max_history', fallback=defaults['max_history']),
                'plot_width': config.getint('Settings', 'plot_width', fallback=defaults['plot_width']),
                'plot_height': config.getint('Settings', 'plot_height', fallback=defaults['plot_height'])
            }
        except Exception as e:
            print(f"Warning: Error loading configuration: {e}")
            print("Using default settings.")
            return defaults
    else:
        print(f"Warning: config.ini file not found, using default settings.")
        return defaults


def load_stocks_from_file(filename):
    """
    Loads list of stock symbols from text file.
    Format: SYMBOL,PURCHASE_PRICE or just SYMBOL (then purchase price = 0.00)
    
    Args:
        filename: Path to file with stock symbols
    
    Returns:
        Dictionary {symbol: purchase_price}
    """
    try:
        stocks = {}
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # Check if there's a comma (format: SYMBOL,PRICE)
                if ',' in line:
                    parts = line.split(',')
                    symbol = parts[0].strip().upper()
                    try:
                        purchase_price = float(parts[1].strip())
                    except ValueError:
                        purchase_price = 0.00
                    stocks[symbol] = purchase_price
                else:
                    # Only symbol, purchase price = 0.00
                    symbol = line.upper()
                    stocks[symbol] = 0.00
        
        return stocks if stocks else None
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return None


def draw_chart(price_history, stock_symbol, config, currency='PLN'):
    """
    Draws stock price chart in terminal.
    
    Args:
        price_history: List with data (time, price)
        stock_symbol: Stock symbol
        config: Dictionary with configuration
        currency: Price currency
    """
    if len(price_history) < 2:
        return
    
    times = [h[0] for h in price_history]
    prices = [h[1] for h in price_history]
    
    # Use numeric indices instead of time strings
    indices = list(range(len(prices)))
    
    # Create chart in terminal
    plt.clf()
    plt.plot(indices, prices, marker="braille")
    plt.title(f"Price Chart {stock_symbol}")
    plt.xlabel("Time")
    plt.ylabel(f"Price ({currency})")
    
    # Set X axis labels - show every few points for readability
    step = max(1, len(times) // 5)  # Show max 5-6 labels
    xticks_pos = [i for i in range(0, len(times), step)]
    xticks_labels = [times[i] for i in xticks_pos]
    plt.xticks(xticks_pos, xticks_labels)
    
    plt.plotsize(config['plot_width'], config['plot_height'])
    plt.show()


def calculate_profit_loss(current_price, purchase_price):
    """
    Calculates profit/loss in percentage and absolute value.
    
    Args:
        current_price: Current stock price
        purchase_price: Stock purchase price
    
    Returns:
        Tuple (percent_change, amount_change, is_profit)
    """
    if purchase_price == 0.00:
        return None, None, None
    
    amount_change = current_price - purchase_price
    percent_change = (amount_change / purchase_price) * 100
    is_profit = amount_change >= 0
    
    return percent_change, amount_change, is_profit


def get_stock_price(stock_symbol):
    """
    Fetches current stock price from GPW.
    
    Args:
        stock_symbol: Stock symbol (e.g. 'PKO', 'PKNORLEN')
    
    Returns:
        Current stock price or None in case of error
    """
    try:
        # Add .WA suffix for GPW stocks
        if not stock_symbol.endswith('.WA'):
            symbol = f"{stock_symbol}.WA"
        else:
            symbol = stock_symbol
        
        # Fetch stock data
        stock = yf.Ticker(symbol)
        
        # Get current price
        info = stock.info
        
        # Check various possible keys for current price
        price = None
        if 'currentPrice' in info and info['currentPrice']:
            price = info['currentPrice']
        elif 'regularMarketPrice' in info and info['regularMarketPrice']:
            price = info['regularMarketPrice']
        elif 'previousClose' in info and info['previousClose']:
            price = info['previousClose']
            print(f"Note: Returning closing price from previous session")
        
        if price:
            currency = info.get('currency', 'PLN')
            full_name = info.get('longName', info.get('shortName', stock_symbol))
            return {
                'symbol': symbol,
                'name': full_name,
                'price': price,
                'currency': currency
            }
        else:
            return None
            
    except Exception as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        return None


def main():
    if len(sys.argv) != 2:
        print("Usage: python gpw_kurs.py STOCKS_FILE")
        print("Example: python gpw_kurs.py akcje.txt")
        print("\nFile format: one stock symbol per line")
        print("Example file contents:")
        print("  PKO")
        print("  PKNORLEN")
        print("  KGHM")
        sys.exit(1)
    
    stocks_file = sys.argv[1]
    
    # Load configuration
    config = load_config()
    refresh_interval = config['refresh_interval']
    max_history = config['max_history']
    
    print(f"Loading stock list from file: {stocks_file}...")
    stocks = load_stocks_from_file(stocks_file)
    
    if not stocks:
        print("Failed to load stock list.")
        sys.exit(1)
    
    if len(stocks) == 0:
        print("File contains no stock symbols.")
        sys.exit(1)
    
    print(f"Found {len(stocks)} stocks: {', '.join(stocks.keys())}")
    print(f"\nProgram will check prices every {refresh_interval} seconds.")
    print("Press Ctrl+C to stop.\n")
    
    # Dictionary to store price history for each stock
    history = defaultdict(list)
    
    try:
        while True:
            current_time = datetime.now()
            time_str = current_time.strftime("%H:%M:%S")
            time_full = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"\n{'='*100}")
            print(f"Price Update: {time_full}")
            print(f"{'='*100}")
            
            for stock_symbol, purchase_price in stocks.items():
                result = get_stock_price(stock_symbol)
                
                if result:
                    price = result['price']
                    currency = result['currency']
                    # Add to history
                    history[stock_symbol].append((time_str, price))
                    # Keep only the last measurements according to config
                    if len(history[stock_symbol]) > max_history:
                        history[stock_symbol].pop(0)
                    
                    # Basic information
                    info_base = f"{result['symbol']:15s} | {price:10.2f} {currency:3s} | {result['name'][:25]:25s}"
                    
                    # Calculate profit/loss
                    percent, amount, is_profit = calculate_profit_loss(price, purchase_price)
                    
                    if percent is not None:
                        if is_profit:
                            info_profit = f"{COLOR_GREEN}+{percent:6.2f}% (+{amount:7.2f} {currency}){COLOR_RESET}"
                        else:
                            info_profit = f"{COLOR_RED}{percent:7.2f}% ({amount:7.2f} {currency}){COLOR_RESET}"
                        print(f"{info_base} | {info_profit}")
                    else:
                        print(info_base)
                else:
                    print(f"{stock_symbol:15s} | {'ERROR':>14s} | Failed to fetch price")
            
            print(f"{'='*100}\n")
            
            # Draw separate charts for each stock
            for stock_symbol in stocks.keys():
                if stock_symbol in history and len(history[stock_symbol]) >= 2:
                    # Get currency from last read
                    result = get_stock_price(stock_symbol)
                    currency = result['currency'] if result else 'PLN'
                    draw_chart(history[stock_symbol], stock_symbol, config, currency)
                    print()
            
            print(f"{'='*100}")
            print(f"Next update in {refresh_interval} seconds...")
            print(f"{'='*100}")
            
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n\nStopped monitoring prices.")
        sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Program do pobierania kursu akcji z GPW (Giełda Papierów Wartościowych w Warszawie)
Użycie: python gpw_kurs.py PLIK_Z_AKCJAMI
Przykład: python gpw_kurs.py akcje.txt
Program sprawdza kursy co 60 sekund i wyświetla je na ekranie.
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
    print("Instaluję bibliotekę plotext...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotext"])
    import plotext as plt

# ANSI colors
COLOR_GREEN = '\033[92m'
COLOR_RED = '\033[91m'
COLOR_RESET = '\033[0m'


def load_config():
    """
    Wczytuje konfigurację z pliku config.ini.
    
    Returns:
        Słownik z ustawieniami konfiguracyjnymi
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
            print(f"Uwaga: Błąd podczas wczytywania konfiguracji: {e}")
            print("Używam domyślnych ustawień.")
            return defaults
    else:
        print(f"Uwaga: Nie znaleziono pliku config.ini, używam domyślnych ustawień.")
        return defaults


def load_stocks_from_file(filename):
    """
    Wczytuje listę symboli akcji z pliku tekstowego.
    Format: SYMBOL,CENA_ZAKUPU lub samo SYMBOL (wtedy cena zakupu = 0.00)
    
    Args:
        filename: Ścieżka do pliku z symbolami akcji
    
    Returns:
        Słownik {symbol: cena_zakupu}
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
        print(f"Błąd: Nie znaleziono pliku '{filename}'", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Błąd podczas czytania pliku: {e}", file=sys.stderr)
        return None


def draw_chart(price_history, stock_symbol, config, currency='PLN'):
    """
    Rysuje wykres kursu akcji w terminalu.
    
    Args:
        price_history: Lista z danymi (czas, kurs)
        stock_symbol: Symbol akcji
        config: Słownik z konfiguracją
        currency: Waluta kursu
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
    plt.title(f"Wykres kursu {stock_symbol}")
    plt.xlabel("Czas")
    plt.ylabel(f"Kurs ({currency})")
    
    # Set X axis labels - show every few points for readability
    step = max(1, len(times) // 5)  # Show max 5-6 labels
    xticks_pos = [i for i in range(0, len(times), step)]
    xticks_labels = [times[i] for i in xticks_pos]
    plt.xticks(xticks_pos, xticks_labels)
    
    plt.plotsize(config['plot_width'], config['plot_height'])
    plt.show()


def calculate_profit_loss(current_price, purchase_price):
    """
    Oblicza zysk/stratę w procentach i wartości bezwzględnej.
    
    Args:
        current_price: Aktualny kurs akcji
        purchase_price: Cena zakupu akcji
    
    Returns:
        Tuple (procent_zmiany, kwota_zmiany, czy_zysk)
    """
    if purchase_price == 0.00:
        return None, None, None
    
    amount_change = current_price - purchase_price
    percent_change = (amount_change / purchase_price) * 100
    is_profit = amount_change >= 0
    
    return percent_change, amount_change, is_profit


def get_stock_price(stock_symbol):
    """
    Pobiera aktualny kurs akcji z GPW.
    
    Args:
        stock_symbol: Symbol akcji (np. 'PKO', 'PKNORLEN')
    
    Returns:
        Aktualny kurs akcji lub None w przypadku błędu
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
            print(f"Uwaga: Zwracam kurs zamknięcia z poprzedniej sesji")
        
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
        print(f"Błąd podczas pobierania danych: {e}", file=sys.stderr)
        return None


def main():
    if len(sys.argv) != 2:
        print("Użycie: python gpw_kurs.py PLIK_Z_AKCJAMI")
        print("Przykład: python gpw_kurs.py akcje.txt")
        print("\nFormat pliku: jeden symbol akcji w każdej linii")
        print("Przykład zawartości pliku:")
        print("  PKO")
        print("  PKNORLEN")
        print("  KGHM")
        sys.exit(1)
    
    stocks_file = sys.argv[1]
    
    # Load configuration
    config = load_config()
    refresh_interval = config['refresh_interval']
    max_history = config['max_history']
    
    print(f"Wczytuję listę akcji z pliku: {stocks_file}...")
    stocks = load_stocks_from_file(stocks_file)
    
    if not stocks:
        print("Nie udało się wczytać listy akcji.")
        sys.exit(1)
    
    if len(stocks) == 0:
        print("Plik nie zawiera żadnych symboli akcji.")
        sys.exit(1)
    
    print(f"Znaleziono {len(stocks)} akcji: {', '.join(stocks.keys())}")
    print(f"\nProgram będzie sprawdzać kursy co {refresh_interval} sekund.")
    print("Naciśnij Ctrl+C aby zakończyć.\n")
    
    # Dictionary to store price history for each stock
    history = defaultdict(list)
    
    try:
        while True:
            current_time = datetime.now()
            time_str = current_time.strftime("%H:%M:%S")
            time_full = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"\n{'='*100}")
            print(f"Aktualizacja kursów: {time_full}")
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
                    print(f"{stock_symbol:15s} | {'BŁĄD':>14s} | Nie udało się pobrać kursu")
            
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
            print(f"Następna aktualizacja za {refresh_interval} sekund...")
            print(f"{'='*100}")
            
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n\nZakończono monitorowanie kursów.")
        sys.exit(0)


if __name__ == "__main__":
    main()

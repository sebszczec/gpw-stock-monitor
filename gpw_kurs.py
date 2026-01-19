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
import select
import tty
import termios
from datetime import datetime
from collections import defaultdict
import configparser

# Import Rich components
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich.text import Text
    from rich import box
    from rich.align import Align
except ImportError:
    print("Installing rich library...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich.text import Text
    from rich import box
    from rich.align import Align

try:
    import plotext as plt
except ImportError:
    print("Installing plotext library...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotext"])
    import plotext as plt

# Initialize Rich console
console = Console()


def wait_for_key_or_timeout(timeout):
    """
    Waits for 'c' key press or timeout.
    
    Args:
        timeout: Time to wait in seconds
    
    Returns:
        True if 'c' was pressed, False if timeout
    """
    start_time = time.time()
    remaining = timeout
    
    # Save terminal settings
    old_settings = termios.tcgetattr(sys.stdin)
    
    try:
        # Set terminal to raw mode (no echo, no buffering)
        tty.setcbreak(sys.stdin.fileno())
        
        while remaining > 0:
            # Create countdown text with Rich styling
            countdown_text = Text()
            countdown_text.append("⏱️  Next update in ", style="bold cyan")
            countdown_text.append(f"{int(remaining)}", style="bold yellow")
            countdown_text.append(" seconds... ", style="bold cyan")
            countdown_text.append("(Press 'c' to see charts)", style="italic bright_black")
            
            console.print(countdown_text, end='\r')
            
            # Check if there's input available (non-blocking)
            if select.select([sys.stdin], [], [], 1)[0]:
                key = sys.stdin.read(1)
                if key.lower() == 'c':
                    console.print()  # New line
                    return True
            
            elapsed = time.time() - start_time
            remaining = timeout - elapsed
        
        console.print()  # New line after countdown
        return False
    finally:
        # Restore terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


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
            console.print(f"[yellow]⚠️  Warning: Error loading configuration: {e}[/yellow]")
            console.print("[yellow]Using default settings.[/yellow]")
            return defaults
    else:
        console.print(f"[yellow]⚠️  Warning: config.ini file not found, using default settings.[/yellow]")
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
        console.print(f"[red]❌ Error: File '{filename}' not found[/red]")
        return None
    except Exception as e:
        console.print(f"[red]❌ Error reading file: {e}[/red]")
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
    
    # Display chart title with Rich
    chart_title = f"📈 Price Chart: {stock_symbol.replace('.WA', '')} ({currency})"
    console.print(Panel(
        chart_title,
        style="bold cyan",
        border_style="cyan"
    ))
    
    # Create chart in terminal
    plt.clf()
    plt.plot(indices, prices, marker="braille")
    plt.title(f"Price Chart {stock_symbol.replace('.WA', '')}")
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
            console.print("[dim yellow]Note: Returning closing price from previous session[/dim yellow]")
        
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
        console.print(f"[red]❌ Error fetching data: {e}[/red]")
        return None


def main():
    if len(sys.argv) != 2:
        console.print(Panel.fit(
            "[bold cyan]GPW Stock Price Monitor[/bold cyan]\n\n"
            "[yellow]Usage:[/yellow] [bold]python gpw_kurs.py STOCKS_FILE[/bold]\n"
            "[yellow]Example:[/yellow] [bold]python gpw_kurs.py akcje.txt[/bold]\n\n"
            "[dim]File format: one stock symbol per line[/dim]\n"
            "[dim]Example file contents:[/dim]\n"
            "  [green]PKO[/green]\n"
            "  [green]PKNORLEN[/green]\n"
            "  [green]KGHM[/green]",
            border_style="blue",
            title="📊 Help"
        ))
        sys.exit(1)
    
    stocks_file = sys.argv[1]
    
    # Display header
    console.print("\n[bold cyan]═" * 50 + "[/bold cyan]")
    console.print(Align.center("[bold magenta]📈 GPW Stock Price Monitor 📈[/bold magenta]"))
    console.print("[bold cyan]═" * 50 + "[/bold cyan]\n")
    
    # Load configuration
    config = load_config()
    refresh_interval = config['refresh_interval']
    max_history = config['max_history']
    
    console.print(f"[cyan]📂 Loading stock list from file:[/cyan] [bold]{stocks_file}[/bold]")
    stocks = load_stocks_from_file(stocks_file)
    
    if not stocks:
        console.print("[red]❌ Failed to load stock list.[/red]")
        sys.exit(1)
    
    if len(stocks) == 0:
        console.print("[red]❌ File contains no stock symbols.[/red]")
        sys.exit(1)
    
    console.print(f"[green]✅ Found {len(stocks)} stocks:[/green] [bold]{', '.join(stocks.keys())}[/bold]")
    console.print(f"\n[cyan]⏱️  Refresh interval:[/cyan] [bold yellow]{refresh_interval} seconds[/bold yellow]")
    console.print("[dim]Press Ctrl+C to stop.[/dim]\n")
    
    # Dictionary to store price history for each stock
    history = defaultdict(list)
    
    try:
        while True:
            current_time = datetime.now()
            time_str = current_time.strftime("%H:%M:%S")
            time_full = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Create a Rich table
            table = Table(
                title=f"📊 Stock Prices Update - {time_full}",
                title_style="bold cyan",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold magenta",
                border_style="blue",
                expand=False
            )
            
            # Add columns
            table.add_column("Symbol", style="cyan", no_wrap=True, width=15)
            table.add_column("Price", justify="right", style="yellow", width=12)
            table.add_column("Currency", justify="center", style="dim", width=8)
            table.add_column("Company Name", style="white", width=30)
            table.add_column("P/L %", justify="right", width=10)
            table.add_column("P/L Amount", justify="right", width=15)
            
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
                    
                    # Calculate profit/loss
                    percent, amount, is_profit = calculate_profit_loss(price, purchase_price)
                    
                    if percent is not None:
                        if is_profit:
                            pl_percent = f"[green]+{percent:.2f}%[/green]"
                            pl_amount = f"[green]+{amount:.2f} {currency}[/green]"
                        else:
                            pl_percent = f"[red]{percent:.2f}%[/red]"
                            pl_amount = f"[red]{amount:.2f} {currency}[/red]"
                    else:
                        pl_percent = "[dim]-[/dim]"
                        pl_amount = "[dim]-[/dim]"
                    
                    table.add_row(
                        result['symbol'].replace('.WA', ''),
                        f"{price:.2f}",
                        currency,
                        result['name'][:30],
                        pl_percent,
                        pl_amount
                    )
                else:
                    table.add_row(
                        stock_symbol,
                        "[red]ERROR[/red]",
                        "-",
                        "[red]Failed to fetch price[/red]",
                        "[dim]-[/dim]",
                        "[dim]-[/dim]"
                    )
            
            # Display the table
            console.print("\n")
            console.print(table)
            console.print("\n")
            
            # Wait for key press or timeout
            show_charts = wait_for_key_or_timeout(refresh_interval)
            
            # Draw charts only if user pressed 'C'
            if show_charts:
                console.print(Panel.fit(
                    "[bold cyan]📈 Displaying Price Charts 📈[/bold cyan]",
                    border_style="cyan"
                ))
                console.print()
                
                for stock_symbol in stocks.keys():
                    if stock_symbol in history and len(history[stock_symbol]) >= 2:
                        # Get currency from last read
                        result = get_stock_price(stock_symbol)
                        currency = result['currency'] if result else 'PLN'
                        draw_chart(history[stock_symbol], stock_symbol, config, currency)
                        console.print()
            
    except KeyboardInterrupt:
        console.print("\n\n[yellow]👋 Stopped monitoring prices.[/yellow]\n")
        sys.exit(0)


if __name__ == "__main__":
    main()

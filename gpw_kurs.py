#!/usr/bin/env python3
"""
Program for fetching stock prices from GPW (Warsaw Stock Exchange)
Usage: python gpw_kurs.py STOCKS_FILE
Example: python gpw_kurs.py akcje.txt
Program checks prices every configurable interval and displays them on screen.
"""

import sys
import time
from datetime import datetime

# Import local modules
from config import Config, load_stocks_from_file
from data_fetcher import StockDataFetcher, PriceHistory
from input_handler import NavigationHandler, InputAction, check_key_nonblocking, wait_for_escape
from ui_display import UIDisplay, StockTableBuilder, ChartDisplay
from calculations import calculate_profit_loss

# Import Rich components
try:
    from rich.console import Console
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn
except ImportError:
    print("Installing rich library...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn

# Initialize Rich console
console = Console()




def main():
    """Main application loop."""
    if len(sys.argv) != 2:
        UIDisplay.show_help()
        sys.exit(1)
    
    stocks_file = sys.argv[1]
    
    # Display header
    UIDisplay.show_header()
    
    # Load configuration
    config = Config()
    refresh_interval = config['refresh_interval']
    
    # Load stocks
    console.print(f"[cyan]📂 Loading stock list from file:[/cyan] [bold]{stocks_file}[/bold]")
    stocks = load_stocks_from_file(stocks_file)
    
    if not stocks:
        UIDisplay.show_error("Failed to load stock list.")
        sys.exit(1)
    
    if len(stocks) == 0:
        UIDisplay.show_error("File contains no stock symbols.")
        sys.exit(1)
    
    UIDisplay.show_loading_info(stocks_file, stocks, refresh_interval)
    
    # Initialize components
    history = PriceHistory(max_history=config['max_history'])
    navigation = NavigationHandler(list(stocks.keys()))
    fetcher = StockDataFetcher()
    
    # Clear screen once at the start
    UIDisplay.clear_and_home()
    
    try:
        with Live(console=console, refresh_per_second=30, screen=True) as live:
            next_update_time = time.time() + refresh_interval
            current_table = None
            last_action_time = time.time()
            last_stock_data = {}  # Store last fetched stock data for navigation
            
            while True:
                now = time.time()
                
                # Check if it's time to refresh data
                if now >= next_update_time or current_table is None:
                    current_time = datetime.now()
                    time_str = current_time.strftime("%H:%M:%S")
                    time_full = current_time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Create table
                    current_table = StockTableBuilder.create_table(f"📊 Stock Prices Update - {time_full}")
                    
                    # Fetch and display stock data
                    row_index = 0
                    for stock_symbol, purchase_price in stocks.items():
                        stock_data = fetcher.get_stock_price(stock_symbol)
                        
                        if stock_data:
                            # Store for later use during navigation
                            last_stock_data[stock_symbol] = stock_data.to_dict()
                        
                        if stock_data:
                            # Add to history
                            history.add(stock_symbol, time_str, stock_data.price)
                            
                            # Calculate profit/loss
                            profit_loss = calculate_profit_loss(stock_data.price, purchase_price)
                            
                            # Add row to table
                            is_selected = (row_index == navigation.get_selected_index())
                            StockTableBuilder.add_stock_row(
                                current_table, stock_data.to_dict(), purchase_price, profit_loss, is_selected
                            )
                        else:
                            is_selected = (row_index == navigation.get_selected_index())
                            StockTableBuilder.add_error_row(current_table, stock_symbol, is_selected)
                        
                        row_index += 1
                    
                    next_update_time = now + refresh_interval
                
                # Calculate remaining time for progress bar
                remaining_time = max(0, next_update_time - now)
                
                # Create progress bar
                progress_bar = UIDisplay.create_refresh_progress_bar(remaining_time, refresh_interval)
                
                # Combine table and progress bar
                from rich.console import Group
                display_group = Group(current_table, progress_bar)
                
                # Update live display
                live.update(display_group)
                
                # Check for key press (non-blocking)
                action = check_key_nonblocking(navigation)
                
                if action == InputAction.NAVIGATE_UP or action == InputAction.NAVIGATE_DOWN:
                    # Rebuild table with new selection immediately
                    current_time = datetime.now()
                    time_full = current_time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    current_table = StockTableBuilder.create_table(f"📊 Stock Prices Update - {time_full}")
                    
                    row_index = 0
                    for stock_symbol, purchase_price in stocks.items():
                        # Use last fetched stock data
                        if stock_symbol in last_stock_data:
                            stock_info = last_stock_data[stock_symbol]
                            profit_loss = calculate_profit_loss(stock_info['price'], purchase_price)
                            
                            is_selected = (row_index == navigation.get_selected_index())
                            StockTableBuilder.add_stock_row(
                                current_table, stock_info, purchase_price, profit_loss, is_selected
                            )
                        else:
                            is_selected = (row_index == navigation.get_selected_index())
                            StockTableBuilder.add_error_row(current_table, stock_symbol, is_selected)
                        
                        row_index += 1
                
                elif action == InputAction.SHOW_CHART:
                    live.stop()
                    selected_stock = navigation.get_selected_stock()
                    
                    if history.has_enough_data(selected_stock):
                        UIDisplay.clear()
                        
                        # Get currency from last read
                        stock_data = fetcher.get_stock_price(selected_stock)
                        currency = stock_data.currency if stock_data else 'PLN'
                        
                        ChartDisplay.draw_chart(
                            history.get(selected_stock), 
                            selected_stock, 
                            config, 
                            currency
                        )
                        console.print()
                        
                        # Wait for ESC to return
                        wait_for_escape()
                        UIDisplay.clear_and_home()
                    else:
                        UIDisplay.show_warning("Not enough data to show chart yet.")
                        time.sleep(1)
                        UIDisplay.clear_and_home()
                    
                    live.start()
            
    except KeyboardInterrupt:
        UIDisplay.show_goodbye()
        sys.exit(0)


if __name__ == "__main__":
    main()

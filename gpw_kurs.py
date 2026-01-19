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
from input_handler import NavigationHandler, InputAction, wait_for_key_or_timeout, wait_for_escape
from ui_display import UIDisplay, StockTableBuilder, ChartDisplay
from calculations import calculate_profit_loss

# Import Rich components
try:
    from rich.console import Console
except ImportError:
    print("Installing rich library...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console

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
    
    try:
        first_run = True
        while True:
            current_time = datetime.now()
            time_str = current_time.strftime("%H:%M:%S")
            time_full = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Create table
            table = StockTableBuilder.create_table(f"📊 Stock Prices Update - {time_full}")
            
            # Fetch and display stock data
            row_index = 0
            for stock_symbol, purchase_price in stocks.items():
                stock_data = fetcher.get_stock_price(stock_symbol)
                
                if stock_data:
                    # Add to history
                    history.add(stock_symbol, time_str, stock_data.price)
                    
                    # Calculate profit/loss
                    profit_loss = calculate_profit_loss(stock_data.price, purchase_price)
                    
                    # Add row to table
                    is_selected = (row_index == navigation.get_selected_index())
                    StockTableBuilder.add_stock_row(
                        table, stock_data.to_dict(), purchase_price, profit_loss, is_selected
                    )
                else:
                    is_selected = (row_index == navigation.get_selected_index())
                    StockTableBuilder.add_error_row(table, stock_symbol, is_selected)
                
                row_index += 1
            
            # Display the table - use smooth refresh
            if not first_run:
                UIDisplay.move_cursor_home()
            first_run = False
            console.print(table)
            console.print()
            
            # Wait for input
            action = wait_for_key_or_timeout(refresh_interval, navigation)
            
            # Handle chart display
            if action == InputAction.SHOW_CHART:
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
                    UIDisplay.clear()
                else:
                    UIDisplay.show_warning("Not enough data to show chart yet.")
                    time.sleep(1)
            
    except KeyboardInterrupt:
        UIDisplay.show_goodbye()
        sys.exit(0)


if __name__ == "__main__":
    main()

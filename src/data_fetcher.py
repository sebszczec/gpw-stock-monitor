"""
Data fetching module for GPW Stock Monitor.
Handles fetching stock data from Yahoo Finance API.
"""

try:
    import yfinance as yf
except ImportError:
    print("Installing yfinance library...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance"])
    import yfinance as yf

from rich.console import Console

console = Console()


class StockData:
    """Represents stock data with price and metadata."""
    
    def __init__(self, symbol, name, price, currency):
        self.symbol = symbol
        self.name = name
        self.price = price
        self.currency = currency
    
    def to_dict(self):
        """Convert to dictionary format for backward compatibility."""
        return {
            'symbol': self.symbol,
            'name': self.name,
            'price': self.price,
            'currency': self.currency
        }


class StockDataFetcher:
    """Fetches stock price data from Yahoo Finance."""
    
    @staticmethod
    def normalize_symbol(stock_symbol):
        """
        Normalize stock symbol by adding .WA suffix if needed.
        
        Args:
            stock_symbol: Stock symbol (e.g. 'PKO', 'PKNORLEN')
        
        Returns:
            Normalized symbol with .WA suffix
        """
        if not stock_symbol.endswith('.WA'):
            return f"{stock_symbol}.WA"
        return stock_symbol
    
    @staticmethod
    def get_stock_price(stock_symbol):
        """
        Fetches current stock price from GPW.
        
        Args:
            stock_symbol: Stock symbol (e.g. 'PKO', 'PKNORLEN')
        
        Returns:
            StockData object or None in case of error
        """
        try:
            symbol = StockDataFetcher.normalize_symbol(stock_symbol)
            
            # Fetch stock data
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Try to get current price from various sources
            price = StockDataFetcher._extract_price(info)
            
            if price:
                currency = info.get('currency', 'PLN')
                full_name = info.get('longName', info.get('shortName', stock_symbol))
                return StockData(symbol, full_name, price, currency)
            else:
                return None
                
        except Exception as e:
            console.print(f"[red]❌ Error fetching data for {stock_symbol}: {e}[/red]")
            return None
    
    @staticmethod
    def _extract_price(info):
        """
        Extract price from stock info dictionary.
        
        Args:
            info: Stock info dictionary from yfinance
        
        Returns:
            Price as float or None
        """
        # Check various possible keys for current price
        if 'currentPrice' in info and info['currentPrice']:
            return info['currentPrice']
        elif 'regularMarketPrice' in info and info['regularMarketPrice']:
            return info['regularMarketPrice']
        elif 'previousClose' in info and info['previousClose']:
            console.print("[dim yellow]Note: Returning closing price from previous session[/dim yellow]")
            return info['previousClose']
        return None


class PriceHistory:
    """Manages price history for stocks."""
    
    def __init__(self, max_history=50):
        """
        Initialize price history manager.
        
        Args:
            max_history: Maximum number of price points to keep
        """
        self.max_history = max_history
        self._history = {}
    
    def add(self, stock_symbol, time_str, price):
        """
        Add a price point to history.
        
        Args:
            stock_symbol: Stock symbol
            time_str: Time string
            price: Price value
        """
        if stock_symbol not in self._history:
            self._history[stock_symbol] = []
        
        self._history[stock_symbol].append((time_str, price))
        
        # Keep only the last measurements according to config
        if len(self._history[stock_symbol]) > self.max_history:
            self._history[stock_symbol].pop(0)
    
    def get(self, stock_symbol):
        """
        Get price history for a stock.
        
        Args:
            stock_symbol: Stock symbol
        
        Returns:
            List of (time, price) tuples
        """
        return self._history.get(stock_symbol, [])
    
    def has_enough_data(self, stock_symbol, min_points=2):
        """
        Check if there's enough data for a stock.
        
        Args:
            stock_symbol: Stock symbol
            min_points: Minimum number of points required
        
        Returns:
            True if enough data exists
        """
        return len(self.get(stock_symbol)) >= min_points
    
    def __contains__(self, stock_symbol):
        """Support 'in' operator."""
        return stock_symbol in self._history

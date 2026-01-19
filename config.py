"""
Configuration management module for GPW Stock Monitor.
Handles loading and managing application configuration.
"""

import os
import configparser
from rich.console import Console

console = Console()


class Config:
    """Configuration manager for the application."""
    
    DEFAULT_SETTINGS = {
        'refresh_interval': 30,
        'max_history': 50,
        'plot_width': 100,
        'plot_height': 20
    }
    
    def __init__(self, config_file='config.ini'):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.settings = self._load()
    
    def _load(self):
        """
        Loads configuration from config.ini file.
        
        Returns:
            Dictionary with configuration settings
        """
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), self.config_file)
        
        if os.path.exists(config_path):
            try:
                config.read(config_path)
                return {
                    'refresh_interval': config.getint('Settings', 'refresh_interval', 
                                                     fallback=self.DEFAULT_SETTINGS['refresh_interval']),
                    'max_history': config.getint('Settings', 'max_history', 
                                                 fallback=self.DEFAULT_SETTINGS['max_history']),
                    'plot_width': config.getint('Settings', 'plot_width', 
                                                fallback=self.DEFAULT_SETTINGS['plot_width']),
                    'plot_height': config.getint('Settings', 'plot_height', 
                                                 fallback=self.DEFAULT_SETTINGS['plot_height'])
                }
            except Exception as e:
                return self.DEFAULT_SETTINGS.copy()
        else:
            return self.DEFAULT_SETTINGS.copy()
    
    def get(self, key, default=None):
        """Get configuration value by key."""
        return self.settings.get(key, default)
    
    def __getitem__(self, key):
        """Allow dictionary-style access."""
        return self.settings[key]
    
    def __contains__(self, key):
        """Support 'in' operator."""
        return key in self.settings


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

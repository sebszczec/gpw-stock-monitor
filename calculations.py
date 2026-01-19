"""
Calculations module for GPW Stock Monitor.
Handles financial calculations like profit/loss.
"""


def calculate_profit_loss(current_price, purchase_price):
    """
    Calculates profit/loss in percentage and absolute value.
    
    Args:
        current_price: Current stock price
        purchase_price: Stock purchase price
    
    Returns:
        Tuple (percent_change, amount_change, is_profit)
        Returns (None, None, None) if purchase_price is 0.00
    """
    if purchase_price == 0.00:
        return None, None, None
    
    amount_change = current_price - purchase_price
    percent_change = (amount_change / purchase_price) * 100
    is_profit = amount_change >= 0
    
    return percent_change, amount_change, is_profit


class ProfitLossCalculator:
    """Calculator for profit/loss analysis."""
    
    @staticmethod
    def calculate(current_price, purchase_price):
        """
        Calculate profit/loss for a stock.
        
        Args:
            current_price: Current stock price
            purchase_price: Stock purchase price
        
        Returns:
            Tuple (percent_change, amount_change, is_profit)
        """
        return calculate_profit_loss(current_price, purchase_price)
    
    @staticmethod
    def format_percentage(percent_change, is_profit):
        """
        Format percentage change for display.
        
        Args:
            percent_change: Percentage change
            is_profit: Whether it's a profit
        
        Returns:
            Formatted string
        """
        if percent_change is None:
            return "-"
        
        sign = "+" if is_profit else ""
        return f"{sign}{percent_change:.2f}%"
    
    @staticmethod
    def format_amount(amount_change, currency, is_profit):
        """
        Format amount change for display.
        
        Args:
            amount_change: Amount change
            currency: Currency symbol
            is_profit: Whether it's a profit
        
        Returns:
            Formatted string
        """
        if amount_change is None:
            return "-"
        
        sign = "+" if is_profit else ""
        return f"{sign}{amount_change:.2f} {currency}"

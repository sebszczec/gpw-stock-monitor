"""
Unit tests for data_fetcher module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.data_fetcher import StockData, StockDataFetcher, PriceHistory


class TestStockData(unittest.TestCase):
    """Tests for StockData class."""
    
    def test_init(self):
        """Test StockData initialization."""
        stock = StockData("PKO.WA", "PKO Bank Polski", 45.67, "PLN")
        
        self.assertEqual(stock.symbol, "PKO.WA")
        self.assertEqual(stock.name, "PKO Bank Polski")
        self.assertEqual(stock.price, 45.67)
        self.assertEqual(stock.currency, "PLN")
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        stock = StockData("PKO.WA", "PKO Bank Polski", 45.67, "PLN")
        result = stock.to_dict()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['symbol'], "PKO.WA")
        self.assertEqual(result['name'], "PKO Bank Polski")
        self.assertEqual(result['price'], 45.67)
        self.assertEqual(result['currency'], "PLN")


class TestStockDataFetcher(unittest.TestCase):
    """Tests for StockDataFetcher class."""
    
    def test_normalize_symbol_without_suffix(self):
        """Test normalizing symbol without .WA suffix."""
        result = StockDataFetcher.normalize_symbol("PKO")
        self.assertEqual(result, "PKO.WA")
    
    def test_normalize_symbol_with_suffix(self):
        """Test normalizing symbol that already has .WA suffix."""
        result = StockDataFetcher.normalize_symbol("PKO.WA")
        self.assertEqual(result, "PKO.WA")
    
    def test_normalize_symbol_empty(self):
        """Test normalizing empty symbol."""
        result = StockDataFetcher.normalize_symbol("")
        self.assertEqual(result, ".WA")
    
    @patch('src.data_fetcher.yf.Ticker')
    def test_get_stock_price_success(self, mock_ticker):
        """Test successful stock price fetch."""
        # Mock yfinance response
        mock_stock = Mock()
        mock_stock.info = {
            'currentPrice': 45.67,
            'currency': 'PLN',
            'longName': 'PKO Bank Polski SA'
        }
        mock_ticker.return_value = mock_stock
        
        result = StockDataFetcher.get_stock_price("PKO")
        
        self.assertIsInstance(result, StockData)
        self.assertEqual(result.symbol, "PKO.WA")
        self.assertEqual(result.price, 45.67)
        self.assertEqual(result.currency, "PLN")
        self.assertEqual(result.name, "PKO Bank Polski SA")
    
    @patch('src.data_fetcher.yf.Ticker')
    def test_get_stock_price_no_price(self, mock_ticker):
        """Test stock price fetch when no price available."""
        # Mock yfinance response without price
        mock_stock = Mock()
        mock_stock.info = {
            'currency': 'PLN',
            'longName': 'PKO Bank Polski SA'
        }
        mock_ticker.return_value = mock_stock
        
        result = StockDataFetcher.get_stock_price("PKO")
        
        self.assertIsNone(result)
    
    @patch('src.data_fetcher.yf.Ticker')
    def test_get_stock_price_exception(self, mock_ticker):
        """Test stock price fetch with exception."""
        mock_ticker.side_effect = Exception("Network error")
        
        result = StockDataFetcher.get_stock_price("PKO")
        
        self.assertIsNone(result)
    
    def test_extract_price_with_current_price(self):
        """Test extracting price from info with currentPrice."""
        info = {'currentPrice': 45.67}
        result = StockDataFetcher._extract_price(info)
        self.assertEqual(result, 45.67)
    
    def test_extract_price_with_regular_market_price(self):
        """Test extracting price from info with regularMarketPrice."""
        info = {'regularMarketPrice': 48.90}
        result = StockDataFetcher._extract_price(info)
        self.assertEqual(result, 48.90)
    
    def test_extract_price_with_previous_close(self):
        """Test extracting price from info with previousClose."""
        info = {'previousClose': 44.55}
        result = StockDataFetcher._extract_price(info)
        self.assertEqual(result, 44.55)
    
    def test_extract_price_no_price(self):
        """Test extracting price when no price available."""
        info = {'currency': 'PLN'}
        result = StockDataFetcher._extract_price(info)
        self.assertIsNone(result)


class TestPriceHistory(unittest.TestCase):
    """Tests for PriceHistory class."""
    
    def test_init(self):
        """Test PriceHistory initialization."""
        history = PriceHistory(max_history=10)
        self.assertEqual(history.max_history, 10)
        self.assertEqual(history._history, {})
    
    def test_init_default_max_history(self):
        """Test PriceHistory with default max_history."""
        history = PriceHistory()
        self.assertEqual(history.max_history, 50)
    
    def test_add_single_entry(self):
        """Test adding a single price entry."""
        history = PriceHistory(max_history=10)
        history.add("PKO", "10:00:00", 45.67)
        
        self.assertIn("PKO", history)
        result = history.get("PKO")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "10:00:00")
        self.assertEqual(result[0][1], 45.67)
    
    def test_add_multiple_entries(self):
        """Test adding multiple price entries."""
        history = PriceHistory(max_history=10)
        history.add("PKO", "10:00:00", 45.67)
        history.add("PKO", "10:30:00", 46.00)
        history.add("PKO", "11:00:00", 45.80)
        
        result = history.get("PKO")
        self.assertEqual(len(result), 3)
    
    def test_add_max_history_limit(self):
        """Test that history respects max_history limit."""
        history = PriceHistory(max_history=3)
        history.add("PKO", "10:00:00", 45.67)
        history.add("PKO", "10:30:00", 46.00)
        history.add("PKO", "11:00:00", 45.80)
        history.add("PKO", "11:30:00", 46.50)
        
        # Should only keep last 3 entries
        result = history.get("PKO")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][0], "10:30:00")
        self.assertEqual(result[-1][0], "11:30:00")
    
    def test_add_multiple_stocks(self):
        """Test adding entries for multiple stocks."""
        history = PriceHistory(max_history=10)
        history.add("PKO", "10:00:00", 45.67)
        history.add("PKNORLEN", "10:00:00", 58.90)
        
        self.assertIn("PKO", history)
        self.assertIn("PKNORLEN", history)
        self.assertEqual(history.get("PKO")[0][1], 45.67)
        self.assertEqual(history.get("PKNORLEN")[0][1], 58.90)
    
    def test_get_existing_stock(self):
        """Test getting history for existing stock."""
        history = PriceHistory(max_history=10)
        history.add("PKO", "10:00:00", 45.67)
        history.add("PKO", "10:30:00", 46.00)
        
        result = history.get("PKO")
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
    
    def test_get_non_existing_stock(self):
        """Test getting history for non-existing stock."""
        history = PriceHistory(max_history=10)
        result = history.get("NONEXISTENT")
        
        self.assertEqual(result, [])
    
    def test_has_enough_data_true(self):
        """Test has_enough_data for stock with sufficient history."""
        history = PriceHistory(max_history=10)
        history.add("PKO", "10:00:00", 45.67)
        history.add("PKO", "10:30:00", 46.00)
        
        self.assertTrue(history.has_enough_data("PKO", 2))
    
    def test_has_enough_data_false(self):
        """Test has_enough_data for stock without sufficient history."""
        history = PriceHistory(max_history=10)
        history.add("PKO", "10:00:00", 45.67)
        
        self.assertFalse(history.has_enough_data("PKO", 2))
    
    def test_has_enough_data_default_min_points(self):
        """Test has_enough_data with default min_points."""
        history = PriceHistory(max_history=10)
        history.add("PKO", "10:00:00", 45.67)
        history.add("PKO", "10:30:00", 46.00)
        
        self.assertTrue(history.has_enough_data("PKO"))
    
    def test_contains_operator(self):
        """Test 'in' operator."""
        history = PriceHistory(max_history=10)
        history.add("PKO", "10:00:00", 45.67)
        
        self.assertTrue("PKO" in history)
        self.assertFalse("NONEXISTENT" in history)


if __name__ == '__main__':
    unittest.main()

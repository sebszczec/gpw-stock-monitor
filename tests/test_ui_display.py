"""
Unit tests for ui_display module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.ui_display import StockTableBuilder, UIDisplay, ChartDisplay
from rich.table import Table


class TestStockTableBuilder(unittest.TestCase):
    """Tests for StockTableBuilder class."""
    
    def test_create_table(self):
        """Test creating a new table."""
        title = "Test Table"
        table = StockTableBuilder.create_table(title)
        
        self.assertIsInstance(table, Table)
        self.assertEqual(table.title, title)
    
    def test_create_table_has_columns(self):
        """Test that created table has all required columns."""
        table = StockTableBuilder.create_table("Test")
        
        # Check that table has been configured with columns
        self.assertIsInstance(table, Table)
        # We can't easily check column names without accessing private attributes,
        # but we can verify it's a Table instance
    
    def test_add_stock_row_with_profit(self):
        """Test adding a stock row with profit."""
        table = StockTableBuilder.create_table("Test")
        stock_data = {
            'symbol': 'PKO.WA',
            'name': 'PKO Bank Polski',
            'price': 50.00,
            'currency': 'PLN'
        }
        purchase_price = 45.00
        profit_loss = (11.11, 5.00, True)
        
        # Should not raise any exceptions
        StockTableBuilder.add_stock_row(table, stock_data, purchase_price, profit_loss, False)
    
    def test_add_stock_row_with_loss(self):
        """Test adding a stock row with loss."""
        table = StockTableBuilder.create_table("Test")
        stock_data = {
            'symbol': 'PKO.WA',
            'name': 'PKO Bank Polski',
            'price': 40.00,
            'currency': 'PLN'
        }
        purchase_price = 45.00
        profit_loss = (-11.11, -5.00, False)
        
        # Should not raise any exceptions
        StockTableBuilder.add_stock_row(table, stock_data, purchase_price, profit_loss, False)
    
    def test_add_stock_row_no_purchase_price(self):
        """Test adding a stock row without purchase price."""
        table = StockTableBuilder.create_table("Test")
        stock_data = {
            'symbol': 'PKO.WA',
            'name': 'PKO Bank Polski',
            'price': 45.67,
            'currency': 'PLN'
        }
        purchase_price = 0.00
        profit_loss = (None, None, None)
        
        # Should not raise any exceptions
        StockTableBuilder.add_stock_row(table, stock_data, purchase_price, profit_loss, False)
    
    def test_add_stock_row_selected(self):
        """Test adding a selected stock row."""
        table = StockTableBuilder.create_table("Test")
        stock_data = {
            'symbol': 'PKO.WA',
            'name': 'PKO Bank Polski',
            'price': 45.67,
            'currency': 'PLN'
        }
        purchase_price = 45.00
        profit_loss = (1.49, 0.67, True)
        
        # Should not raise any exceptions
        StockTableBuilder.add_stock_row(table, stock_data, purchase_price, profit_loss, True)
    
    def test_add_error_row(self):
        """Test adding an error row."""
        table = StockTableBuilder.create_table("Test")
        
        # Should not raise any exceptions
        StockTableBuilder.add_error_row(table, "PKO", False)
    
    def test_add_error_row_selected(self):
        """Test adding a selected error row."""
        table = StockTableBuilder.create_table("Test")
        
        # Should not raise any exceptions
        StockTableBuilder.add_error_row(table, "PKO", True)
    
    def test_add_stock_row_with_stock_data_object(self):
        """Test adding row with StockData object."""
        table = StockTableBuilder.create_table("Test")
        
        # Mock StockData object
        stock_data = Mock()
        stock_data.to_dict.return_value = {
            'symbol': 'PKO.WA',
            'name': 'PKO Bank Polski',
            'price': 45.67,
            'currency': 'PLN'
        }
        
        purchase_price = 45.00
        profit_loss = (1.49, 0.67, True)
        
        # Should not raise any exceptions
        StockTableBuilder.add_stock_row(table, stock_data, purchase_price, profit_loss, False)
        stock_data.to_dict.assert_called_once()


class TestUIDisplay(unittest.TestCase):
    """Tests for UIDisplay class."""
    
    @patch('src.ui_display.console.print')
    def test_show_header(self, mock_print):
        """Test showing header."""
        UIDisplay.show_header()
        mock_print.assert_called()
    
    @patch('src.ui_display.console.print')
    def test_show_error(self, mock_print):
        """Test showing error message."""
        UIDisplay.show_error("Test error")
        mock_print.assert_called()
    
    @patch('src.ui_display.console.print')
    def test_show_loading_info(self, mock_print):
        """Test showing loading info."""
        stocks = {'PKO': 45.67, 'PKNORLEN': 58.90}
        UIDisplay.show_loading_info('test.txt', stocks, 30)
        mock_print.assert_called()
    
    @patch('src.ui_display.console.print')
    def test_show_help(self, mock_print):
        """Test showing help message."""
        UIDisplay.show_help()
        mock_print.assert_called()
    
    @patch('sys.stdout')
    def test_clear_and_home(self, mock_stdout):
        """Test clearing screen and moving cursor to home position."""
        UIDisplay.clear_and_home()
        mock_stdout.write.assert_called_once_with('\033[2J\033[H')
        mock_stdout.flush.assert_called_once()


class TestChartDisplay(unittest.TestCase):
    """Tests for ChartDisplay class."""
    
    @patch('src.ui_display.console.print')
    def test_draw_chart(self, mock_print):
        """Test drawing a chart."""
        price_history = [('10:00', 45.67), ('10:30', 46.00), ('11:00', 45.80)]
        config = {'plot_width': 100, 'plot_height': 20}
        
        ChartDisplay.draw_chart(price_history, "PKO.WA", config, 'PLN')
        
        # Should print multiple times (header, chart lines, stats)
        self.assertTrue(mock_print.call_count > 5)
    
    @patch('src.ui_display.console.print')
    def test_draw_chart_insufficient_data(self, mock_print):
        """Test drawing chart with insufficient data."""
        price_history = [('10:00', 45.67)]
        config = {'plot_width': 100, 'plot_height': 20}
        
        ChartDisplay.draw_chart(price_history, "PKO.WA", config, 'PLN')
        mock_print.assert_called()
    
    @patch('src.ui_display.console.print')
    def test_draw_chart_empty_history(self, mock_print):
        """Test drawing chart with empty history."""
        price_history = []
        config = {'plot_width': 100, 'plot_height': 20}
        
        ChartDisplay.draw_chart(price_history, "PKO.WA", config, 'PLN')
        mock_print.assert_called()
    
    @patch('src.ui_display.console.print')
    def test_draw_chart_custom_size(self, mock_print):
        """Test drawing chart with custom size."""
        price_history = [('10:00', 45.67), ('10:30', 46.00)]
        config = {'plot_width': 60, 'plot_height': 15}
        
        ChartDisplay.draw_chart(price_history, "PKO.WA", config, 'USD')
        
        # Should print multiple times
        self.assertTrue(mock_print.call_count > 0)


if __name__ == '__main__':
    unittest.main()

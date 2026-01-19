"""
Unit tests for config module.
"""

import unittest
import os
import tempfile
from unittest.mock import patch, mock_open
from src.config import Config, load_stocks_from_file


class TestConfig(unittest.TestCase):
    """Tests for Config class."""
    
    def test_default_settings(self):
        """Test default settings values."""
        self.assertEqual(Config.DEFAULT_SETTINGS['refresh_interval'], 30)
        self.assertEqual(Config.DEFAULT_SETTINGS['max_history'], 50)
        self.assertEqual(Config.DEFAULT_SETTINGS['plot_width'], 100)
        self.assertEqual(Config.DEFAULT_SETTINGS['plot_height'], 20)
    
    @patch('os.path.exists')
    def test_init_no_config_file(self, mock_exists):
        """Test initialization when config file doesn't exist."""
        mock_exists.return_value = False
        
        config = Config('config.ini')
        
        self.assertEqual(config.settings, Config.DEFAULT_SETTINGS)
    
    def test_get_method(self):
        """Test get method."""
        config = Config()
        
        result = config.get('refresh_interval')
        self.assertIsNotNone(result)
        
        result = config.get('nonexistent', 'default_value')
        self.assertEqual(result, 'default_value')
    
    def test_getitem_method(self):
        """Test dictionary-style access."""
        config = Config()
        
        result = config['refresh_interval']
        self.assertIsNotNone(result)
    
    def test_contains_method(self):
        """Test 'in' operator."""
        config = Config()
        
        self.assertTrue('refresh_interval' in config)
        self.assertFalse('nonexistent_key' in config)
    
    @patch('os.path.exists')
    @patch('configparser.ConfigParser.read')
    @patch('configparser.ConfigParser.getint')
    def test_load_config_from_file(self, mock_getint, mock_read, mock_exists):
        """Test loading configuration from file."""
        mock_exists.return_value = True
        mock_getint.side_effect = [60, 100, 120, 25]  # refresh, max_history, plot_width, plot_height
        
        config = Config('config.ini')
        
        mock_read.assert_called_once()
        self.assertEqual(config.settings['refresh_interval'], 60)
        self.assertEqual(config.settings['max_history'], 100)
        self.assertEqual(config.settings['plot_width'], 120)
        self.assertEqual(config.settings['plot_height'], 25)


class TestLoadStocksFromFile(unittest.TestCase):
    """Tests for load_stocks_from_file function."""
    
    def test_load_stocks_simple_format(self):
        """Test loading stocks with simple format (just symbols)."""
        content = "PKO\nPKNORLEN\nKGHM\n"
        
        with patch('builtins.open', mock_open(read_data=content)):
            result = load_stocks_from_file('test.txt')
        
        self.assertEqual(len(result), 3)
        self.assertIn('PKO', result)
        self.assertIn('PKNORLEN', result)
        self.assertIn('KGHM', result)
        self.assertEqual(result['PKO'], 0.00)
        self.assertEqual(result['PKNORLEN'], 0.00)
        self.assertEqual(result['KGHM'], 0.00)
    
    def test_load_stocks_with_prices(self):
        """Test loading stocks with purchase prices."""
        content = "PKO,45.67\nPKNORLEN,58.90\nKGHM,120.50\n"
        
        with patch('builtins.open', mock_open(read_data=content)):
            result = load_stocks_from_file('test.txt')
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result['PKO'], 45.67)
        self.assertEqual(result['PKNORLEN'], 58.90)
        self.assertEqual(result['KGHM'], 120.50)
    
    def test_load_stocks_mixed_format(self):
        """Test loading stocks with mixed format."""
        content = "PKO,45.67\nPKNORLEN\nKGHM,120.50\n"
        
        with patch('builtins.open', mock_open(read_data=content)):
            result = load_stocks_from_file('test.txt')
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result['PKO'], 45.67)
        self.assertEqual(result['PKNORLEN'], 0.00)
        self.assertEqual(result['KGHM'], 120.50)
    
    def test_load_stocks_skip_empty_lines(self):
        """Test that empty lines are skipped."""
        content = "PKO,45.67\n\nPKNORLEN,58.90\n\n\nKGHM,120.50\n"
        
        with patch('builtins.open', mock_open(read_data=content)):
            result = load_stocks_from_file('test.txt')
        
        self.assertEqual(len(result), 3)
    
    def test_load_stocks_skip_comments(self):
        """Test that comment lines are skipped."""
        content = "# This is a comment\nPKO,45.67\n# Another comment\nPKNORLEN,58.90\n"
        
        with patch('builtins.open', mock_open(read_data=content)):
            result = load_stocks_from_file('test.txt')
        
        self.assertEqual(len(result), 2)
        self.assertIn('PKO', result)
        self.assertIn('PKNORLEN', result)
    
    def test_load_stocks_lowercase_conversion(self):
        """Test that stock symbols are converted to uppercase."""
        content = "pko,45.67\npknorlen,58.90\n"
        
        with patch('builtins.open', mock_open(read_data=content)):
            result = load_stocks_from_file('test.txt')
        
        self.assertIn('PKO', result)
        self.assertIn('PKNORLEN', result)
        self.assertNotIn('pko', result)
        self.assertNotIn('pknorlen', result)
    
    def test_load_stocks_whitespace_handling(self):
        """Test handling of whitespace in file."""
        content = "  PKO  ,  45.67  \n  PKNORLEN  ,  58.90  \n"
        
        with patch('builtins.open', mock_open(read_data=content)):
            result = load_stocks_from_file('test.txt')
        
        self.assertEqual(result['PKO'], 45.67)
        self.assertEqual(result['PKNORLEN'], 58.90)
    
    def test_load_stocks_invalid_price(self):
        """Test handling of invalid price values."""
        content = "PKO,invalid\nPKNORLEN,58.90\n"
        
        with patch('builtins.open', mock_open(read_data=content)):
            result = load_stocks_from_file('test.txt')
        
        self.assertEqual(result['PKO'], 0.00)  # Invalid price defaults to 0.00
        self.assertEqual(result['PKNORLEN'], 58.90)
    
    def test_load_stocks_file_not_found(self):
        """Test handling of non-existent file."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            result = load_stocks_from_file('nonexistent.txt')
        
        self.assertIsNone(result)
    
    def test_load_stocks_empty_file(self):
        """Test loading from empty file."""
        content = ""
        
        with patch('builtins.open', mock_open(read_data=content)):
            result = load_stocks_from_file('test.txt')
        
        self.assertIsNone(result)  # Empty file returns None
    
    def test_load_stocks_only_comments(self):
        """Test loading file with only comments."""
        content = "# Comment 1\n# Comment 2\n# Comment 3\n"
        
        with patch('builtins.open', mock_open(read_data=content)):
            result = load_stocks_from_file('test.txt')
        
        self.assertIsNone(result)  # Only comments returns None
    
    def test_load_stocks_real_file(self):
        """Test loading from a real temporary file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("PKO,45.67\n")
            f.write("PKNORLEN,58.90\n")
            f.write("KGHM\n")
            temp_file = f.name
        
        try:
            result = load_stocks_from_file(temp_file)
            
            self.assertEqual(len(result), 3)
            self.assertEqual(result['PKO'], 45.67)
            self.assertEqual(result['PKNORLEN'], 58.90)
            self.assertEqual(result['KGHM'], 0.00)
        finally:
            os.unlink(temp_file)
    
    def test_load_stocks_unicode(self):
        """Test handling of unicode characters."""
        content = "PKO,45.67\n# Komentarz z polskimi znakami: ąćęłńóśźż\nPKNORLEN,58.90\n"
        
        with patch('builtins.open', mock_open(read_data=content)):
            result = load_stocks_from_file('test.txt')
        
        self.assertEqual(len(result), 2)


if __name__ == '__main__':
    unittest.main()

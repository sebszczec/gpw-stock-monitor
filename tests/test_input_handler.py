"""
Unit tests for input_handler module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.input_handler import InputAction, TerminalInput, NavigationHandler


class TestInputAction(unittest.TestCase):
    """Tests for InputAction enumeration."""
    
    def test_action_values(self):
        """Test that all action values are defined."""
        self.assertEqual(InputAction.NAVIGATE_UP, 'navigate_up')
        self.assertEqual(InputAction.NAVIGATE_DOWN, 'navigate_down')
        self.assertEqual(InputAction.SHOW_CHART, 'show_chart')
        self.assertEqual(InputAction.TIMEOUT, 'timeout')
        self.assertEqual(InputAction.ESCAPE, 'escape')


class TestNavigationHandler(unittest.TestCase):
    """Tests for NavigationHandler class."""
    
    def test_init(self):
        """Test NavigationHandler initialization."""
        stocks = ["PKO", "PKNORLEN", "KGHM"]
        nav = NavigationHandler(stocks)
        
        self.assertEqual(nav.stocks_list, stocks)
        self.assertEqual(nav.selected_index, 0)
    
    def test_init_empty_list(self):
        """Test initialization with empty list."""
        nav = NavigationHandler([])
        
        self.assertEqual(nav.stocks_list, [])
        self.assertEqual(nav.selected_index, 0)
    
    def test_move_down(self):
        """Test moving selection down."""
        stocks = ["PKO", "PKNORLEN", "KGHM"]
        nav = NavigationHandler(stocks)
        
        nav.move_down()
        self.assertEqual(nav.selected_index, 1)
        
        nav.move_down()
        self.assertEqual(nav.selected_index, 2)
    
    def test_move_down_wrap_around(self):
        """Test that move_down wraps around at the end."""
        stocks = ["PKO", "PKNORLEN", "KGHM"]
        nav = NavigationHandler(stocks)
        
        nav.selected_index = 2  # Last item
        nav.move_down()
        self.assertEqual(nav.selected_index, 0)  # Should wrap to first
    
    def test_move_up(self):
        """Test moving selection up."""
        stocks = ["PKO", "PKNORLEN", "KGHM"]
        nav = NavigationHandler(stocks)
        nav.selected_index = 2
        
        nav.move_up()
        self.assertEqual(nav.selected_index, 1)
        
        nav.move_up()
        self.assertEqual(nav.selected_index, 0)
    
    def test_move_up_wrap_around(self):
        """Test that move_up wraps around at the beginning."""
        stocks = ["PKO", "PKNORLEN", "KGHM"]
        nav = NavigationHandler(stocks)
        
        nav.selected_index = 0  # First item
        nav.move_up()
        self.assertEqual(nav.selected_index, 2)  # Should wrap to last
    
    def test_get_selected_stock(self):
        """Test getting currently selected stock."""
        stocks = ["PKO", "PKNORLEN", "KGHM"]
        nav = NavigationHandler(stocks)
        
        self.assertEqual(nav.get_selected_stock(), "PKO")
        
        nav.move_down()
        self.assertEqual(nav.get_selected_stock(), "PKNORLEN")
        
        nav.move_down()
        self.assertEqual(nav.get_selected_stock(), "KGHM")
    
    def test_get_selected_index(self):
        """Test getting currently selected index."""
        stocks = ["PKO", "PKNORLEN", "KGHM"]
        nav = NavigationHandler(stocks)
        
        self.assertEqual(nav.get_selected_index(), 0)
        
        nav.move_down()
        self.assertEqual(nav.get_selected_index(), 1)
    
    def test_navigation_sequence(self):
        """Test a complete navigation sequence."""
        stocks = ["PKO", "PKNORLEN", "KGHM"]
        nav = NavigationHandler(stocks)
        
        # Start at first item
        self.assertEqual(nav.get_selected_stock(), "PKO")
        
        # Move down twice
        nav.move_down()
        nav.move_down()
        self.assertEqual(nav.get_selected_stock(), "KGHM")
        
        # Move down (should wrap)
        nav.move_down()
        self.assertEqual(nav.get_selected_stock(), "PKO")
        
        # Move up (should wrap to last)
        nav.move_up()
        self.assertEqual(nav.get_selected_stock(), "KGHM")
    
    def test_single_item_navigation(self):
        """Test navigation with single item list."""
        stocks = ["PKO"]
        nav = NavigationHandler(stocks)
        
        self.assertEqual(nav.get_selected_stock(), "PKO")
        
        nav.move_down()
        self.assertEqual(nav.get_selected_stock(), "PKO")
        
        nav.move_up()
        self.assertEqual(nav.get_selected_stock(), "PKO")


class TestTerminalInput(unittest.TestCase):
    """Tests for TerminalInput class."""
    
    @patch('src.input_handler.sys.stdin')
    @patch('src.input_handler.termios.tcgetattr')
    @patch('src.input_handler.tty.setcbreak')
    def test_set_raw_mode(self, mock_setcbreak, mock_tcgetattr, mock_stdin):
        """Test setting terminal to raw mode."""
        mock_old_settings = Mock()
        mock_tcgetattr.return_value = mock_old_settings
        mock_stdin.fileno.return_value = 0
        
        result = TerminalInput._set_raw_mode()
        
        mock_tcgetattr.assert_called_once()
        mock_setcbreak.assert_called_once()
        self.assertEqual(result, mock_old_settings)
    
    @patch('src.input_handler.termios.tcsetattr')
    def test_restore_terminal(self, mock_tcsetattr):
        """Test restoring terminal settings."""
        mock_old_settings = Mock()
        
        TerminalInput._restore_terminal(mock_old_settings)
        
        mock_tcsetattr.assert_called_once()
    
    @patch('src.input_handler.select.select')
    @patch('src.input_handler.sys.stdin')
    def test_read_key_with_timeout_key_pressed(self, mock_stdin, mock_select):
        """Test reading key when key is pressed."""
        mock_select.return_value = ([mock_stdin], [], [])
        mock_stdin.read.return_value = 'a'
        
        result = TerminalInput.read_key_with_timeout(5)
        
        self.assertEqual(result, 'a')
    
    @patch('src.input_handler.select.select')
    @patch('src.input_handler.sys.stdin')
    def test_read_key_with_timeout_timeout(self, mock_stdin, mock_select):
        """Test reading key when timeout occurs."""
        mock_select.return_value = ([], [], [])
        
        result = TerminalInput.read_key_with_timeout(5)
        
        self.assertIsNone(result)
    
    @patch('src.input_handler.select.select')
    @patch('src.input_handler.sys.stdin')
    def test_read_key_escape_key(self, mock_stdin, mock_select):
        """Test reading escape key."""
        # First call returns stdin available, second returns nothing (no arrow key)
        mock_select.side_effect = [
            ([mock_stdin], [], []),  # ESC key available
            ([], [], [])              # No follow-up character
        ]
        mock_stdin.read.return_value = '\x1b'
        
        result = TerminalInput.read_key_with_timeout(5)
        
        self.assertEqual(result, '\x1b')
    
    @patch('src.input_handler.select.select')
    @patch('src.input_handler.sys.stdin')
    def test_read_key_arrow_up(self, mock_stdin, mock_select):
        """Test reading arrow up key."""
        mock_select.side_effect = [
            ([mock_stdin], [], []),  # ESC available
            ([mock_stdin], [], []),  # '[' available
            ([mock_stdin], [], [])   # 'A' available
        ]
        mock_stdin.read.side_effect = ['\x1b', '[', 'A']
        
        result = TerminalInput.read_key_with_timeout(5)
        
        self.assertEqual(result, 'w')  # Arrow up converted to 'w'
    
    @patch('src.input_handler.select.select')
    @patch('src.input_handler.sys.stdin')
    def test_read_key_arrow_down(self, mock_stdin, mock_select):
        """Test reading arrow down key."""
        mock_select.side_effect = [
            ([mock_stdin], [], []),  # ESC available
            ([mock_stdin], [], []),  # '[' available
            ([mock_stdin], [], [])   # 'B' available
        ]
        mock_stdin.read.side_effect = ['\x1b', '[', 'B']
        
        result = TerminalInput.read_key_with_timeout(5)
        
        self.assertEqual(result, 's')  # Arrow down converted to 's'


if __name__ == '__main__':
    unittest.main()

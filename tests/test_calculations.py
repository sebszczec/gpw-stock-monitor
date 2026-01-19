"""
Unit tests for calculations module.
"""

import unittest
from calculations import calculate_profit_loss, ProfitLossCalculator


class TestCalculateProfitLoss(unittest.TestCase):
    """Tests for calculate_profit_loss function."""
    
    def test_profit_scenario(self):
        """Test calculation when stock price increased."""
        current_price = 120.00
        purchase_price = 100.00
        
        percent, amount, is_profit = calculate_profit_loss(current_price, purchase_price)
        
        self.assertAlmostEqual(percent, 20.0, places=2)
        self.assertAlmostEqual(amount, 20.0, places=2)
        self.assertTrue(is_profit)
    
    def test_loss_scenario(self):
        """Test calculation when stock price decreased."""
        current_price = 80.00
        purchase_price = 100.00
        
        percent, amount, is_profit = calculate_profit_loss(current_price, purchase_price)
        
        self.assertAlmostEqual(percent, -20.0, places=2)
        self.assertAlmostEqual(amount, -20.0, places=2)
        self.assertFalse(is_profit)
    
    def test_no_change(self):
        """Test calculation when stock price unchanged."""
        current_price = 100.00
        purchase_price = 100.00
        
        percent, amount, is_profit = calculate_profit_loss(current_price, purchase_price)
        
        self.assertAlmostEqual(percent, 0.0, places=2)
        self.assertAlmostEqual(amount, 0.0, places=2)
        self.assertTrue(is_profit)  # Zero change is considered profit
    
    def test_zero_purchase_price(self):
        """Test calculation when purchase price is 0.00."""
        current_price = 100.00
        purchase_price = 0.00
        
        percent, amount, is_profit = calculate_profit_loss(current_price, purchase_price)
        
        self.assertIsNone(percent)
        self.assertIsNone(amount)
        self.assertIsNone(is_profit)
    
    def test_small_profit(self):
        """Test calculation with small profit."""
        current_price = 100.50
        purchase_price = 100.00
        
        percent, amount, is_profit = calculate_profit_loss(current_price, purchase_price)
        
        self.assertAlmostEqual(percent, 0.5, places=2)
        self.assertAlmostEqual(amount, 0.5, places=2)
        self.assertTrue(is_profit)
    
    def test_large_profit(self):
        """Test calculation with large profit."""
        current_price = 500.00
        purchase_price = 100.00
        
        percent, amount, is_profit = calculate_profit_loss(current_price, purchase_price)
        
        self.assertAlmostEqual(percent, 400.0, places=2)
        self.assertAlmostEqual(amount, 400.0, places=2)
        self.assertTrue(is_profit)
    
    def test_decimal_values(self):
        """Test calculation with decimal values."""
        current_price = 45.67
        purchase_price = 38.23
        
        percent, amount, is_profit = calculate_profit_loss(current_price, purchase_price)
        
        expected_amount = 7.44
        expected_percent = (7.44 / 38.23) * 100
        
        self.assertAlmostEqual(amount, expected_amount, places=2)
        self.assertAlmostEqual(percent, expected_percent, places=2)
        self.assertTrue(is_profit)


class TestProfitLossCalculator(unittest.TestCase):
    """Tests for ProfitLossCalculator class."""
    
    def test_calculate_method(self):
        """Test calculate static method."""
        current_price = 150.00
        purchase_price = 100.00
        
        percent, amount, is_profit = ProfitLossCalculator.calculate(current_price, purchase_price)
        
        self.assertAlmostEqual(percent, 50.0, places=2)
        self.assertAlmostEqual(amount, 50.0, places=2)
        self.assertTrue(is_profit)
    
    def test_format_percentage_profit(self):
        """Test formatting percentage for profit."""
        result = ProfitLossCalculator.format_percentage(25.5, True)
        self.assertEqual(result, "+25.50%")
    
    def test_format_percentage_loss(self):
        """Test formatting percentage for loss."""
        result = ProfitLossCalculator.format_percentage(-15.25, False)
        self.assertEqual(result, "-15.25%")
    
    def test_format_percentage_none(self):
        """Test formatting percentage when None."""
        result = ProfitLossCalculator.format_percentage(None, True)
        self.assertEqual(result, "-")
    
    def test_format_amount_profit(self):
        """Test formatting amount for profit."""
        result = ProfitLossCalculator.format_amount(12.50, "PLN", True)
        self.assertEqual(result, "+12.50 PLN")
    
    def test_format_amount_loss(self):
        """Test formatting amount for loss."""
        result = ProfitLossCalculator.format_amount(-8.75, "USD", False)
        self.assertEqual(result, "-8.75 USD")
    
    def test_format_amount_none(self):
        """Test formatting amount when None."""
        result = ProfitLossCalculator.format_amount(None, "PLN", True)
        self.assertEqual(result, "-")
    
    def test_format_percentage_zero(self):
        """Test formatting zero percentage."""
        result = ProfitLossCalculator.format_percentage(0.0, True)
        self.assertEqual(result, "+0.00%")
    
    def test_format_amount_zero(self):
        """Test formatting zero amount."""
        result = ProfitLossCalculator.format_amount(0.0, "EUR", True)
        self.assertEqual(result, "+0.00 EUR")


if __name__ == '__main__':
    unittest.main()

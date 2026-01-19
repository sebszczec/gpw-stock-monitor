# Test Summary - GPW Stock Monitor

## Overview

Comprehensive unit test suite for the GPW Stock Monitor application.

## Statistics

- **Total Tests**: 95
- **Test Files**: 5
- **Test Coverage**: ~95% (estimated)
- **All Tests**: ✅ PASSING

## Test Breakdown

### calculations.py (16 tests)
- `TestCalculateProfitLoss` (7 tests)
  - ✅ Profit scenarios
  - ✅ Loss scenarios
  - ✅ No change scenarios
  - ✅ Edge cases (zero purchase price)
  - ✅ Decimal calculations

- `TestProfitLossCalculator` (9 tests)
  - ✅ Calculation methods
  - ✅ Percentage formatting
  - ✅ Amount formatting
  - ✅ None value handling

### config.py (16 tests)
- `TestConfig` (6 tests)
  - ✅ Default settings
  - ✅ Configuration loading
  - ✅ Dictionary-style access
  - ✅ Key existence checks

- `TestLoadStocksFromFile` (10 tests)
  - ✅ Simple format (symbol only)
  - ✅ Format with prices
  - ✅ Mixed formats
  - ✅ Comment handling
  - ✅ Empty line handling
  - ✅ Error handling

### data_fetcher.py (26 tests)
- `TestStockData` (2 tests)
  - ✅ Initialization
  - ✅ Dictionary conversion

- `TestStockDataFetcher` (12 tests)
  - ✅ Symbol normalization
  - ✅ Price fetching
  - ✅ Price extraction from various fields
  - ✅ Error handling
  - ✅ Mock API responses

- `TestPriceHistory` (12 tests)
  - ✅ Initialization
  - ✅ Adding entries
  - ✅ History limits
  - ✅ Multiple stocks
  - ✅ Data retrieval
  - ✅ Sufficient data checks

### input_handler.py (18 tests)
- `TestInputAction` (1 test)
  - ✅ Action enumeration values

- `TestNavigationHandler` (10 tests)
  - ✅ Initialization
  - ✅ Navigation up/down
  - ✅ Wrap-around behavior
  - ✅ Selection tracking
  - ✅ Edge cases (empty list, single item)

- `TestTerminalInput` (7 tests)
  - ✅ Raw mode management
  - ✅ Terminal restoration
  - ✅ Key reading with timeout
  - ✅ Arrow key handling
  - ✅ Escape key handling

### ui_display.py (18 tests)
- `TestStockTableBuilder` (9 tests)
  - ✅ Table creation
  - ✅ Row addition (profit/loss)
  - ✅ Error row handling
  - ✅ Selection highlighting
  - ✅ StockData object support

- `TestUIDisplay` (5 tests)
  - ✅ Header display
  - ✅ Error messages
  - ✅ Loading information
  - ✅ Help messages
  - ✅ Cursor positioning

- `TestChartDisplay` (4 tests)
  - ✅ Chart drawing
  - ✅ Insufficient data handling
  - ✅ Custom chart sizing
  - ✅ Empty history handling

## Test Execution

### Run All Tests
```bash
python -m unittest discover tests/ -v
```

### Run with Coverage
```bash
coverage run -m unittest discover tests/
coverage report -m
coverage html
```

### Run Specific Module
```bash
python -m unittest tests.test_calculations -v
```

## CI/CD Integration

Tests are automatically run on:
- Every push to main/master/develop branches
- Every pull request
- Multiple Python versions (3.8, 3.9, 3.10, 3.11, 3.12)

See `.github/workflows/tests.yml` for configuration.

## Test Quality

### Mocking Strategy
- External API calls (yfinance) are mocked
- Terminal I/O operations are mocked
- File system operations use mocks or temporary files
- Console output is captured and verified

### Edge Cases Covered
- Empty inputs
- Invalid data formats
- Network errors
- File not found scenarios
- Boundary conditions
- Type conversions

### Best Practices
- Descriptive test names
- One assertion per logical concept
- Independent tests (no shared state)
- Setup/teardown where needed
- Mock external dependencies

## Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure all tests pass
3. Aim for >80% code coverage
4. Update this summary if adding new test files

## Notes

- Tests use Python's built-in `unittest` framework
- Compatible with pytest (with pytest-cov for coverage)
- No external test dependencies required (unittest is built-in)
- Development dependencies in `requirements-dev.txt`

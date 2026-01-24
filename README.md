# GPW Stock Price Monitor

![Tests](https://img.shields.io/badge/tests-95%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

A terminal application for monitoring stock prices from the Warsaw Stock Exchange (GPW - Giełda Papierów Wartościowych w Warszawie) with real-time updates, interactive navigation, and price history charts.

## Features

- 📈 Fetch current stock prices from GPW via Yahoo Finance
- 📊 Monitor multiple stocks simultaneously in a rich table display
- ⏱️ Automatic refresh every 30 seconds (configurable)
- 📉 Display price history charts in terminal (ASCII art)
- 💰 Calculate profit/loss relative to purchase price
- 🎨 Color-coded results (green = profit, red = loss)
- ⌨️ Interactive keyboard navigation (↑/↓ arrows, Enter for chart)
- 🔄 Live progress bar showing time to next refresh

## Project Structure

```
gpw/
├── run.py                  # Entry point - run from project root
├── akcje.txt               # Example stock list
├── requirements-dev.txt    # Development dependencies
├── setup.cfg               # Project configuration
├── src/                    # Main source code
│   ├── __init__.py
│   ├── gpw_kurs.py         # Main application logic
│   ├── config.py           # Configuration management
│   ├── config.ini          # Settings file
│   ├── data_fetcher.py     # Stock data fetching (yfinance)
│   ├── input_handler.py    # Keyboard input handling
│   ├── ui_display.py       # UI rendering (Rich library)
│   └── calculations.py     # Profit/loss calculations
└── tests/                  # Unit tests
    ├── test_calculations.py
    ├── test_config.py
    ├── test_data_fetcher.py
    ├── test_input_handler.py
    └── test_ui_display.py
```

## Requirements

- Python 3.8+
- yfinance
- rich

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd gpw

# Install dependencies
pip install yfinance rich

# Or install all dependencies including dev tools
pip install -r requirements-dev.txt
```

## Usage

```bash
# Run from project root
python run.py akcje.txt

# Or run the module directly
python -m src.gpw_kurs akcje.txt
```
# By docker 
docker compose build # will fetch fresh repo from GitHub, it will not compile local code
docker compose run --rm stock-monitor

### Keyboard Controls

| Key | Action |
|-----|--------|
| ↑ / ↓ | Navigate between stocks |
| Enter | Show price history chart for selected stock |
| ESC | Return from chart view / Exit application |
| Ctrl+C | Exit application |

## Stock File Format

The `akcje.txt` file should contain stock symbols with purchase prices (optional):

```
# Format: SYMBOL,PURCHASE_PRICE
PKO,88.08
CDR,274.00
PEO,206.30
KGHM,0.00
```

- Stock symbols are automatically appended with `.WA` suffix for Warsaw Stock Exchange
- If purchase price is `0.00`, profit/loss will not be displayed
- Lines starting with `#` are treated as comments

## Configuration

The `src/config.ini` file allows customization:

```ini
[Settings]
# Refresh interval in seconds
refresh_interval = 30

# Maximum number of historical measurements to store
max_history = 50

# Chart size (width, height)
plot_width = 100
plot_height = 20
```

## Example Output

```
╭──────────────────────────────────────────────────────────────────────────────╮
│                    📊 Stock Prices Update - 2026-01-19 14:30:00              │
├─────────────────┬────────────┬──────────┬────────────────────────┬───────────┤
│ Symbol          │      Price │ Currency │ Company Name           │      P/L  │
├─────────────────┼────────────┼──────────┼────────────────────────┼───────────┤
│ → PKO           │      89.50 │   PLN    │ PKO Bank Polski SA     │   +1.61%  │
│   CDR           │     280.00 │   PLN    │ CD Projekt SA          │   +2.19%  │
│   PEO          │     210.50 │   PLN    │ Bank Pekao SA          │   +2.04%  │
╰─────────────────┴────────────┴──────────┴────────────────────────┴───────────╯
[████████████░░░░░░░░] Next refresh in 18s

↑↓ Navigate | Enter: Chart | ESC: Exit
```

## Testing

The project includes comprehensive unit tests for all modules.

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
python run_tests.py

# Or use pytest directly
python -m pytest tests/

# Run with coverage report
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_calculations.py -v
```

### Test Coverage

The project includes 95 unit tests covering:
- **test_calculations.py** - 17 tests for profit/loss calculations
- **test_config.py** - 16 tests for configuration management
- **test_data_fetcher.py** - 26 tests for stock data fetching
- **test_input_handler.py** - 18 tests for keyboard input handling
- **test_ui_display.py** - 16 tests for UI display components

For more details, see [tests/README.md](tests/README.md).

## VS Code Integration

The project includes VS Code launch configuration. Press **F5** to start debugging.

## License

MIT License

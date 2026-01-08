# GPW Stock Price Monitor

A program for monitoring stock prices from the Warsaw Stock Exchange (GPW - Giełda Papierów Wartościowych w Warszawie).

## Features

- Fetch current stock prices from GPW
- Monitor multiple stocks simultaneously
- Automatic refresh every 30 seconds (configurable)
- Display price change charts in terminal
- Calculate profit/loss relative to purchase price
- Color-coded results (green = profit, red = loss)

## Requirements

- Python 3.6+
- yfinance
- plotext

## Installation

```bash
pip install yfinance plotext
```

## Usage

```bash
python gpw_kurs.py akcje.txt
```

## Stock File Format

The `akcje.txt` file should contain stock symbols with purchase prices (optional):

```
# Format: SYMBOL,PURCHASE_PRICE
PKO,45.50
PKNORLEN,55.20
KGHM,120.00
```

If you don't provide a purchase price (or set it to 0.00), the program won't display profit/loss.

## Configuration

The `config.ini` file allows customization:

- `refresh_interval` - refresh time in seconds (default 30)
- `max_history` - number of stored measurements (default 50)
- `plot_width` - chart width (default 100)
- `plot_height` - chart height (default 20)

## Example Output

```
================================================================================
Price Update: 2026-01-08 14:30:00
================================================================================
PKO.WA          |      45.80 PLN | PKO Bank Polski SA        | +0.66% (+0.30 PLN)
PKNORLEN.WA     |      54.50 PLN | Polski Koncern Naftowy    | -1.27% (-0.70 PLN)
KGHM.WA         |     125.30 PLN | KGHM Polska Miedź SA      | +4.42% (+5.30 PLN)
```

## Stopping the Program

Press `Ctrl+C` to stop monitoring.

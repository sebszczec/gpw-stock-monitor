# Testy jednostkowe - GPW Stock Monitor

## Struktura testów

```
tests/
├── __init__.py
├── test_calculations.py    # Testy dla modułu calculations
├── test_config.py          # Testy dla modułu config
├── test_data_fetcher.py    # Testy dla modułu data_fetcher
├── test_input_handler.py   # Testy dla modułu input_handler
└── test_ui_display.py      # Testy dla modułu ui_display
```

## Instalacja zależności testowych

```bash
pip install -r requirements-dev.txt
```

## Uruchamianie testów

### Wszystkie testy

```bash
# Sposób 1: Użyj skryptu run_tests.py
python run_tests.py

# Sposób 2: Bezpośrednio pytest
python -m pytest tests/

# Sposób 3: Tylko unittest
python -m unittest discover tests/
```

### Pojedynczy moduł

```bash
# Test konkretnego modułu
python -m pytest tests/test_calculations.py

# Lub z unittest
python -m unittest tests.test_calculations
```

### Konkretny test

```bash
# Test konkretnej klasy
python -m pytest tests/test_calculations.py::TestCalculateProfitLoss

# Test konkretnej funkcji
python -m pytest tests/test_calculations.py::TestCalculateProfitLoss::test_profit_scenario
```

## Opcje pytest

### Tryb verbose

```bash
python -m pytest tests/ -v
```

### Coverage (pokrycie kodu)

```bash
# Raport w terminalu
python -m pytest tests/ --cov=. --cov-report=term-missing

# Raport HTML
python -m pytest tests/ --cov=. --cov-report=html
# Otwórz: htmlcov/index.html

# Raport XML (dla CI/CD)
python -m pytest tests/ --cov=. --cov-report=xml
```

### Tylko określone testy

```bash
# Testy zawierające słowo "profit"
python -m pytest tests/ -k profit

# Testy z określonego pliku zawierające "loss"
python -m pytest tests/test_calculations.py -k loss
```

### Zatrzymanie po pierwszym błędzie

```bash
python -m pytest tests/ -x
```

### Pokazanie wszystkich print statements

```bash
python -m pytest tests/ -s
```

## Statystyki testów

### test_calculations.py
- Testy funkcji `calculate_profit_loss`
- Testy klasy `ProfitLossCalculator`
- Przypadki: zysk, strata, brak zmiany, zerowa cena zakupu
- **17 testów**

### test_config.py
- Testy klasy `Config`
- Testy funkcji `load_stocks_from_file`
- Przypadki: domyślne ustawienia, wczytywanie z pliku, różne formaty danych
- **16 testów**

### test_data_fetcher.py
- Testy klasy `StockData`
- Testy klasy `StockDataFetcher`
- Testy klasy `PriceHistory`
- Przypadki: normalizacja symboli, pobieranie cen, historia cen
- **26 testów**

### test_input_handler.py
- Testy klasy `InputAction`
- Testy klasy `NavigationHandler`
- Testy klasy `TerminalInput`
- Przypadki: nawigacja, obsługa klawiatury, strzałki
- **18 testów**

### test_ui_display.py
- Testy klasy `StockTableBuilder`
- Testy klasy `UIDisplay`
- Testy klasy `ChartDisplay`
- Przypadki: tworzenie tabel, wyświetlanie wykresów, formatowanie
- **16 testów**

**Łącznie: 93 testy**

## Continuous Integration

Przykładowa konfiguracja dla GitHub Actions (`.github/workflows/tests.yml`):

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
        pip install yfinance rich
    
    - name: Run tests
      run: python -m pytest tests/ --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Najlepsze praktyki

1. **Uruchamiaj testy przed commitem**
   ```bash
   python run_tests.py
   ```

2. **Sprawdzaj pokrycie kodu**
   - Cel: >80% pokrycia kodu
   - Generuj raport HTML do przeglądania

3. **Piszę testy dla nowych funkcji**
   - Każda nowa funkcja powinna mieć testy
   - Test-Driven Development (TDD) gdy możliwe

4. **Mockuj zewnętrzne zależności**
   - API (yfinance)
   - Wejście/wyjście terminala
   - System plików

5. **Nazywaj testy opisowo**
   - `test_calculate_profit_when_price_increased`
   - `test_load_stocks_from_file_with_invalid_format`

## Debugowanie testów

### Uruchom z debuggerem Python

```bash
python -m pdb -m pytest tests/test_calculations.py
```

### Pokaż lokalne zmienne przy błędzie

```bash
python -m pytest tests/ -l
```

### Szczegółowy traceback

```bash
python -m pytest tests/ --tb=long
```

## Problemy i rozwiązania

### ImportError: No module named 'pytest'

```bash
pip install pytest
```

### Testy nie znajdują modułów

Upewnij się, że uruchamiasz testy z głównego katalogu projektu:
```bash
cd /home/slaugh/source/gpw
python -m pytest tests/
```

### Mock nie działa

Sprawdź ścieżkę importu w `@patch`:
```python
# Jeśli w module używasz: from config import Config
# To mockuj: @patch('test_module.Config')
# Nie: @patch('config.Config')
```

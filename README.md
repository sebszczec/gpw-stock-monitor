# GPW Stock Price Monitor

Program do monitorowania kursów akcji z Giełdy Papierów Wartościowych w Warszawie (GPW).

## Funkcje

- Pobieranie aktualnych kursów akcji z GPW
- Monitorowanie wielu akcji jednocześnie
- Automatyczne odświeżanie co 30 sekund (konfigurowalny czas)
- Wyświetlanie wykresów zmian kursów w terminalu
- Obliczanie zysków/strat względem ceny zakupu
- Kolorowe wyświetlanie wyników (zielony = zysk, czerwony = strata)

## Wymagania

- Python 3.6+
- yfinance
- plotext

## Instalacja

```bash
pip install yfinance plotext
```

## Użycie

```bash
python gpw_kurs.py akcje.txt
```

## Format pliku z akcjami

Plik `akcje.txt` powinien zawierać symbole akcji wraz z ceną zakupu (opcjonalnie):

```
# Format: SYMBOL,CENA_ZAKUPU
PKO,45.50
PKNORLEN,55.20
KGHM,120.00
```

Jeśli nie podasz ceny zakupu (lub ustawisz 0.00), program nie będzie wyświetlać zysków/strat.

## Konfiguracja

Plik `config.ini` pozwala na dostosowanie:

- `refresh_interval` - czas odświeżania w sekundach (domyślnie 30)
- `max_history` - liczba przechowywanych pomiarów (domyślnie 50)
- `plot_width` - szerokość wykresów (domyślnie 100)
- `plot_height` - wysokość wykresów (domyślnie 20)

## Przykładowy wynik

```
================================================================================
Aktualizacja kursów: 2026-01-08 14:30:00
================================================================================
PKO.WA          |      45.80 PLN | PKO Bank Polski SA        | +0.66% (+0.30 PLN)
PKNORLEN.WA     |      54.50 PLN | Polski Koncern Naftowy    | -1.27% (-0.70 PLN)
KGHM.WA         |     125.30 PLN | KGHM Polska Miedź SA      | +4.42% (+5.30 PLN)
```

## Zakończenie programu

Naciśnij `Ctrl+C` aby zakończyć monitorowanie.

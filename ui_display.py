"""
UI Display module for GPW Stock Monitor.
Handles all UI rendering including tables and charts.
"""

try:
    import plotext as plt
except ImportError:
    print("Installing plotext library...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotext"])
    import plotext as plt

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich import box

console = Console()


class StockTableBuilder:
    """Builds Rich tables for displaying stock data."""
    
    @staticmethod
    def create_table(title):
        """
        Create a new stock price table.
        
        Args:
            title: Table title
        
        Returns:
            Rich Table object
        """
        table = Table(
            title=title,
            title_style="bold cyan",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
            expand=False
        )
        
        # Add columns
        table.add_column("Symbol", style="cyan", no_wrap=True, width=15)
        table.add_column("Price", justify="right", style="yellow", width=12)
        table.add_column("Currency", justify="center", style="dim", width=8)
        table.add_column("Company Name", style="white", width=30)
        table.add_column("P/L %", justify="right", width=10)
        table.add_column("P/L Amount", justify="right", width=15)
        
        return table
    
    @staticmethod
    def add_stock_row(table, stock_data, purchase_price, profit_loss, is_selected=False):
        """
        Add a stock row to the table.
        
        Args:
            table: Rich Table object
            stock_data: StockData object or dict
            purchase_price: Purchase price
            profit_loss: Tuple (percent, amount, is_profit) or (None, None, None)
            is_selected: Whether this row is selected
        """
        # Handle both StockData objects and dicts
        if hasattr(stock_data, 'to_dict'):
            data = stock_data.to_dict()
        else:
            data = stock_data
        
        symbol_display = data['symbol'].replace('.WA', '')
        if is_selected:
            symbol_display = f"→ {symbol_display}"
        
        # Format profit/loss
        percent, amount, is_profit = profit_loss
        if percent is not None:
            if is_profit:
                pl_percent = f"[green]+{percent:.2f}%[/green]"
                pl_amount = f"[green]+{amount:.2f} {data['currency']}[/green]"
            else:
                pl_percent = f"[red]{percent:.2f}%[/red]"
                pl_amount = f"[red]{amount:.2f} {data['currency']}[/red]"
        else:
            pl_percent = "[dim]-[/dim]"
            pl_amount = "[dim]-[/dim]"
        
        table.add_row(
            symbol_display,
            f"{data['price']:.2f}",
            data['currency'],
            data['name'][:30],
            pl_percent,
            pl_amount,
            style="bold" if is_selected else None
        )
    
    @staticmethod
    def add_error_row(table, stock_symbol, is_selected=False):
        """
        Add an error row to the table.
        
        Args:
            table: Rich Table object
            stock_symbol: Stock symbol
            is_selected: Whether this row is selected
        """
        symbol_display = stock_symbol
        if is_selected:
            symbol_display = f"→ {symbol_display}"
        
        table.add_row(
            symbol_display,
            "[red]ERROR[/red]",
            "-",
            "[red]Failed to fetch price[/red]",
            "[dim]-[/dim]",
            "[dim]-[/dim]",
            style="bold" if is_selected else None
        )


class ChartDisplay:
    """Displays stock price charts using plotext."""
    
    @staticmethod
    def draw_chart(price_history, stock_symbol, config, currency='PLN'):
        """
        Draws stock price chart in terminal.
        
        Args:
            price_history: List with data (time, price)
            stock_symbol: Stock symbol
            config: Config object or dictionary
            currency: Price currency
        """
        if len(price_history) < 2:
            console.print("[yellow]Not enough data to display chart.[/yellow]")
            return
        
        times = [h[0] for h in price_history]
        prices = [h[1] for h in price_history]
        
        # Use numeric indices instead of time strings
        indices = list(range(len(prices)))
        
        # Display chart title with Rich
        chart_title = f"📈 Price Chart: {stock_symbol.replace('.WA', '')} ({currency})"
        console.print(Panel(
            chart_title,
            style="bold cyan",
            border_style="cyan"
        ))
        
        # Create chart in terminal
        plt.clf()
        plt.plot(indices, prices, marker="braille")
        plt.title(f"Price Chart {stock_symbol.replace('.WA', '')}")
        plt.xlabel("Time")
        plt.ylabel(f"Price ({currency})")
        
        # Set X axis labels - show every few points for readability
        step = max(1, len(times) // 5)  # Show max 5-6 labels
        xticks_pos = [i for i in range(0, len(times), step)]
        xticks_labels = [times[i] for i in xticks_pos]
        plt.xticks(xticks_pos, xticks_labels)
        
        # Get plot size from config
        plot_width = config['plot_width'] if isinstance(config, dict) else config.get('plot_width')
        plot_height = config['plot_height'] if isinstance(config, dict) else config.get('plot_height')
        
        plt.plotsize(plot_width, plot_height)
        plt.show()


class UIDisplay:
    """Main UI display manager."""
    
    @staticmethod
    def show_header():
        """Display application header."""
        console.print("\n[bold cyan]═" * 50 + "[/bold cyan]")
        console.print(Align.center("[bold magenta]📈 GPW Stock Price Monitor 📈[/bold magenta]"))
        console.print("[bold cyan]═" * 50 + "[/bold cyan]\n")
    
    @staticmethod
    def show_help():
        """Display help message."""
        console.print(Panel.fit(
            "[bold cyan]GPW Stock Price Monitor[/bold cyan]\n\n"
            "[yellow]Usage:[/yellow] [bold]python gpw_kurs.py STOCKS_FILE[/bold]\n"
            "[yellow]Example:[/yellow] [bold]python gpw_kurs.py akcje.txt[/bold]\n\n"
            "[dim]File format: one stock symbol per line[/dim]\n"
            "[dim]Example file contents:[/dim]\n"
            "  [green]PKO[/green]\n"
            "  [green]PKNORLEN[/green]\n"
            "  [green]KGHM[/green]",
            border_style="blue",
            title="📊 Help"
        ))
    
    @staticmethod
    def show_loading_info(stocks_file, stocks, refresh_interval):
        """
        Display loading and configuration information.
        
        Args:
            stocks_file: Path to stocks file
            stocks: Dictionary of stocks
            refresh_interval: Refresh interval in seconds
        """
        console.print(f"[cyan]📂 Loading stock list from file:[/cyan] [bold]{stocks_file}[/bold]")
        console.print(f"[green]✅ Found {len(stocks)} stocks:[/green] [bold]{', '.join(stocks.keys())}[/bold]")
        console.print(f"\n[cyan]⏱️  Refresh interval:[/cyan] [bold yellow]{refresh_interval} seconds[/bold yellow]")
        console.print("[dim]Press Ctrl+C to stop.[/dim]\n")
    
    @staticmethod
    def show_error(message):
        """Display error message."""
        console.print(f"[red]❌ {message}[/red]")
    
    @staticmethod
    def show_warning(message):
        """Display warning message."""
        console.print(f"[yellow]⚠️  {message}[/yellow]")
    
    @staticmethod
    def show_goodbye():
        """Display goodbye message."""
        console.print("\n\n[yellow]👋 Stopped monitoring prices.[/yellow]\n")
    
    @staticmethod
    def clear():
        """Clear the console."""
        console.clear()
    
    @staticmethod
    def clear_and_home():
        """Clear screen and move cursor to home position without scrolling."""
        # ANSI escape sequences:
        # \033[2J - clear entire screen
        # \033[H - move cursor to home position (1,1)
        import sys
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.flush()

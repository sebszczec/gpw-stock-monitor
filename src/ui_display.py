"""
UI Display module for GPW Stock Monitor.
Handles all UI rendering including tables and charts.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
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
    """Displays stock price charts using Rich Unicode blocks."""
    
    @staticmethod
    def draw_chart(price_history, stock_symbol, config, currency='PLN'):
        """
        Draws stock price chart in terminal using Rich.
        
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
        
        # Get chart dimensions from config
        plot_width = config['plot_width'] if isinstance(config, dict) else config.get('plot_width')
        plot_height = config['plot_height'] if isinstance(config, dict) else config.get('plot_height')
        
        # Adjust dimensions
        chart_width = min(plot_width, 80)
        chart_height = min(plot_height, 20)
        
        # Calculate min/max for scaling
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price if max_price != min_price else 1
        
        # Build the chart using Unicode blocks
        chart_lines = []
        
        # Characters for drawing (from bottom to top: empty, quarter, half, three-quarter, full)
        blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        
        # Scale prices to fit height
        scaled = []
        for price in prices:
            if price_range > 0:
                normalized = (price - min_price) / price_range
            else:
                normalized = 0.5
            scaled.append(normalized * (chart_height - 1))
        
        # Resample if needed to fit width
        if len(scaled) > chart_width:
            step = len(scaled) / chart_width
            resampled = []
            resampled_times = []
            for i in range(chart_width):
                idx = int(i * step)
                resampled.append(scaled[idx])
                resampled_times.append(times[idx])
            scaled = resampled
            times = resampled_times
        
        # Build chart from top to bottom
        for row in range(chart_height - 1, -1, -1):
            line = Text()
            for col, val in enumerate(scaled):
                if val >= row + 1:
                    # Full block
                    line.append("█", style="cyan")
                elif val > row:
                    # Partial block
                    frac = val - row
                    block_idx = int(frac * 8)
                    block_idx = max(1, min(8, block_idx))
                    line.append(blocks[block_idx], style="cyan")
                else:
                    line.append(" ")
            chart_lines.append(line)
        
        # Create price labels
        price_labels = Text()
        price_labels.append(f"{max_price:.2f} {currency}\n", style="yellow")
        for _ in range(chart_height - 2):
            price_labels.append("\n")
        price_labels.append(f"{min_price:.2f} {currency}", style="yellow")
        
        # Print chart header
        symbol_clean = stock_symbol.replace('.WA', '')
        console.print()
        console.print(Panel(
            f"📈 [bold cyan]Price Chart: {symbol_clean}[/bold cyan] ({currency})",
            border_style="cyan",
            padding=(0, 2)
        ))
        console.print()
        
        # Print the chart with border
        console.print(f"  [dim]┌{'─' * len(scaled)}┐[/dim]")
        for i, line in enumerate(chart_lines):
            # Add price label on the right side
            if i == 0:
                price_label = f" {max_price:.2f}"
            elif i == len(chart_lines) - 1:
                price_label = f" {min_price:.2f}"
            elif i == len(chart_lines) // 2:
                mid_price = (max_price + min_price) / 2
                price_label = f" {mid_price:.2f}"
            else:
                price_label = ""
            
            console.print(Text("  [dim]│[/dim]") + line + Text(f"[dim]│[/dim][yellow]{price_label}[/yellow]"))
        console.print(f"  [dim]└{'─' * len(scaled)}┘[/dim]")
        
        # Print time labels
        if len(times) > 0:
            time_line = "   "
            # Show first, middle and last time
            first_time = times[0]
            last_time = times[-1]
            mid_idx = len(times) // 2
            mid_time = times[mid_idx] if mid_idx < len(times) else ""
            
            # Calculate spacing
            spacing = len(scaled) // 2 - len(first_time)
            time_line = f"   [dim]{first_time}[/dim]"
            time_line += " " * max(0, spacing - len(mid_time) // 2)
            time_line += f"[dim]{mid_time}[/dim]"
            time_line += " " * max(0, spacing - len(mid_time) // 2)
            time_line += f"[dim]{last_time}[/dim]"
            console.print(time_line)
        
        console.print()
        
        # Show statistics
        current_price = prices[-1]
        first_price = prices[0]
        change = current_price - first_price
        change_pct = (change / first_price * 100) if first_price != 0 else 0
        
        if change >= 0:
            change_style = "green"
            change_symbol = "▲"
        else:
            change_style = "red"
            change_symbol = "▼"
        
        stats = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        stats.add_column("Label", style="dim")
        stats.add_column("Value", style="bold")
        
        stats.add_row("Current:", f"[yellow]{current_price:.2f} {currency}[/yellow]")
        stats.add_row("High:", f"[green]{max_price:.2f} {currency}[/green]")
        stats.add_row("Low:", f"[red]{min_price:.2f} {currency}[/red]")
        stats.add_row("Change:", f"[{change_style}]{change_symbol} {change:+.2f} ({change_pct:+.2f}%)[/{change_style}]")
        stats.add_row("Data points:", f"{len(prices)}")
        
        console.print(Panel(stats, title="[bold]Statistics[/bold]", border_style="blue"))


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
    
    @staticmethod
    def create_refresh_progress_bar(remaining_seconds, total_seconds):
        """
        Create a progress bar showing time until next refresh.
        
        Args:
            remaining_seconds: Seconds remaining until refresh
            total_seconds: Total seconds between refreshes
        
        Returns:
            Rich renderable progress bar
        """
        # Calculate percentage
        percent = (remaining_seconds / total_seconds) * 100 if total_seconds > 0 else 0
        
        # Create progress bar (50 characters wide)
        bar_width = 50
        filled = int((percent / 100) * bar_width)
        empty = bar_width - filled
        
        # Build progress bar string
        bar_text = Text()
        bar_text.append("█" * filled, style="cyan")
        bar_text.append("░" * empty, style="dim")
        bar_text.append(f"  {int(remaining_seconds)}s ", style="yellow")
        
        return bar_text
    
    @staticmethod
    def create_keyboard_help():
        """
        Create keyboard help text.
        
        Returns:
            Rich Text with keyboard shortcuts
        """
        help_text = Text()
        help_text.append("  ↑/w", style="bold cyan")
        help_text.append(" - up  ", style="dim")
        help_text.append("↓/s", style="bold cyan")
        help_text.append(" - down  ", style="dim")
        help_text.append("Enter", style="bold cyan")
        help_text.append(" - chart  ", style="dim")
        help_text.append("Ctrl+C", style="bold cyan")
        help_text.append(" - exit", style="dim")
        
        return help_text

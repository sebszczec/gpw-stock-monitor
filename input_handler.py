"""
Input handling module for GPW Stock Monitor.
Handles keyboard input and terminal control.
"""

import sys
import select
import tty
import termios
import time
from rich.console import Console
from rich.text import Text

console = Console()


class InputAction:
    """Enumeration of possible input actions."""
    NAVIGATE_UP = 'navigate_up'
    NAVIGATE_DOWN = 'navigate_down'
    SHOW_CHART = 'show_chart'
    TIMEOUT = 'timeout'
    ESCAPE = 'escape'


class TerminalInput:
    """Handles terminal input in raw mode."""
    
    @staticmethod
    def _set_raw_mode():
        """Set terminal to raw mode and return old settings."""
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        return old_settings
    
    @staticmethod
    def _restore_terminal(old_settings):
        """Restore terminal to previous settings."""
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    @staticmethod
    def read_key_with_timeout(timeout_seconds):
        """
        Read a single key with timeout.
        
        Args:
            timeout_seconds: Timeout in seconds
        
        Returns:
            Key character or None if timeout
        """
        if select.select([sys.stdin], [], [], timeout_seconds)[0]:
            key = sys.stdin.read(1)
            
            # Handle escape sequences (arrow keys)
            if key == '\x1b':
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    next_char = sys.stdin.read(1)
                    if next_char == '[':
                        if select.select([sys.stdin], [], [], 0.1)[0]:
                            arrow = sys.stdin.read(1)
                            if arrow == 'A':  # Up arrow
                                return 'w'
                            elif arrow == 'B':  # Down arrow
                                return 's'
                return '\x1b'  # Just ESC
            return key
        return None


class NavigationHandler:
    """Handles navigation through stock list."""
    
    def __init__(self, stocks_list):
        """
        Initialize navigation handler.
        
        Args:
            stocks_list: List of stock symbols
        """
        self.stocks_list = stocks_list
        self.selected_index = 0
    
    def move_up(self):
        """Move selection up (wraps around)."""
        self.selected_index = (self.selected_index - 1) % len(self.stocks_list)
    
    def move_down(self):
        """Move selection down (wraps around)."""
        self.selected_index = (self.selected_index + 1) % len(self.stocks_list)
    
    def get_selected_stock(self):
        """Get currently selected stock symbol."""
        return self.stocks_list[self.selected_index]
    
    def get_selected_index(self):
        """Get currently selected index."""
        return self.selected_index


class CountdownTimer:
    """Displays countdown timer with navigation hints."""
    
    @staticmethod
    def display(remaining_seconds):
        """
        Display countdown with hints.
        
        Args:
            remaining_seconds: Seconds remaining
        """
        countdown_text = Text()
        countdown_text.append("⏱️  Next update in ", style="bold cyan")
        countdown_text.append(f"{int(remaining_seconds)}", style="bold yellow")
        countdown_text.append(" seconds... ", style="bold cyan")
        countdown_text.append("(w/s: navigate, Enter: show chart)", style="italic bright_black")
        console.print(countdown_text, end='\r')


def wait_for_key_or_timeout(timeout, navigation_handler):
    """
    Waits for key press or timeout. Supports navigation and selection.
    
    Args:
        timeout: Time to wait in seconds
        navigation_handler: NavigationHandler instance
    
    Returns:
        InputAction constant
    """
    start_time = time.time()
    remaining = timeout
    
    old_settings = TerminalInput._set_raw_mode()
    
    try:
        while remaining > 0:
            CountdownTimer.display(remaining)
            
            key = TerminalInput.read_key_with_timeout(1)
            
            if key:
                if key.lower() == 'w':  # Move up
                    navigation_handler.move_up()
                    console.print()
                    return InputAction.NAVIGATE_UP
                elif key.lower() == 's':  # Move down
                    navigation_handler.move_down()
                    console.print()
                    return InputAction.NAVIGATE_DOWN
                elif key == '\r' or key == '\n':  # Enter
                    console.print()
                    return InputAction.SHOW_CHART
            
            elapsed = time.time() - start_time
            remaining = timeout - elapsed
        
        console.print()
        return InputAction.TIMEOUT
    finally:
        TerminalInput._restore_terminal(old_settings)


def wait_for_escape():
    """
    Waits for ESC key press to return to table view.
    
    Returns:
        True when ESC is pressed
    """
    old_settings = TerminalInput._set_raw_mode()
    
    try:
        console.print("[dim]Press ESC to return to table view...[/dim]")
        
        while True:
            key = TerminalInput.read_key_with_timeout(0.5)
            if key == '\x1b':  # ESC
                return True
    finally:
        TerminalInput._restore_terminal(old_settings)

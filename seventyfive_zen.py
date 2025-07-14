#!/usr/bin/env python3
"""
75 Zen - Minimalist CLI tracker for daily discipline and personal growth
Refactored version with improved architecture and interactive mode
"""

import os
import sys
import json
import argparse
import termios
import tty
from datetime import datetime, date, timedelta
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum


# ======================== Configuration ========================

APP_NAME = "75zen"
HOME_DIR = Path.home() / f".{APP_NAME}"
STREAK_FILE = HOME_DIR / "streak.json"

# Daily checklist items
CHECKLIST_ITEMS = [
    ("⏳", "Time for self"),
    ("🏃", "Exercise 45+ min"),
    ("👨‍👩‍👧", "Quality family time"),
    ("📚", "Study (60+ min)"),
    ("💼", "Focused work (90+ min)"),
    ("🚫", "No alcohol"),
    ("🍽️", "Followed diet")
]


# ======================== ANSI Colors ========================

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    CLEAR = '\033[2J\033[H'

    @classmethod
    def green(cls, text: str) -> str:
        return f"{cls.GREEN}{text}{cls.ENDC}"

    @classmethod
    def red(cls, text: str) -> str:
        return f"{cls.RED}{text}{cls.ENDC}"

    @classmethod
    def yellow(cls, text: str) -> str:
        return f"{cls.YELLOW}{text}{cls.ENDC}"

    @classmethod
    def blue(cls, text: str) -> str:
        return f"{cls.BLUE}{text}{cls.ENDC}"

    @classmethod
    def bold(cls, text: str) -> str:
        return f"{cls.BOLD}{text}{cls.ENDC}"


# ======================== Data Models ========================

@dataclass
class StreakData:
    """Represents streak tracking data"""
    current: int = 0
    best: int = 0
    last_date: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "current": self.current,
            "best": self.best,
            "last_date": self.last_date
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'StreakData':
        return cls(
            current=data.get("current", 0),
            best=data.get("best", 0),
            last_date=data.get("last_date")
        )


class ChecklistItem:
    """Represents a single checklist item"""
    def __init__(self, index: int, emoji: str, task: str, checked: bool = False):
        self.index = index
        self.emoji = emoji
        self.task = task
        self.checked = checked

    def toggle(self):
        """Toggle the checked state"""
        self.checked = not self.checked

    def __str__(self) -> str:
        checkbox = "✅" if self.checked else "⬜"
        color = Colors.green if self.checked else Colors.yellow
        return f"{self.index}. {checkbox} {color(f'{self.emoji} {self.task}')}"


# ======================== File Operations ========================

class FileManager:
    """Handles all file operations for the app"""

    @staticmethod
    def ensure_directory():
        """Create the app directory if it doesn't exist"""
        HOME_DIR.mkdir(exist_ok=True)

    @staticmethod
    def get_today_file() -> Path:
        """Get the path for today's checklist file"""
        today = date.today().strftime("%Y-%m-%d")
        return HOME_DIR / f"{today}.md"

    @classmethod
    def create_daily_file(cls) -> Path:
        """Create a new daily checklist file"""
        today_file = cls.get_today_file()
        if not today_file.exists():
            content = f"# 75 Zen - {date.today().strftime('%A, %B %d, %Y')}\n\n"
            for i, (emoji, task) in enumerate(CHECKLIST_ITEMS, 1):
                content += f"{i}. [ ] {emoji} {task}\n"
            today_file.write_text(content)
        return today_file

    @classmethod
    def read_checklist(cls) -> List[ChecklistItem]:
        """Read the current day's checklist"""
        today_file = cls.get_today_file()
        if not today_file.exists():
            cls.create_daily_file()

        with open(today_file, 'r') as f:
            lines = f.readlines()

        checklist = []
        item_index = 0
        for line in lines:
            if line.strip() and line[0].isdigit():
                is_checked = "[x]" in line or "[X]" in line
                emoji, task = CHECKLIST_ITEMS[item_index]
                checklist.append(ChecklistItem(
                    index=item_index + 1,
                    emoji=emoji,
                    task=task,
                    checked=is_checked
                ))
                item_index += 1

        return checklist

    @classmethod
    def write_checklist(cls, checklist: List[ChecklistItem]):
        """Write the updated checklist back to file"""
        today_file = cls.get_today_file()

        with open(today_file, 'r') as f:
            lines = f.readlines()

        # Update the checklist items
        checklist_index = 0
        for i, line in enumerate(lines):
            if line.strip() and line[0].isdigit() and checklist_index < len(checklist):
                item = checklist[checklist_index]
                if item.checked:
                    lines[i] = line.replace("[ ]", "[x]")
                else:
                    lines[i] = line.replace("[x]", "[ ]").replace("[X]", "[ ]")
                checklist_index += 1

        with open(today_file, 'w') as f:
            f.writelines(lines)

    @staticmethod
    def load_streak() -> StreakData:
        """Load streak data from JSON file"""
        if STREAK_FILE.exists():
            with open(STREAK_FILE, 'r') as f:
                data = json.load(f)
                return StreakData.from_dict(data)
        return StreakData()

    @staticmethod
    def save_streak(streak_data: StreakData):
        """Save streak data to JSON file"""
        with open(STREAK_FILE, 'w') as f:
            json.dump(streak_data.to_dict(), f, indent=2)

    @classmethod
    def reset_day(cls):
        """Reset today's checklist"""
        today_file = cls.get_today_file()
        if today_file.exists():
            today_file.unlink()
        cls.create_daily_file()


# ======================== Streak Management ========================

class StreakManager:
    """Manages streak calculation and updates"""

    @staticmethod
    def update_streak(checklist: List[ChecklistItem]) -> StreakData:
        """Update streak based on checklist completion"""
        streak_data = FileManager.load_streak()
        today = date.today().strftime("%Y-%m-%d")

        # Check if all items are completed
        all_completed = all(item.checked for item in checklist)

        # If it's a new day
        if streak_data.last_date != today:
            yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

            # Check if we're continuing from yesterday
            if streak_data.last_date == yesterday and all_completed:
                streak_data.current += 1
            elif all_completed:
                streak_data.current = 1
            elif not all_completed:
                streak_data.current = 0

            streak_data.last_date = today

            # Update best streak
            if streak_data.current > streak_data.best:
                streak_data.best = streak_data.current

            FileManager.save_streak(streak_data)

        return streak_data

    @staticmethod
    def reset_streak():
        """Force reset the streak counter"""
        streak_data = StreakData(
            current=0,
            best=FileManager.load_streak().best,
            last_date=date.today().strftime("%Y-%m-%d")
        )
        FileManager.save_streak(streak_data)


# ======================== UI Components ========================

class UI:
    """User Interface components"""

    @staticmethod
    def clear_screen():
        """Clear the terminal screen"""
        print(Colors.CLEAR, end='')

    @staticmethod
    def print_header():
        """Print the app header"""
        print(Colors.bold("🧘 75 Zen - Daily Discipline Tracker"))
        print("=" * 50)

    @staticmethod
    def print_checklist(checklist: List[ChecklistItem]):
        """Print the checklist items"""
        for item in checklist:
            print(item)

    @staticmethod
    def print_progress_bar(checklist: List[ChecklistItem]):
        """Print a progress bar based on completion"""
        completed_count = sum(1 for item in checklist if item.checked)
        total = len(checklist)
        progress = completed_count / total if total > 0 else 0

        print("\n" + "─" * 50)

        bar_length = 40
        filled = int(bar_length * progress)
        bar = "█" * filled + "░" * (bar_length - filled)
        percentage = int(progress * 100)

        print(f"Progress: [{bar}] {completed_count}/{total} ({percentage}%)")

        return completed_count, total

    @staticmethod
    def print_streak_info(streak_data: StreakData):
        """Print streak information"""
        print("─" * 50)

        streak_color = Colors.green if streak_data.current > 0 else Colors.red
        print(f"🔥 Current Streak: {streak_color(f'{streak_data.current} days')}")
        print(f"🏆 Best Streak: {Colors.blue(f'{streak_data.best} days')}")

    @staticmethod
    def print_motivational_message(completed_count: int, total: int):
        """Print a motivational message based on progress"""
        if completed_count == total:
            print(f"\n{Colors.green('✨ Perfect day! Keep going! ✨')}")
        elif completed_count > 0:
            remaining = total - completed_count
            print(f"\n{Colors.yellow(f'💪 {remaining} more to go! You got this!')}")
        else:
            print(f"\n{Colors.red('🚀 Time to start! One task at a time.')}")

    @staticmethod
    def print_interactive_controls():
        """Print control instructions for interactive mode"""
        print(f"\n{Colors.bold('Controls:')}")
        print("Press [1-7] to toggle items | [r] reset day | [q] quit")
        print(f"{Colors.yellow('>')} ", end='', flush=True)


# ======================== Input Handling ========================

class InputHandler:
    """Handles keyboard input for interactive mode"""

    @staticmethod
    def getch() -> str:
        """Get a single character from stdin"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


# ======================== Application Logic ========================

class ZenApp:
    """Main application class"""

    def __init__(self):
        FileManager.ensure_directory()

    def toggle_item(self, item_number: int, silent: bool = False) -> bool:
        """Toggle a checklist item"""
        checklist = FileManager.read_checklist()

        if 1 <= item_number <= len(checklist):
            checklist[item_number - 1].toggle()
            FileManager.write_checklist(checklist)

            if not silent:
                item = checklist[item_number - 1]
                status = "✅ Completed" if item.checked else "⬜ Unchecked"
                print(f"{Colors.green(status)}: {item.emoji} {item.task}")

            return True
        else:
            if not silent:
                print(Colors.red(f"Invalid item number. Use 1-{len(checklist)}"))
            return False

    def display_status(self):
        """Display current checklist and streak status (non-interactive)"""
        checklist = FileManager.read_checklist()
        streak_data = StreakManager.update_streak(checklist)

        UI.print_header()
        UI.print_checklist(checklist)
        completed, total = UI.print_progress_bar(checklist)
        UI.print_streak_info(streak_data)
        UI.print_motivational_message(completed, total)
        print()

    def interactive_mode(self):
        """Run the interactive mode"""
        try:
            while True:
                UI.clear_screen()

                checklist = FileManager.read_checklist()
                streak_data = StreakManager.update_streak(checklist)

                UI.print_header()
                UI.print_checklist(checklist)
                completed, total = UI.print_progress_bar(checklist)
                UI.print_streak_info(streak_data)
                UI.print_motivational_message(completed, total)
                UI.print_interactive_controls()

                # Get user input
                key = InputHandler.getch()

                if key == 'q' or key == 'Q':
                    print("\n👋 Keep crushing it!")
                    break
                elif key == 'r' or key == 'R':
                    FileManager.reset_day()
                elif key in '1234567':
                    self.toggle_item(int(key), silent=True)
                elif key == '\x03':  # Ctrl+C
                    print("\n👋 Keep crushing it!")
                    break

        except KeyboardInterrupt:
            print("\n👋 Keep crushing it!")
        except Exception as e:
            print(f"\n{Colors.red(f'Error in interactive mode: {e}')}")
            print("Falling back to status display...")
            self.display_status()

    def reset_day(self):
        """Reset today's checklist"""
        FileManager.reset_day()
        print(Colors.yellow("📝 Today's checklist has been reset."))

    def force_reset_streak(self):
        """Force reset the streak counter"""
        response = input(Colors.yellow("Are you sure you want to reset your streak? (y/N): "))
        if response.lower() == 'y':
            StreakManager.reset_streak()
            print(Colors.red("🔄 Streak has been reset to 0."))
        else:
            print("Streak reset cancelled.")


# ======================== Main Entry Point ========================

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(
        description="75 Zen - Minimalist CLI tracker for daily discipline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  75z                 # Interactive mode (just press numbers!)
  75z check 4         # Mark item 4 as completed
  75z status          # Show current status (non-interactive)
  75z reset_day       # Clear and recreate today
  75z force_reset     # Manual streak reset

Interactive Mode Controls:
  Press 1-7 to toggle items
  Press 'r' to reset day
  Press 'q' to quit
        """
    )

    parser.add_argument('command', nargs='?', default='interactive',
                      choices=['check', 'status', 'reset_day', 'force_reset', 'interactive'],
                      help='Command to execute (default: interactive)')
    parser.add_argument('item', nargs='?', type=int,
                      help='Item number for check command (1-7)')

    args = parser.parse_args()

    # Initialize the app
    app = ZenApp()

    # Execute command
    if args.command == 'check':
        if args.item:
            app.toggle_item(args.item)
        else:
            print(Colors.red("Please specify an item number (1-7)"))
    elif args.command == 'status':
        app.display_status()
    elif args.command == 'reset_day':
        app.reset_day()
    elif args.command == 'force_reset':
        app.force_reset_streak()
    else:  # interactive mode (default)
        app.interactive_mode()


if __name__ == "__main__":
    main()

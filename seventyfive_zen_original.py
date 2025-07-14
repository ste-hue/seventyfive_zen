#!/usr/bin/env python3
"""
75 Zen - Minimalist CLI tracker for daily discipline and personal growth
"""

import os
import json
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path

# Configuration
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

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def ensure_directory():
    """Create the app directory if it doesn't exist"""
    HOME_DIR.mkdir(exist_ok=True)

def get_today_file():
    """Get the path for today's checklist file"""
    today = date.today().strftime("%Y-%m-%d")
    return HOME_DIR / f"{today}.md"

def create_daily_file():
    """Create a new daily checklist file"""
    today_file = get_today_file()
    if not today_file.exists():
        content = f"# 75 Zen - {date.today().strftime('%A, %B %d, %Y')}\n\n"
        for i, (emoji, task) in enumerate(CHECKLIST_ITEMS, 1):
            content += f"{i}. [ ] {emoji} {task}\n"

        today_file.write_text(content)
    return today_file

def read_checklist():
    """Read the current day's checklist"""
    today_file = get_today_file()
    if not today_file.exists():
        create_daily_file()

    with open(today_file, 'r') as f:
        lines = f.readlines()

    checklist = []
    for line in lines:
        if line.strip() and line[0].isdigit():
            is_checked = "[x]" in line or "[X]" in line
            checklist.append(is_checked)

    return checklist

def write_checklist(checklist):
    """Write the updated checklist back to file"""
    today_file = get_today_file()

    with open(today_file, 'r') as f:
        lines = f.readlines()

    # Update the checklist items
    checklist_index = 0
    for i, line in enumerate(lines):
        if line.strip() and line[0].isdigit() and checklist_index < len(checklist):
            if checklist[checklist_index]:
                lines[i] = line.replace("[ ]", "[x]")
            else:
                lines[i] = line.replace("[x]", "[ ]").replace("[X]", "[ ]")
            checklist_index += 1

    with open(today_file, 'w') as f:
        f.writelines(lines)

def toggle_item(item_number):
    """Toggle a checklist item between checked and unchecked"""
    checklist = read_checklist()

    if 1 <= item_number <= len(checklist):
        checklist[item_number - 1] = not checklist[item_number - 1]
        write_checklist(checklist)

        status = "✅ Completed" if checklist[item_number - 1] else "⬜ Unchecked"
        emoji, task = CHECKLIST_ITEMS[item_number - 1]
        print(f"{Colors.GREEN}{status}{Colors.ENDC}: {emoji} {task}")
    else:
        print(f"{Colors.RED}Invalid item number. Use 1-{len(checklist)}{Colors.ENDC}")

def load_streak():
    """Load streak data from JSON file"""
    if STREAK_FILE.exists():
        with open(STREAK_FILE, 'r') as f:
            return json.load(f)
    return {
        "current": 0,
        "best": 0,
        "last_date": None
    }

def save_streak(streak_data):
    """Save streak data to JSON file"""
    with open(STREAK_FILE, 'w') as f:
        json.dump(streak_data, f, indent=2)

def update_streak():
    """Update streak based on today's checklist"""
    checklist = read_checklist()
    streak_data = load_streak()
    today = date.today().strftime("%Y-%m-%d")

    # Check if all items are completed
    all_completed = all(checklist)

    # If it's a new day
    if streak_data["last_date"] != today:
        yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        # Check if we're continuing from yesterday
        if streak_data["last_date"] == yesterday and all_completed:
            streak_data["current"] += 1
        elif all_completed:
            streak_data["current"] = 1
        elif not all_completed:
            streak_data["current"] = 0

        streak_data["last_date"] = today

        # Update best streak
        if streak_data["current"] > streak_data["best"]:
            streak_data["best"] = streak_data["current"]

        save_streak(streak_data)

    return streak_data

def display_status():
    """Display current checklist and streak status"""
    checklist = read_checklist()
    streak_data = update_streak()

    # Header
    print(f"\n{Colors.BOLD}🧘 75 Zen - Daily Discipline Tracker{Colors.ENDC}")
    print("=" * 40)

    # Checklist
    completed_count = 0
    for i, (is_checked, (emoji, task)) in enumerate(zip(checklist, CHECKLIST_ITEMS), 1):
        checkbox = "✅" if is_checked else "⬜"
        color = Colors.GREEN if is_checked else Colors.YELLOW
        print(f"{i}. {checkbox} {color}{emoji} {task}{Colors.ENDC}")
        if is_checked:
            completed_count += 1

    # Progress bar
    print("\n" + "─" * 40)
    progress = completed_count / len(checklist)
    bar_length = 30
    filled = int(bar_length * progress)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"Progress: [{bar}] {completed_count}/{len(checklist)}")

    # Streak info
    print("─" * 40)
    streak_color = Colors.GREEN if streak_data["current"] > 0 else Colors.RED
    print(f"🔥 Current Streak: {streak_color}{streak_data['current']} days{Colors.ENDC}")
    print(f"🏆 Best Streak: {Colors.BLUE}{streak_data['best']} days{Colors.ENDC}")

    # Motivational message
    if completed_count == len(checklist):
        print(f"\n{Colors.GREEN}✨ Perfect day! Keep going! ✨{Colors.ENDC}")
    elif completed_count > 0:
        remaining = len(checklist) - completed_count
        print(f"\n{Colors.YELLOW}💪 {remaining} more to go! You got this!{Colors.ENDC}")
    else:
        print(f"\n{Colors.RED}🚀 Time to start! One task at a time.{Colors.ENDC}")
    print()

def reset_day():
    """Reset today's checklist"""
    today_file = get_today_file()
    if today_file.exists():
        today_file.unlink()
    create_daily_file()
    print(f"{Colors.YELLOW}📝 Today's checklist has been reset.{Colors.ENDC}")

def force_reset_streak():
    """Force reset the streak counter"""
    streak_data = load_streak()
    streak_data["current"] = 0
    streak_data["last_date"] = date.today().strftime("%Y-%m-%d")
    save_streak(streak_data)
    print(f"{Colors.RED}🔄 Streak has been reset to 0.{Colors.ENDC}")

def main():
    parser = argparse.ArgumentParser(
        description="75 Zen - Minimalist CLI tracker for daily discipline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  75z                 # Show checklist and streak
  75z check 4         # Mark item 4 as completed
  75z status          # Show current status + streak
  75z reset_day       # Clear and recreate today
  75z force_reset     # Manual streak reset
        """
    )

    parser.add_argument('command', nargs='?', default='status',
                      choices=['check', 'status', 'reset_day', 'force_reset'],
                      help='Command to execute')
    parser.add_argument('item', nargs='?', type=int,
                      help='Item number for check command (1-7)')

    args = parser.parse_args()

    # Ensure app directory exists
    ensure_directory()

    # Execute command
    if args.command == 'check':
        if args.item:
            toggle_item(args.item)
        else:
            print(f"{Colors.RED}Please specify an item number (1-7){Colors.ENDC}")
    elif args.command == 'reset_day':
        reset_day()
    elif args.command == 'force_reset':
        response = input(f"{Colors.YELLOW}Are you sure you want to reset your streak? (y/N): {Colors.ENDC}")
        if response.lower() == 'y':
            force_reset_streak()
        else:
            print("Streak reset cancelled.")
    else:  # status or default
        display_status()

if __name__ == "__main__":
    main()

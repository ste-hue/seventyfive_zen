#!/usr/bin/env python3
"""
75z Knowledge Engine - Interactive Naval-style iteration loop
Do → See → Understand → Change → Repeat
"""
import json
import sys
import os
import termios
import tty
import time
from pathlib import Path
from datetime import date, timedelta, datetime
from typing import Optional, Dict, Any
import argparse


# ---------- CONFIG ----------

DEFAULT_LOG_DIR = Path.home() / "75z_logs"
LOOPS = ["BUILD", "BODY", "SYSTEM", "INSIGHT"]

LOOP_INFO = {
    "BUILD": {
        "time": "60-90m",
        "description": "Deep work on your main project (CM3070/HotelOPS)",
        "prompts": [
            "What are you building?",
            "What's the hardest part?",
            "What will you ship today?"
        ],
        "questions": {
            "surprise": "What was unexpected in the code/design?",
            "understanding": "What pattern or concept clicked?"
        }
    },
    "BODY": {
        "time": "20-30m",
        "description": "Physical training - push/dips/KB/walk",
        "prompts": [
            "What exercise?",
            "How many reps/duration?",
            "How do you feel?"
        ],
        "questions": {
            "surprise": "What felt different in your body today?",
            "understanding": "What did you notice about form/breathing/energy?"
        }
    },
    "SYSTEM": {
        "time": "10-15m",
        "description": "Simplify one thing - file/config/process",
        "prompts": [
            "What needs simplifying?",
            "What can you delete?",
            "How to make it cleaner?"
        ],
        "questions": {
            "surprise": "What complexity was hiding in plain sight?",
            "understanding": "What principle of simplicity applied here?"
        }
    },
    "INSIGHT": {
        "time": "5-10m",
        "description": "Extract today's learning",
        "prompts": [
            "What did you learn?",
            "What tiny change for tomorrow?",
            "What belief updated?"
        ]
    }
}

# ANSI Colors
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'
    CLEAR = '\033[2J\033[H'


# ---------- DATA MODEL ----------

def load_day_data(log_dir: Path, target_date: date) -> Dict[str, Any]:
    """Load JSON data for a specific day"""
    log_path = log_dir / f"{target_date.isoformat()}.json"
    if log_path.exists():
        with open(log_path, 'r') as f:
            return json.load(f)
    return {}


def save_day_data(log_dir: Path, target_date: date, data: Dict[str, Any]):
    """Save JSON data for a specific day"""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{target_date.isoformat()}.json"
    
    # Ensure required fields
    data["date"] = target_date.isoformat()
    if "day_number" not in data:
        data["day_number"] = find_day_number(log_dir, target_date)
    
    with open(log_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Also write markdown version
    write_markdown_log(log_dir, target_date, data)


def find_day_number(log_dir: Path, target_date: date) -> int:
    """Calculate day number based on existing files"""
    if not log_dir.exists():
        return 1
    
    count = 0
    for path in log_dir.glob("*.json"):
        try:
            stem = path.stem
            file_date = date.fromisoformat(stem)
            if file_date < target_date:
                count += 1
        except ValueError:
            continue
    
    return max(1, count + 1)


def write_markdown_log(log_dir: Path, target_date: date, data: Dict[str, Any]):
    """Write human-readable markdown version"""
    md_path = log_dir / f"{target_date.isoformat()}.md"
    
    day_num = data.get("day_number", 1)
    intention = data.get("intention", "")
    
    md_content = f"# 75z – Day {day_num} ({target_date.isoformat()})\n\n"
    
    if intention:
        md_content += f"**Intention:** {intention}\n\n"
    
    # Loops
    loops = data.get("loops", {})
    for loop_name in ["BUILD", "BODY", "SYSTEM"]:
        loop_data = loops.get(loop_name, {})
        completed = loop_data.get("completed", False)
        status = "✓" if completed else " "
        
        md_content += f"## {status} {loop_name}\n\n"
        
        if completed:
            edge = loop_data.get("edge")
            surprise = loop_data.get("surprise", "")
            understanding = loop_data.get("understanding_change", "")
            
            if edge:
                md_content += f"- Edge: {edge}/10\n"
            if surprise:
                md_content += f"- Surprise: {surprise}\n"
            if understanding:
                md_content += f"- Understanding: {understanding}\n"
            md_content += "\n"
    
    # Insight
    insight = data.get("insight", {})
    if insight:
        md_content += "## ✓ INSIGHT\n\n"
        learning = insight.get("learning", "")
        tiny_change = insight.get("tiny_change", "")
        belief_update = insight.get("belief_update", "")
        
        if learning:
            md_content += f"- **Learning:** {learning}\n"
        if tiny_change:
            md_content += f"- **Tomorrow:** {tiny_change}\n"
        if belief_update:
            md_content += f"- **Belief:** {belief_update}\n"
        md_content += "\n"
    
    md_path.write_text(md_content, encoding="utf-8")


# ---------- INPUT HANDLING ----------

def getch() -> str:
    """Get a single character from stdin"""
    try:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    except:
        # Fallback for non-terminal environments
        return input().strip()[0] if sys.stdin.isatty() else 'q'


def prompt_input(prompt: str, default: str = "") -> str:
    """Get user input with prompt"""
    try:
        if default:
            print(f"{prompt} [{default}]: ", end='', flush=True)
            value = input().strip()
            return value if value else default
        else:
            print(f"{prompt}: ", end='', flush=True)
            return input().strip()
    except (EOFError, KeyboardInterrupt):
        print("\n")
        return ""


# ---------- INTERACTIVE UI ----------

def clear_screen():
    """Clear the terminal screen"""
    print(Colors.CLEAR, end='')


def get_yesterday_insight(log_dir: Path) -> Optional[Dict[str, str]]:
    """Get yesterday's insight to show today"""
    yesterday = date.today() - timedelta(days=1)
    yesterday_data = load_day_data(log_dir, yesterday)
    return yesterday_data.get("insight", {})


def display_interactive(log_dir: Path):
    """Interactive mode - press numbers to complete loops"""
    today = date.today()
    
    while True:
        data = load_day_data(log_dir, today)
        day_num = data.get("day_number") or find_day_number(log_dir, today)
        
        clear_screen()
        
        # Header with current time
        current_time = datetime.now().strftime("%H:%M")
        print(f"{Colors.BOLD}75z – Day {day_num} ({today.isoformat()}) [{current_time}]{Colors.ENDC}\n")
        
        # Yesterday's insight (if exists and not shown)
        if not data.get("intention"):
            yesterday_insight = get_yesterday_insight(log_dir)
            if yesterday_insight:
                learning = yesterday_insight.get("learning", "")
                tiny_change = yesterday_insight.get("tiny_change", "")
                
                if learning or tiny_change:
                    print(f"{Colors.BLUE}Yesterday:{Colors.ENDC}")
                    if learning:
                        print(f"  → {learning}")
                    if tiny_change:
                        print(f"  → {tiny_change}")
                    print()
        
        # Intention
        intention = data.get("intention", "")
        if intention:
            print(f"{Colors.BOLD}Intention:{Colors.ENDC} {intention}\n")
        else:
            print(f"{Colors.YELLOW}No intention set{Colors.ENDC}\n")
        
        # Show active timer
        if "timer_start" in data:
            timer_loop = data.get("timer_loop", "")
            start_time = datetime.fromisoformat(data["timer_start"])
            elapsed = int((datetime.now() - start_time).total_seconds() / 60)
            print(f"{Colors.GREEN}⏱ Timer running: {timer_loop} ({elapsed}m){Colors.ENDC}\n")
        
        # Progress bar
        loops = data.get("loops", {})
        insight = data.get("insight", {})
        
        completed_count = sum(1 for loop in ["BUILD", "BODY", "SYSTEM"] if loops.get(loop, {}).get("completed", False))
        if insight.get("learning"):
            completed_count += 1
        
        total = 4
        progress = completed_count / total
        bar_length = 40
        filled = int(bar_length * progress)
        bar = "█" * filled + "░" * (bar_length - filled)
        percentage = int(progress * 100)
        
        color = Colors.GREEN if progress == 1.0 else Colors.YELLOW if progress > 0 else Colors.RED
        print(f"Progress: [{color}{bar}{Colors.ENDC}] {completed_count}/{total} ({percentage}%)\n")
        
        # Menu items with timing info
        print(f"{Colors.BOLD}Loops:{Colors.ENDC}")
        
        for i, loop_name in enumerate(["BUILD", "BODY", "SYSTEM"], 1):
            loop_data = loops.get(loop_name, {})
            completed = loop_data.get("completed", False)
            edge = loop_data.get("edge")
            time_info = LOOP_INFO[loop_name]["time"]
            
            if completed:
                status = f"{Colors.GREEN}✓{Colors.ENDC}"
                edge_str = f" {Colors.BLUE}(edge={edge}){Colors.ENDC}" if edge else ""
                duration = loop_data.get("duration_min")
                time_str = f" {Colors.GREEN}{duration}m{Colors.ENDC}" if duration else ""
                print(f"  {i}. {status} {loop_name} ({time_info}){edge_str}{time_str}")
            else:
                status = " "
                print(f"  {i}. {status} {loop_name} ({time_info})")
        
        # Insight
        if insight.get("learning"):
            print(f"  4. {Colors.GREEN}✓{Colors.ENDC} INSIGHT (5-10m)")
        else:
            print(f"  4.   INSIGHT (5-10m)")
        
        print()
        
        # Commands
        print(f"{Colors.BOLD}Commands:{Colors.ENDC}")
        if not intention:
            print(f"  s - Set intention")
        print(f"  1-3 - Complete loop")
        print(f"  4 - Add insight")
        print(f"  t - Start timer")
        print(f"  i - Info about loops")
        print(f"  v - View details")
        print(f"  p - Past logs")
        print(f"  r - Reset today")
        print(f"  q - Quit")
        
        print(f"\n{Colors.YELLOW}>{Colors.ENDC} ", end='', flush=True)
        
        # Get input
        key = getch()
        
        if key == 'q' or key == 'Q':
            print("\n")
            break
        elif key == 's' or key == 'S':
            if not intention:
                print("\n")
                intention = prompt_input("What are you building today?")
                if intention:
                    data["intention"] = intention
                    data["day_number"] = day_num
                    save_day_data(log_dir, today, data)
        elif key in '123':
            loop_idx = int(key) - 1
            loop_name = ["BUILD", "BODY", "SYSTEM"][loop_idx]
            
            if "loops" not in data:
                data["loops"] = {}
            
            loop_data = data["loops"].get(loop_name, {})
            
            if not loop_data.get("completed"):
                loop_info = LOOP_INFO[loop_name]
                print(f"\n\n{Colors.BOLD}{loop_name} Loop{Colors.ENDC}")
                print(f"{Colors.BLUE}{loop_info['description']}{Colors.ENDC}")
                print(f"Target time: {loop_info['time']}\n")
                
                # Check if timer was running
                if "timer_start" in data and data.get("timer_loop") == loop_name:
                    start_time = datetime.fromisoformat(data["timer_start"])
                    duration = int((datetime.now() - start_time).total_seconds() / 60)
                    print(f"{Colors.GREEN}Timer: {duration} minutes{Colors.ENDC}\n")
                    loop_data["duration_min"] = duration
                    # Clear timer
                    del data["timer_start"]
                    del data["timer_loop"]
                
                edge_input = prompt_input("Edge/difficulty (1-10)", "5")
                try:
                    edge = int(edge_input) if edge_input else 5
                    if 1 <= edge <= 10:
                        loop_data["edge"] = edge
                except ValueError:
                    loop_data["edge"] = 5
                
                # Use custom questions if available
                custom_q = loop_info.get("questions", {})
                
                surprise_prompt = custom_q.get("surprise", "What surprised you?")
                surprise = prompt_input(surprise_prompt)
                if surprise:
                    loop_data["surprise"] = surprise
                
                understanding_prompt = custom_q.get("understanding", "What changed in your understanding?")
                understanding = prompt_input(understanding_prompt)
                if understanding:
                    loop_data["understanding_change"] = understanding
                
                loop_data["completed"] = True
                data["loops"][loop_name] = loop_data
                save_day_data(log_dir, today, data)
        elif key == '4':
            if not insight.get("learning"):
                print(f"\n\n{Colors.BOLD}INSIGHT - Knowledge Extraction{Colors.ENDC}\n")
                
                learning = prompt_input("What did you learn today?")
                if learning:
                    if "insight" not in data:
                        data["insight"] = {}
                    data["insight"]["learning"] = learning
                    
                    tiny_change = prompt_input("What small change for tomorrow?")
                    if tiny_change:
                        data["insight"]["tiny_change"] = tiny_change
                    
                    belief = prompt_input("What belief did you update?")
                    if belief:
                        data["insight"]["belief_update"] = belief
                    
                    save_day_data(log_dir, today, data)
        elif key == 'v' or key == 'V':
            view_details(log_dir, today)
            print("\nPress any key to continue...")
            getch()
        elif key == 'p' or key == 'P':
            view_past_logs(log_dir)
            print("\nPress any key to continue...")
            getch()
        elif key == 't' or key == 'T':
            # Timer functionality
            print("\n")
            print(f"{Colors.BOLD}Start Timer{Colors.ENDC}\n")
            print("Which loop?")
            for i, loop_name in enumerate(["BUILD", "BODY", "SYSTEM"], 1):
                print(f"  {i}. {loop_name} ({LOOP_INFO[loop_name]['time']})")
            print()
            timer_key = prompt_input("Select (1-3)")
            if timer_key in '123':
                loop_idx = int(timer_key) - 1
                loop_name = ["BUILD", "BODY", "SYSTEM"][loop_idx]
                data["timer_start"] = datetime.now().isoformat()
                data["timer_loop"] = loop_name
                save_day_data(log_dir, today, data)
                print(f"\n{Colors.GREEN}Timer started for {loop_name}{Colors.ENDC}")
                print("Complete the loop with the same number when done.")
                time.sleep(2)
        elif key == 'i' or key == 'I':
            # Show info about loops
            print("\n")
            print(f"{Colors.BOLD}Loop Information{Colors.ENDC}\n")
            for loop_name in ["BUILD", "BODY", "SYSTEM", "INSIGHT"]:
                info = LOOP_INFO[loop_name]
                print(f"{Colors.BOLD}{loop_name} ({info['time']}){Colors.ENDC}")
                print(f"  {info['description']}")
                print(f"  Questions:")
                for prompt in info['prompts']:
                    print(f"    • {prompt}")
                print()
            print("\nPress any key to continue...")
            getch()
        elif key == 'r' or key == 'R':
            # Reset today
            print("\n")
            print(f"{Colors.YELLOW}Reset today's progress?{Colors.ENDC}")
            print("This will clear all loops and insights for today.")
            confirm = prompt_input("Type 'yes' to confirm")
            if confirm.lower() == 'yes':
                # Keep intention but clear loops
                new_data = {
                    "date": today.isoformat(),
                    "day_number": day_num,
                    "intention": data.get("intention", "")
                }
                save_day_data(log_dir, today, new_data)
                print(f"\n{Colors.GREEN}Today's progress reset{Colors.ENDC}")
                time.sleep(1)
        elif key == '\x03':  # Ctrl+C
            print("\n")
            break


def view_details(log_dir: Path, target_date: date):
    """View detailed log for a specific day"""
    data = load_day_data(log_dir, target_date)
    
    print(f"\n{Colors.BOLD}Details for {target_date.isoformat()}{Colors.ENDC}\n")
    
    intention = data.get("intention", "")
    if intention:
        print(f"{Colors.BOLD}Intention:{Colors.ENDC} {intention}\n")
    
    loops = data.get("loops", {})
    for loop_name in ["BUILD", "BODY", "SYSTEM"]:
        loop_data = loops.get(loop_name, {})
        if loop_data.get("completed"):
            print(f"{Colors.BOLD}{loop_name}:{Colors.ENDC}")
            edge = loop_data.get("edge")
            if edge:
                print(f"  Edge: {edge}/10")
            surprise = loop_data.get("surprise")
            if surprise:
                print(f"  Surprise: {surprise}")
            understanding = loop_data.get("understanding_change")
            if understanding:
                print(f"  Understanding: {understanding}")
            print()
    
    insight = data.get("insight", {})
    if insight.get("learning"):
        print(f"{Colors.BOLD}INSIGHT:{Colors.ENDC}")
        print(f"  Learning: {insight.get('learning', '')}")
        tiny_change = insight.get("tiny_change")
        if tiny_change:
            print(f"  Tomorrow: {tiny_change}")
        belief = insight.get("belief_update")
        if belief:
            print(f"  Belief: {belief}")


def view_past_logs(log_dir: Path):
    """View past logs"""
    if not log_dir.exists():
        print("No logs found")
        return
    
    logs = sorted([p for p in log_dir.glob("*.json")], reverse=True)[:7]  # Last 7 days
    
    print(f"\n{Colors.BOLD}Past 7 Days:{Colors.ENDC}\n")
    
    for log_path in logs:
        try:
            log_date = date.fromisoformat(log_path.stem)
            data = load_day_data(log_dir, log_date)
            
            loops = data.get("loops", {})
            completed = sum(1 for l in ["BUILD", "BODY", "SYSTEM"] if loops.get(l, {}).get("completed"))
            insight_done = "✓" if data.get("insight", {}).get("learning") else " "
            
            intention = data.get("intention", "")[:30] + "..." if len(data.get("intention", "")) > 30 else data.get("intention", "")
            
            print(f"{log_date.isoformat()} - [{completed}/3] Loops [{insight_done}] Insight")
            if intention:
                print(f"  → {intention}")
            
            learning = data.get("insight", {}).get("learning", "")
            if learning:
                learning_short = learning[:50] + "..." if len(learning) > 50 else learning
                print(f"  {Colors.GREEN}↳ {learning_short}{Colors.ENDC}")
            print()
        except:
            continue


# ---------- CLI ----------

def main():
    parser = argparse.ArgumentParser(
        description="75z Knowledge Engine – Interactive Naval-style iteration loop"
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=DEFAULT_LOG_DIR,
        help=f"Directory for logs (default: {DEFAULT_LOG_DIR})",
    )
    
    args = parser.parse_args()
    log_dir: Path = args.log_dir
    
    # Check if we can run interactive mode
    if not sys.stdin.isatty():
        # Fallback to simple status display
        today = date.today()
        data = load_day_data(log_dir, today)
        day_num = data.get("day_number") or find_day_number(log_dir, today)
        
        print(f"\n75z – Day {day_num} ({today.isoformat()})\n")
        
        intention = data.get("intention", "")
        if intention:
            print(f"Intention: {intention}\n")
        
        loops = data.get("loops", {})
        for loop_name in ["BUILD", "BODY", "SYSTEM"]:
            loop_data = loops.get(loop_name, {})
            completed = loop_data.get("completed", False)
            status = "✓" if completed else " "
            edge = loop_data.get("edge")
            edge_str = f" (edge={edge})" if edge else ""
            print(f"  [{status}] {loop_name}{edge_str}")
        
        insight = data.get("insight", {})
        status = "✓" if insight.get("learning") else " "
        print(f"  [{status}] INSIGHT\n")
        return
    
    # Run interactive mode
    try:
        display_interactive(log_dir)
    except KeyboardInterrupt:
        print("\n")
    except Exception as e:
        # Fallback to simple display on error
        print(f"\nCannot run interactive mode: {e}")
        print("Run in a proper terminal for interactive features.\n")
        
        # Show simple status
        today = date.today()
        data = load_day_data(log_dir, today)
        day_num = data.get("day_number") or find_day_number(log_dir, today)
        
        print(f"75z – Day {day_num} ({today.isoformat()})\n")
        
        intention = data.get("intention", "")
        if intention:
            print(f"Intention: {intention}\n")
        
        loops = data.get("loops", {})
        for loop_name in ["BUILD", "BODY", "SYSTEM"]:
            loop_data = loops.get(loop_name, {})
            completed = loop_data.get("completed", False)
            status = "✓" if completed else " "
            edge = loop_data.get("edge")
            edge_str = f" (edge={edge})" if edge else ""
            print(f"  [{status}] {loop_name}{edge_str}")
        
        insight = data.get("insight", {})
        status = "✓" if insight.get("learning") else " "
        print(f"  [{status}] INSIGHT\n")


if __name__ == "__main__":
    main()
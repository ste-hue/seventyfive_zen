#!/usr/bin/env python3
"""
75z Knowledge Engine - Interactive Naval-style iteration loop
Do → See → Understand → Change → Repeat

ENFORCEMENT MODE: The loop is enforced, not described.
Inner state → attention → word → action → result
"""

import argparse
import json
import sys
import termios
import time
import tty
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

# Import enforcement gates
from enforcement_gates import (
    BACKWARD_DEBUG_THRESHOLD,
    STATE_COHERENCE_THRESHOLD,
    enforce_concrete_insight,
    gate_1_state_coherence,
    gate_2_causality_chain,
    gate_3_backward_debug,
    gate_4_daily_coherence,
)

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
            "What will you ship today?",
        ],
        "questions": {
            "surprise": "What was unexpected in the code/design?",
            "understanding": "What pattern or concept clicked?",
        },
    },
    "BODY": {
        "time": "20-30m",
        "description": "Physical training - push/dips/KB/walk",
        "prompts": ["What exercise?", "How many reps/duration?", "How do you feel?"],
        "questions": {
            "surprise": "What felt different in your body today?",
            "understanding": "What did you notice about form/breathing/energy?",
        },
    },
    "SYSTEM": {
        "time": "10-15m",
        "description": "Simplify one thing - file/config/process",
        "prompts": [
            "What needs simplifying?",
            "What can you delete?",
            "How to make it cleaner?",
        ],
        "questions": {
            "surprise": "What complexity was hiding in plain sight?",
            "understanding": "What principle of simplicity applied here?",
        },
    },
    "INSIGHT": {
        "time": "5-10m",
        "description": "Extract today's learning",
        "prompts": [
            "What did you learn?",
            "What tiny change for tomorrow?",
            "What belief updated?",
        ],
    },
}


# ANSI Colors
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    ENDC = "\033[0m"
    CLEAR = "\033[2J\033[H"


# ---------- DATA MODEL ----------


def load_day_data(log_dir: Path, target_date: date) -> Dict[str, Any]:
    """Load JSON data for a specific day"""
    log_path = log_dir / f"{target_date.isoformat()}.json"
    if log_path.exists():
        with open(log_path, "r") as f:
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

    with open(log_path, "w") as f:
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
        md_content += f"**Intention:** {intention}\n"

    # State coherence score
    state_score = data.get("state_coherence_score")
    if state_score:
        md_content += f"**State Coherence:** {state_score}/10\n"
    md_content += "\n"

    # Loops with causality chains
    loops = data.get("loops", {})
    for loop_name in ["BUILD", "BODY", "SYSTEM"]:
        loop_data = loops.get(loop_name, {})
        completed = loop_data.get("completed", False)
        status = "✓" if completed else " "

        md_content += f"## [{status}] {loop_name}\n\n"

        if completed:
            # New enforcement format (causality chain)
            attention = loop_data.get("attention", "")
            action = loop_data.get("action", "")
            result = loop_data.get("result", "")
            edge = loop_data.get("edge")

            if attention or action or result:
                md_content += f"**Causality Chain:**\n"
                if attention:
                    md_content += f"- Attention: {attention}\n"
                if action:
                    md_content += f"- Action: {action}\n"
                if result:
                    md_content += f"- Result: {result}\n"
            else:
                # Fallback to old format if present
                did = loop_data.get("did", "")
                shift = loop_data.get("shift", "")
                if did:
                    md_content += f"- Did: {did}\n"
                if shift:
                    md_content += f"- Shift: {shift}\n"

            if edge is not None:
                md_content += f"- Edge: {edge}/10\n"

            # Debug info if present
            debug = loop_data.get("debug")
            if debug:
                md_content += (
                    f"\n**Backward Debug (edge < {BACKWARD_DEBUG_THRESHOLD}):**\n"
                )
                root_cause = debug.get("root_cause_state", "")
                if root_cause:
                    md_content += f"- Root Cause: {root_cause}\n"

            md_content += "\n"

    # Insight
    insight = data.get("insight", {})
    if insight:
        md_content += "## [✓] INSIGHT\n\n"
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

    # Coherence check indicator
    if data.get("daily_coherence_checked"):
        md_content += "---\n**Daily Coherence Check:** Passed ✓\n"

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
        if sys.stdin.isatty():
            user_input = input().strip()
            return user_input[0] if user_input else "q"
        else:
            return "q"


def prompt_input(prompt: str, default: str = "") -> str:
    """Get user input with prompt"""
    try:
        if default:
            print(f"{prompt} [{default}]: ", end="", flush=True)
            value = input().strip()
            return value if value else default
        else:
            print(f"{prompt}: ", end="", flush=True)
            return input().strip()
    except (EOFError, KeyboardInterrupt):
        print("\n")
        return ""


# ---------- INTERACTIVE UI ----------


def clear_screen():
    """Clear the terminal screen"""
    print(Colors.CLEAR, end="")


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
        print(
            f"{Colors.BOLD}75z ENFORCEMENT MODE – Day {day_num} ({today.isoformat()}) [{current_time}]{Colors.ENDC}"
        )
        print(
            f"{Colors.BLUE}Inner state → attention → word → action → result{Colors.ENDC}\n"
        )

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

        # Intention with state coherence
        intention = data.get("intention", "")
        if intention:
            state_score = data.get("state_coherence_score", "?")
            print(f"{Colors.BOLD}Intention:{Colors.ENDC} {intention}")
            print(f"{Colors.BOLD}State Coherence:{Colors.ENDC} {state_score}/10\n")
        else:
            print(
                f"{Colors.YELLOW}⚠ No intention set (inner state undefined){Colors.ENDC}\n"
            )

        # Show active timer
        if "timer_start" in data:
            timer_loop = data.get("timer_loop", "")
            start_time = datetime.fromisoformat(data["timer_start"])
            elapsed = int((datetime.now() - start_time).total_seconds() / 60)
            print(
                f"{Colors.GREEN}⏱ Timer running: {timer_loop} ({elapsed}m){Colors.ENDC}\n"
            )

        # Progress bar
        loops = data.get("loops", {})
        insight = data.get("insight", {})

        completed_count = sum(
            1
            for loop in ["BUILD", "BODY", "SYSTEM"]
            if loops.get(loop, {}).get("completed", False)
        )
        if insight.get("learning"):
            completed_count += 1

        total = 4
        progress = completed_count / total
        bar_length = 40
        filled = int(bar_length * progress)
        bar = "█" * filled + "░" * (bar_length - filled)
        percentage = int(progress * 100)

        color = (
            Colors.GREEN
            if progress == 1.0
            else Colors.YELLOW
            if progress > 0
            else Colors.RED
        )
        print(
            f"Progress: [{color}{bar}{Colors.ENDC}] {completed_count}/{total} ({percentage}%)\n"
        )

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
                time_str = (
                    f" {Colors.GREEN}{duration}m{Colors.ENDC}" if duration else ""
                )
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

        print(f"\n{Colors.YELLOW}>{Colors.ENDC} ", end="", flush=True)

        # Get input
        key = getch()

        if key == "q" or key == "Q":
            print("\n")
            break
        elif key == "s" or key == "S":
            current_intention = data.get("intention", "")
            if not current_intention:
                print("\n")
                intention_text = prompt_input(
                    "What is your intention today? (inner state)"
                )
                if intention_text:
                    # GATE 1: State coherence check when setting intention
                    is_coherent, coherence_score = gate_1_state_coherence()
                    if is_coherent:
                        data["intention"] = intention_text
                        data["day_number"] = day_num
                        data["state_coherence_checked"] = True
                        data["state_coherence_score"] = coherence_score
                        save_day_data(log_dir, today, data)
                        print(
                            f"\n{Colors.GREEN}✓ Intention saved with coherence score: {coherence_score}/10{Colors.ENDC}"
                        )
                        time.sleep(2)
                    else:
                        print(
                            f"\n{Colors.YELLOW}Intention not saved. Reset state and try again.{Colors.ENDC}"
                        )
                        time.sleep(2)
        elif key in "123":
            loop_idx = int(key) - 1
            loop_name = ["BUILD", "BODY", "SYSTEM"][loop_idx]

            # ENFORCE: Must have intention first
            if not data.get("intention"):
                print(
                    f"\n{Colors.RED}✗ BLOCKED: Set intention first (press 's'){Colors.ENDC}"
                )
                time.sleep(2)
                continue

            # ENFORCE: State coherence check (once per day)
            if not data.get("state_coherence_checked"):
                is_coherent, coherence_score = gate_1_state_coherence()
                if not is_coherent:
                    continue
                data["state_coherence_checked"] = True
                data["state_coherence_score"] = coherence_score
                save_day_data(log_dir, today, data)

            if "loops" not in data:
                data["loops"] = {}

            # Stop timer if running for this loop (regardless of completion status)
            if "timer_start" in data and data.get("timer_loop") == loop_name:
                start_time = datetime.fromisoformat(data["timer_start"])
                duration = int((datetime.now() - start_time).total_seconds() / 60)
                print(f"\n{Colors.GREEN}Timer stopped: {duration} minutes{Colors.ENDC}")
                # Store duration to be added to the session
                current_duration = duration
                # Clear timer
                del data["timer_start"]
                del data["timer_loop"]
                save_day_data(log_dir, today, data)
                time.sleep(1)
            else:
                current_duration = 0

            # Support multiple sessions - keep old structure but allow re-doing
            loop_data = data["loops"].get(loop_name, {})

            # If already completed, ask if they want to do another session
            if loop_data.get("completed"):
                print(
                    f"\n{Colors.YELLOW}Already completed {loop_name} today.{Colors.ENDC}"
                )
                another = prompt_input("Do another session? (y/n)", "n")
                if another.lower() != "y":
                    continue
                # Store previous session and start fresh
                if "sessions" not in loop_data:
                    # Convert first session to array
                    first_session = {
                        "did": loop_data.get("did"),
                        "shift": loop_data.get("shift"),
                        "edge": loop_data.get("edge"),
                        "duration_min": loop_data.get("duration_min"),
                    }
                    loop_data["sessions"] = [first_session]
                else:
                    # Add current to sessions
                    current_session = {
                        "did": loop_data.get("did"),
                        "shift": loop_data.get("shift"),
                        "edge": loop_data.get("edge"),
                        "duration_min": loop_data.get("duration_min"),
                    }
                    loop_data["sessions"].append(current_session)
                # Clear for new session
                loop_data = {"completed": False, "sessions": loop_data["sessions"]}

            if not loop_data.get("completed"):
                loop_info = LOOP_INFO[loop_name]
                print(f"\n\n{Colors.BOLD}═══ {loop_name} LOOP ═══{Colors.ENDC}")
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

                # GATE 2: Causality chain enforcement
                intention = data.get("intention", "")
                causality = gate_2_causality_chain(loop_name, intention)

                if not causality:
                    print(
                        f"\n{Colors.RED}✗ Loop aborted (causality chain incomplete){Colors.ENDC}"
                    )
                    time.sleep(2)
                    continue

                # Store causality chain
                loop_data["attention"] = causality["attention"]
                loop_data["action"] = causality["action"]
                loop_data["result"] = causality["result"]

                # Edge score
                print(f"\n{Colors.BOLD}Edge/Difficulty:{Colors.ENDC}")
                edge_input = prompt_input("Rate 1-10")
                try:
                    edge = int(edge_input)
                    if edge >= 1 and edge <= 10:
                        loop_data["edge"] = edge

                        # GATE 3: Backward debug if low edge
                        if edge < BACKWARD_DEBUG_THRESHOLD:
                            debug_data = gate_3_backward_debug(loop_name, edge)
                            loop_data["debug"] = debug_data
                    else:
                        edge = None
                except ValueError:
                    edge = None

                # Keep legacy fields for compatibility
                loop_data["did"] = causality["action"]
                loop_data["shift"] = causality["result"]

                loop_data["completed"] = True
                data["loops"][loop_name] = loop_data
                save_day_data(log_dir, today, data)

                print(f"\n{Colors.GREEN}✓ {loop_name} completed{Colors.ENDC}")
                time.sleep(1)

                # GATE 4: Daily coherence check (after first loop)
                if not data.get("daily_coherence_checked"):
                    completed_loops = [
                        name
                        for name in ["BUILD", "BODY", "SYSTEM"]
                        if data.get("loops", {}).get(name, {}).get("completed", False)
                    ]
                    if gate_4_daily_coherence(intention, completed_loops):
                        data["daily_coherence_checked"] = True
                        save_day_data(log_dir, today, data)
        elif key == "4":
            if not insight.get("learning"):
                # Must have completed at least one loop
                loops_completed = sum(
                    1
                    for l in ["BUILD", "BODY", "SYSTEM"]
                    if data.get("loops", {}).get(l, {}).get("completed", False)
                )

                if loops_completed == 0:
                    print(
                        f"\n{Colors.RED}✗ Complete at least one loop first{Colors.ENDC}"
                    )
                    time.sleep(2)
                    continue

                print(
                    f"\n\n{Colors.BOLD}═══ INSIGHT - Knowledge Extraction ═══{Colors.ENDC}\n"
                )

                learning = prompt_input(
                    "What did you learn today that wasn't obvious before?"
                )
                if learning:
                    if "insight" not in data:
                        data["insight"] = {}
                    data["insight"]["learning"] = learning

                    tiny_change = prompt_input(
                        "What small change will you apply tomorrow?"
                    )

                    # ENFORCE: Tiny change must be concrete
                    if tiny_change:
                        tiny_change = enforce_concrete_insight(tiny_change)
                        if tiny_change:
                            data["insight"]["tiny_change"] = tiny_change

                    save_day_data(log_dir, today, data)
                    print(f"\n{Colors.GREEN}✓ Insight saved{Colors.ENDC}")
                    time.sleep(1)
        elif key == "v" or key == "V":
            view_details(log_dir, today)
            print("\nPress any key to continue...")
            getch()
        elif key == "p" or key == "P":
            view_past_logs(log_dir)
            print("\nPress any key to continue...")
            getch()
        elif key == "t" or key == "T":
            # Timer functionality
            print("\n")
            print(f"{Colors.BOLD}Start Timer{Colors.ENDC}\n")
            print("Which loop?")
            for i, loop_name in enumerate(["BUILD", "BODY", "SYSTEM"], 1):
                print(f"  {i}. {loop_name} ({LOOP_INFO[loop_name]['time']})")
            print()
            timer_key = prompt_input("Select (1-3)")
            if timer_key in "123":
                loop_idx = int(timer_key) - 1
                loop_name = ["BUILD", "BODY", "SYSTEM"][loop_idx]
                data["timer_start"] = datetime.now().isoformat()
                data["timer_loop"] = loop_name
                save_day_data(log_dir, today, data)
                print(f"\n{Colors.GREEN}Timer started for {loop_name}{Colors.ENDC}")
                print("Complete the loop with the same number when done.")
                time.sleep(2)
        elif key == "i" or key == "I":
            # Show info about loops
            print("\n")
            print(f"{Colors.BOLD}Loop Information{Colors.ENDC}\n")
            for loop_name in ["BUILD", "BODY", "SYSTEM", "INSIGHT"]:
                info = LOOP_INFO[loop_name]
                print(f"{Colors.BOLD}{loop_name} ({info['time']}){Colors.ENDC}")
                print(f"  {info['description']}")
                print(f"  Questions:")
                for prompt in info["prompts"]:
                    print(f"    • {prompt}")
                print()
            print("\nPress any key to continue...")
            getch()
        elif key == "r" or key == "R":
            # Reset today
            print("\n")
            print(f"{Colors.YELLOW}Reset today's progress?{Colors.ENDC}")
            print("This will clear all loops and insights for today.")
            confirm = prompt_input("Type 'yes' to confirm")
            if confirm.lower() == "yes":
                # Clear everything including intention
                new_data = {
                    "date": today.isoformat(),
                    "day_number": day_num,
                }
                save_day_data(log_dir, today, new_data)
                print(f"\n{Colors.GREEN}Today's progress reset{Colors.ENDC}")
                time.sleep(1)
        elif key == "\x03":  # Ctrl+C
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

            # Show causality chain if present
            attention = loop_data.get("attention")
            action = loop_data.get("action")
            result = loop_data.get("result")

            if attention:
                print(f"  Attention: {attention}")
            if action:
                print(f"  Action: {action}")
            if result:
                print(f"  Result: {result}")

            edge = loop_data.get("edge")
            if edge is not None:
                print(f"  Edge: {edge}/10")

            # Show debug info if present
            debug = loop_data.get("debug")
            if debug:
                print(
                    f"  {Colors.RED}Debug (root cause):{Colors.ENDC} {debug.get('root_cause_state', '')}"
                )

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
            completed = sum(
                1
                for l in ["BUILD", "BODY", "SYSTEM"]
                if loops.get(l, {}).get("completed")
            )
            insight_done = "✓" if data.get("insight", {}).get("learning") else " "

            intention = (
                data.get("intention", "")[:30] + "..."
                if len(data.get("intention", "")) > 30
                else data.get("intention", "")
            )

            print(
                f"{log_date.isoformat()} - [{completed}/3] Loops [{insight_done}] Insight"
            )
            if intention:
                print(f"  → {intention}")

            learning = data.get("insight", {}).get("learning", "")
            if learning:
                learning_short = (
                    learning[:50] + "..." if len(learning) > 50 else learning
                )
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

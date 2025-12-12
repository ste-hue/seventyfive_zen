#!/usr/bin/env python3
"""
75z - Alignment Journaling OS
You are not journaling to remember. You are journaling to become inevitable.
"""

import json
from datetime import date, timedelta
from pathlib import Path

DEFAULT_LOG_DIR = Path.home() / "75z_logs"


def clear():
    print("\033[2J\033[H", end="")


def load_log(target_date):
    """Load log for a specific date"""
    log_dir = Path(DEFAULT_LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{target_date.isoformat()}.json"

    if log_path.exists():
        with open(log_path, "r") as f:
            return json.load(f)
    return {}


def save_log(target_date, data):
    """Save log with markdown mirror"""
    log_dir = Path(DEFAULT_LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{target_date.isoformat()}.json"

    data["date"] = target_date.isoformat()

    with open(log_path, "w") as f:
        json.dump(data, f, indent=2)

    # Write markdown mirror
    md_path = log_dir / f"{target_date.isoformat()}.md"
    md = f"# {target_date.isoformat()}\n\n"

    if "result" in data:
        md += f"**RESULT:** {data['result']}\n\n"
    if "attention" in data:
        md += f"**ATTENTION HELD:** {data['attention']}\n"
    if "drift" in data and data["drift"]:
        md += f"**DRIFT:** {data['drift']}\n"
    if "tomorrow" in data:
        md += f"\n**TOMORROW LOCK:** {data['tomorrow']}\n"

    md_path.write_text(md)


def show_alignment():
    """Read ALIGNMENT.md if it exists"""
    alignment_path = Path(__file__).parent / "ALIGNMENT.md"
    if alignment_path.exists():
        print(alignment_path.read_text())
        print("\n" + "─" * 60 + "\n")
        input("Press Enter to continue...")


def reconcile():
    """Evening reconciliation - the core writing surface"""
    clear()
    print("RECONCILIATION\n")

    data = load_log(date.today())

    print("RESULT (1 sentence, concrete):")
    result = input("→ ").strip()

    if not result:
        print("\nNo result captured.\n")
        return

    print("\nWHERE ATTENTION HELD (1 sentence):")
    attention = input("→ ").strip()

    print("\nWHERE IT DRIFTED (optional, leave blank if none):")
    drift = input("→ ").strip()

    print("\nTOMORROW LOCK (1 unavoidable action):")
    tomorrow = input("→ ").strip()

    data["result"] = result
    data["attention"] = attention
    data["drift"] = drift if drift else None
    data["tomorrow"] = tomorrow

    save_log(date.today(), data)

    print("\n✓ Reconciled\n")


def view_today():
    """Mirror - reinforces identity"""
    clear()
    data = load_log(date.today())

    if not data.get("result"):
        print("TODAY\n")
        print("Not yet reconciled.\n")
        print("Press 4 to reconcile.\n")
        return

    print("MIRROR\n")
    print(f"RESULT: {data.get('result', '')}\n")
    print(f"ATTENTION: {data.get('attention', '')}")

    if data.get("drift"):
        print(f"DRIFT: {data.get('drift', '')}")

    print(f"\nTOMORROW LOCK: {data.get('tomorrow', '')}\n")

    input("Press Enter to continue...")


def view_past():
    """Pattern detection by proximity - read only"""
    clear()
    log_dir = Path(DEFAULT_LOG_DIR)

    if not log_dir.exists():
        print("No logs yet.\n")
        input("Press Enter to continue...")
        return

    logs = sorted([p for p in log_dir.glob("*.json")], reverse=True)[:7]

    print("PAST 7 DAYS\n")

    for log_path in logs:
        try:
            log_date = date.fromisoformat(log_path.stem)
            data = load_log(log_date)

            result = data.get("result", "—")
            tomorrow = data.get("tomorrow", "—")

            print(f"{log_date.isoformat()}")
            print(f"  Result: {result[:60]}{'...' if len(result) > 60 else ''}")
            print(f"  Lock: {tomorrow[:60]}{'...' if len(tomorrow) > 60 else ''}")

            if data.get("drift"):
                print(
                    f"  Drift: {data['drift'][:60]}{'...' if len(data['drift']) > 60 else ''}"
                )
            print()
        except:
            continue

    input("Press Enter to continue...")


def reset_today():
    """State correction, not failure"""
    clear()
    print("RESET\n")
    print("Delete today's log and start clean?\n")
    confirm = input("Type 'yes' to confirm: ").strip()

    if confirm.lower() == "yes":
        log_path = Path(DEFAULT_LOG_DIR) / f"{date.today().isoformat()}.json"
        md_path = Path(DEFAULT_LOG_DIR) / f"{date.today().isoformat()}.md"

        if log_path.exists():
            log_path.unlink()
        if md_path.exists():
            md_path.unlink()

        print("\n✓ Reset complete\n")
        print("Re-read ALIGNMENT.md to reset state.\n")
    else:
        print("\nCancelled.\n")

    input("Press Enter to continue...")


def show_info():
    """Minimal info - no explanation of the OS"""
    clear()
    print("75z - ALIGNMENT JOURNALING OS\n")
    print("Commands:")
    print("  a - Read ALIGNMENT.md (morning)")
    print("  4 - Reconcile (evening)")
    print("  v - View today (mirror)")
    print("  p - Past 7 days (patterns)")
    print("  r - Reset today")
    print("  i - Info (this screen)")
    print("  q - Quit\n")
    input("Press Enter to continue...")


def main():
    """Main loop - minimal surface"""
    while True:
        clear()

        data = load_log(date.today())
        reconciled = bool(data.get("result"))

        print("75z\n")

        if reconciled:
            print(f"Today: ✓ Reconciled\n")
        else:
            print(f"Today: Not yet reconciled\n")

        print("Commands: a 4 v p r i q\n")
        cmd = input("> ").strip().lower()

        if cmd == "q":
            break
        elif cmd == "a":
            show_alignment()
        elif cmd == "4":
            reconcile()
        elif cmd == "v":
            view_today()
        elif cmd == "p":
            view_past()
        elif cmd == "r":
            reset_today()
        elif cmd == "i":
            show_info()
        else:
            continue


if __name__ == "__main__":
    main()

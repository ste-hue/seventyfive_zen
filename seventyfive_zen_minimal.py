#!/usr/bin/env python3
"""
75z Minimal - Ultraminimal daily alignment tracker
No gates. No enforcement. Just clarity.
"""

import json
from datetime import date
from pathlib import Path

DEFAULT_LOG_DIR = Path.home() / "75z_logs"


def clear():
    print("\033[2J\033[H", end="")


def load_today():
    log_dir = Path(DEFAULT_LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{date.today().isoformat()}.json"

    if log_path.exists():
        with open(log_path, "r") as f:
            return json.load(f)
    return {}


def save_today(data):
    log_dir = Path(DEFAULT_LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{date.today().isoformat()}.json"

    data["date"] = date.today().isoformat()

    with open(log_path, "w") as f:
        json.dump(data, f, indent=2)

    # Write markdown
    md_path = log_dir / f"{date.today().isoformat()}.md"
    md = f"# {date.today().isoformat()}\n\n"

    if "state" in data:
        md += f"**State:** {data['state']}/10\n"
    if "focus" in data:
        md += f"**Focus:** {data['focus']}\n\n"

    if "did" in data:
        md += f"**Did:** {data['did']}\n"
    if "shifted" in data:
        md += f"**Shifted:** {data['shifted']}\n\n"

    if "tomorrow" in data:
        md += f"**Tomorrow:** {data['tomorrow']}\n"

    md_path.write_text(md)


def main():
    clear()

    print("75z minimal\n")

    data = load_today()

    # Morning
    if "state" not in data:
        print("Morning check:")
        state = input("State (1-10): ").strip()
        focus = input("Focus today: ").strip()

        data["state"] = state
        data["focus"] = focus
        save_today(data)

        print("\n✓ Set\n")
        return

    # Evening
    if "did" not in data:
        print(f"State: {data.get('state', '?')}/10")
        print(f"Focus: {data.get('focus', '')}\n")
        print("Evening review:")

        did = input("What I did: ").strip()
        shifted = input("What shifted: ").strip()
        tomorrow = input("Tomorrow: ").strip()

        data["did"] = did
        data["shifted"] = shifted
        data["tomorrow"] = tomorrow
        save_today(data)

        print("\n✓ Done\n")
        return

    # Already complete
    print(f"State: {data.get('state', '?')}/10")
    print(f"Focus: {data.get('focus', '')}\n")
    print(f"Did: {data.get('did', '')}")
    print(f"Shifted: {data.get('shifted', '')}\n")
    print(f"Tomorrow: {data.get('tomorrow', '')}\n")
    print("✓ Today complete\n")


if __name__ == "__main__":
    main()

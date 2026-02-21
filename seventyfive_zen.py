#!/usr/bin/env python3
"""
75z - Productivity OS
CLI-first for rituals. Obsidian for viewing.
"""

import json
import re
import time
import random
from datetime import date, datetime, timedelta
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"

# ─── Config ──────────────────────────────────────────────────────────────────


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        cfg["vault_path"] = Path(cfg["vault_path"]).expanduser()
        return cfg
    return {"vault_path": Path.home() / "obsidian", "alignment_path": "75z/Systems/Alignment.md"}


CFG = load_config()
VAULT = CFG["vault_path"]
Z = VAULT / "75z"


def clear():
    print("\033[2J\033[H", end="")


# ─── Daily Note I/O ──────────────────────────────────────────────────────────


def daily_path(d=None):
    d = d or date.today()
    return Z / "Daily" / f"{d.isoformat()}.md"


def sidecar_path(d=None):
    d = d or date.today()
    return Z / "Daily" / f"{d.isoformat()}.json"


def ensure_dirs():
    for sub in ["Daily", "Weekly", "Thinking", "Inbox", "Systems"]:
        (Z / sub).mkdir(parents=True, exist_ok=True)


def load_sidecar(d=None):
    p = sidecar_path(d)
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return {
        "date": (d or date.today()).isoformat(),
        "reconciled": False,
        "energy_sleep": None,
        "energy_movement": None,
        "energy_fuel": None,
        "mits": [],
        "mit_done": [],
        "captures": [],
        "habits": [],
        "streak_slip": False,
    }


def save_sidecar(data, d=None):
    ensure_dirs()
    p = sidecar_path(d)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def render_daily_note(data):
    """Render full daily note markdown from sidecar data."""
    d = data["date"]
    mits = data.get("mits", [])
    mit_done = data.get("mit_done", [])
    captures = data.get("captures", [])
    habits = data.get("habits", [])

    mit_count = len(mits)
    mit_done_count = sum(1 for x in mit_done if x)

    # Frontmatter
    fm = [
        "---",
        f"date: {d}",
        f"reconciled: {str(data.get('reconciled', False)).lower()}",
        f"energy_sleep: {data.get('energy_sleep') or 'null'}",
        f"energy_movement: {json.dumps(data.get('energy_movement')) if data.get('energy_movement') else 'null'}",
        f"energy_fuel: {json.dumps(data.get('energy_fuel')) if data.get('energy_fuel') else 'null'}",
        f"mit_count: {mit_count}",
        f"mit_done: {mit_done_count}",
        f"captures: {len(captures)}",
        f"streak_slip: {str(data.get('streak_slip', False)).lower()}",
        "---",
    ]

    lines = fm + [f"", f"# {d}", ""]

    # Morning Startup
    alignment_done = any(h.get("name") == "Morning alignment read" and h.get("done") for h in habits)
    mits_set = mit_count > 0
    lines += [
        "## Morning Startup",
        f"- [{'x' if alignment_done else ' '}] Read alignment",
        f"- [{'x' if mits_set else ' '}] Set MITs",
        "",
    ]

    # MITs
    lines.append("## 3 MITs")
    if mits:
        for i, mit in enumerate(mits):
            done = mit_done[i] if i < len(mit_done) else False
            lines.append(f"{i+1}. [{'x' if done else ' '}] {mit}")
    else:
        lines += ["1. [ ]", "2. [ ]", "3. [ ]"]
    lines.append("")

    # Captures
    lines.append("## Captures")
    if captures:
        for cap in captures:
            ts = cap.get("time", "")
            lines.append(f"- [{ts}] {cap.get('text', '')}")
    else:
        lines.append("-")
    lines.append("")

    # Energy
    sleep = data.get("energy_sleep")
    movement = data.get("energy_movement") or ""
    fuel = data.get("energy_fuel") or ""
    lines += [
        "## Energy",
        f"- **Sleep:** {f'{sleep}/10' if sleep is not None else '/10'}",
        f"- **Movement:** {movement}",
        f"- **Fuel:** {fuel}",
        "",
    ]

    # Reconcile
    lines.append("## Reconcile")
    lines.append(f"**RESULT:** {data.get('result', '')}")
    lines.append(f"**ATTENTION HELD:** {data.get('attention', '')}")
    lines.append(f"**DRIFT:** {data.get('drift', '')}")
    lines.append(f"**TOMORROW LOCK:** {data.get('tomorrow', '')}")
    lines.append("")

    # Habits
    lines.append("## Habits")
    if habits:
        for h in habits:
            lines.append(f"- [{'x' if h.get('done') else ' '}] {h['name']}")
    else:
        # Load default habits
        for name in load_habit_names():
            lines.append(f"- [ ] {name}")
    lines.append("")

    return "\n".join(lines)


def save_daily(data, d=None):
    """Save both sidecar JSON and rendered markdown daily note."""
    ensure_dirs()
    save_sidecar(data, d)
    md = render_daily_note(data)
    dp = daily_path(d)
    dp.write_text(md)


# ─── Habits ──────────────────────────────────────────────────────────────────


def load_habit_names():
    """Parse habit names from Systems/Habit Stacks.md 'Tracked Daily' section."""
    p = Z / "Systems" / "Habit Stacks.md"
    if not p.exists():
        return ["Morning alignment read", "3 MITs set", "Movement (any)", "Evening reconcile"]

    text = p.read_text()
    names = []
    in_section = False
    for line in text.splitlines():
        if "## Tracked Daily" in line:
            in_section = True
            continue
        if in_section:
            if line.startswith("##"):
                break
            m = re.match(r"- \[.\] (.+)", line)
            if m:
                names.append(m.group(1).strip())
    return names or ["Morning alignment read", "3 MITs set", "Movement (any)", "Evening reconcile"]


def ensure_habits(data):
    """Ensure today's data has a habits list matching the habit definitions."""
    names = load_habit_names()
    existing = {h["name"]: h for h in data.get("habits", [])}
    habits = []
    for name in names:
        if name in existing:
            habits.append(existing[name])
        else:
            habits.append({"name": name, "done": False})
    data["habits"] = habits
    return data


# ─── Thinking Prompts ────────────────────────────────────────────────────────

PROMPTS = [
    {"id": "avoidance", "text": "What's one thing I'm avoiding that I shouldn't be?", "theme": "Resistance"},
    {"id": "trust", "text": "What would I do if I trusted myself completely?", "theme": "Self-trust"},
    {"id": "pattern", "text": "What pattern keeps repeating that I need to address?", "theme": "Patterns"},
    {"id": "gap", "text": "What's the gap between who I am and who I'm becoming?", "theme": "Identity"},
    {"id": "decision", "text": "What decision am I delaying that already has an answer?", "theme": "Clarity"},
    {"id": "energy", "text": "Where is my energy going that doesn't serve me?", "theme": "Energy"},
    {"id": "truth", "text": "What truth am I not saying out loud?", "theme": "Honesty"},
    {"id": "fear", "text": "What would I do if I wasn't afraid?", "theme": "Fear"},
    {"id": "simple", "text": "What's the simplest next step I'm overcomplicating?", "theme": "Simplicity"},
    {"id": "surrender", "text": "What do I need to let go of?", "theme": "Release"},
]


# ─── Commands ─────────────────────────────────────────────────────────────────


def cmd_alignment():
    """Morning alignment read."""
    clear()
    p = VAULT / CFG["alignment_path"]
    if p.exists():
        print(p.read_text())
        print("\n" + "─" * 60 + "\n")
    else:
        print("Alignment file not found.\n")
        print(f"Expected at: {p}\n")

    # Mark habit
    data = load_sidecar()
    data = ensure_habits(data)
    for h in data["habits"]:
        if h["name"] == "Morning alignment read":
            h["done"] = True
    save_daily(data)

    input("Press Enter to continue...")


def cmd_mits():
    """Set or update 3 Most Important Tasks."""
    clear()
    data = load_sidecar()
    data = ensure_habits(data)

    existing = data.get("mits", [])
    mit_done = data.get("mit_done", [])

    if existing:
        print("CURRENT MITs\n")
        for i, mit in enumerate(existing):
            done = mit_done[i] if i < len(mit_done) else False
            print(f"  {'[x]' if done else '[ ]'} {i+1}. {mit}")
        print()
        print("  d - Mark done")
        print("  n - Set new MITs")
        print("  b - Back\n")

        choice = input("> ").strip().lower()
        if choice == "d":
            num = input("Which MIT? (1/2/3): ").strip()
            try:
                idx = int(num) - 1
                if 0 <= idx < len(existing):
                    while len(mit_done) <= idx:
                        mit_done.append(False)
                    mit_done[idx] = True
                    data["mit_done"] = mit_done
                    save_daily(data)
                    print(f"\n  Done: {existing[idx]}\n")
                else:
                    print("\n  Invalid number.\n")
            except ValueError:
                print("\n  Invalid input.\n")
            input("Press Enter to continue...")
            return
        elif choice != "n":
            return
        print()

    print("SET 3 MITs\n")
    print("What are the 3 most important things to do today?\n")

    mits = []
    for i in range(3):
        mit = input(f"  {i+1}. ").strip()
        if mit:
            mits.append(mit)

    if mits:
        data["mits"] = mits
        data["mit_done"] = [False] * len(mits)
        for h in data["habits"]:
            if h["name"] == "3 MITs set":
                h["done"] = True
        save_daily(data)
        print(f"\n  {len(mits)} MIT(s) set.\n")
    else:
        print("\n  No MITs set.\n")

    input("Press Enter to continue...")


def cmd_capture():
    """Quick capture to inbox."""
    clear()
    print("CAPTURE\n")
    text = input("  → ").strip()

    if not text:
        print("\n  Nothing captured.\n")
        input("Press Enter to continue...")
        return

    ts = datetime.now().strftime("%H:%M")
    capture = {"time": ts, "text": text}

    # Add to daily note
    data = load_sidecar()
    data = ensure_habits(data)
    data.setdefault("captures", []).append(capture)
    save_daily(data)

    # Also add to Inbox file
    inbox_dir = Z / "Inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    inbox_path = inbox_dir / f"{date.today().isoformat()}.md"

    if inbox_path.exists():
        content = inbox_path.read_text()
    else:
        content = f"# Inbox — {date.today().isoformat()}\n"

    content += f"\n- [{ts}] {text}"
    inbox_path.write_text(content)

    print(f"\n  Captured at {ts}\n")
    input("Press Enter to continue...")


def cmd_energy():
    """Log energy: sleep, movement, fuel."""
    clear()
    data = load_sidecar()
    data = ensure_habits(data)

    print("ENERGY LOG\n")

    print("  Sleep quality (1-10):")
    sleep = input("  → ").strip()
    try:
        sleep = int(sleep)
        sleep = max(1, min(10, sleep))
    except ValueError:
        sleep = None

    print("\n  Movement today:")
    movement = input("  → ").strip()

    print("\n  Fuel (what did you eat/drink):")
    fuel = input("  → ").strip()

    data["energy_sleep"] = sleep
    data["energy_movement"] = movement or None
    data["energy_fuel"] = fuel or None

    save_daily(data)
    print("\n  Energy logged.\n")
    input("Press Enter to continue...")


def cmd_habits():
    """Toggle habits for today."""
    clear()
    data = load_sidecar()
    data = ensure_habits(data)

    habits = data["habits"]

    while True:
        clear()
        print("HABITS\n")
        for i, h in enumerate(habits):
            print(f"  {'[x]' if h['done'] else '[ ]'} {i+1}. {h['name']}")
        print(f"\n  Toggle (1-{len(habits)}) or b to go back\n")

        choice = input("> ").strip().lower()
        if choice == "b" or choice == "":
            break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(habits):
                habits[idx]["done"] = not habits[idx]["done"]
                data["habits"] = habits
                save_daily(data)
        except ValueError:
            pass


def cmd_think():
    """Zen thinking session — 10 minutes of focused expansion."""
    clear()

    # Load today's thinking log
    thinking_dir = Z / "Thinking"
    thinking_dir.mkdir(parents=True, exist_ok=True)
    thinking_json = thinking_dir / f"{date.today().isoformat()}.json"

    if thinking_json.exists():
        with open(thinking_json) as f:
            thinking_log = json.load(f)
    else:
        thinking_log = {"date": date.today().isoformat(), "sessions": []}

    used_today = {s["prompt_id"] for s in thinking_log.get("sessions", [])}
    unused = [p for p in PROMPTS if p["id"] not in used_today]
    if not unused:
        unused = PROMPTS

    # Choose prompt
    print("ZEN THINKING\n")
    print("  s — Suggested prompt")
    print("  l — List all prompts\n")

    choice = input("  → ").strip().lower()

    if choice == "l":
        clear()
        print("ALL PROMPTS\n")
        for i, p in enumerate(PROMPTS, 1):
            used = "x" if p["id"] in used_today else " "
            print(f"  [{used}] {i}. [{p['theme']}] {p['text']}")
        print(f"\n  Enter number:\n")
        num = input("  → ").strip()
        try:
            idx = int(num) - 1
            if 0 <= idx < len(PROMPTS):
                prompt = PROMPTS[idx]
            else:
                prompt = random.choice(unused)
        except ValueError:
            prompt = random.choice(unused)
    else:
        prompt = random.choice(unused)

    # Show prompt and start session
    clear()
    print("=" * 60)
    print(f"\n  THEME: {prompt['theme']}")
    print(f"\n  {prompt['text']}\n")
    print("=" * 60)
    print("\n  [10 minutes to think and expand]")
    print("  [Press ENTER when ready to start]\n")
    input()

    clear()
    print("=" * 60)
    print(f"  THEME: {prompt['theme']}")
    print(f"  {prompt['text']}")
    print("=" * 60)
    print("\n  Timer started. Think freely. Write if you want.\n")
    print("  Type your thoughts below (optional):")
    print("─" * 60)
    print("\n[Type thoughts, press Ctrl+D when done]\n")

    start_time = time.time()
    duration = 600
    lines = []

    try:
        while True:
            elapsed = time.time() - start_time
            if elapsed >= duration:
                break
            try:
                line = input()
                lines.append(line)
            except EOFError:
                break
    except KeyboardInterrupt:
        pass

    freewrite = "\n".join(lines)

    # Distill
    clear()
    print("\n" + "=" * 60)
    print("\n  TIME'S UP")
    print("\n" + "=" * 60)
    print("\n  Distill your thinking into the essential insight.\n")

    if freewrite:
        print("  Your expansion:")
        print("  " + "-" * 58)
        for line in freewrite.split("\n")[:10]:
            print(f"  {line}")
        if len(freewrite.split("\n")) > 10:
            print("  ...")
        print("  " + "-" * 58 + "\n")

    print("  Core insight (1-3 sentences):\n")

    insight_lines = []
    print("  → ", end="", flush=True)
    try:
        while True:
            line = input()
            if not line:
                break
            insight_lines.append(line)
            if len(insight_lines) < 3:
                print("  → ", end="", flush=True)
            else:
                break
    except (EOFError, KeyboardInterrupt):
        pass

    insight = "\n".join(insight_lines).strip()

    if not insight:
        print("\n  Session cancelled (no insight captured)\n")
        input("  Press Enter to continue...")
        return

    # Save session
    session = {
        "timestamp": datetime.now().isoformat(),
        "prompt_id": prompt["id"],
        "prompt": prompt["text"],
        "theme": prompt["theme"],
        "freewrite": freewrite,
        "insight": insight,
    }
    thinking_log["sessions"].append(session)

    with open(thinking_json, "w") as f:
        json.dump(thinking_log, f, indent=2)

    # Write thinking markdown
    thinking_md = thinking_dir / f"{date.today().isoformat()}.md"
    md = f"---\ndate: {date.today().isoformat()}\nsessions: {len(thinking_log['sessions'])}\n---\n\n"
    md += f"# Thinking Sessions — {date.today().isoformat()}\n\n"

    for i, s in enumerate(thinking_log["sessions"], 1):
        ts = datetime.fromisoformat(s["timestamp"]).strftime("%H:%M")
        md += f"## Session {i} — {ts}\n"
        md += f"**Theme:** {s['theme']}\n\n"
        md += f"**Prompt:** {s['prompt']}\n\n"
        if s.get("freewrite"):
            md += f"### Expansion\n{s['freewrite']}\n\n"
        md += f"### Insight\n{s['insight']}\n\n"
        md += "---\n\n"

    thinking_md.write_text(md)

    print("\n  Session captured.\n")
    input("  Press Enter to continue...")


def cmd_reconcile():
    """Evening reconciliation."""
    clear()
    data = load_sidecar()
    data = ensure_habits(data)

    print("RECONCILIATION\n")

    print("RESULT (1 sentence, concrete):")
    result = input("→ ").strip()
    if not result:
        print("\nNo result captured.\n")
        return

    print("\nWHERE ATTENTION HELD (1 sentence):")
    attention = input("→ ").strip()

    print("\nWHERE IT DRIFTED (optional):")
    drift = input("→ ").strip()

    print("\nTOMORROW LOCK (1 unavoidable action):")
    tomorrow = input("→ ").strip()

    data["result"] = result
    data["attention"] = attention
    data["drift"] = drift or ""
    data["tomorrow"] = tomorrow
    data["reconciled"] = True

    for h in data["habits"]:
        if h["name"] == "Evening reconcile":
            h["done"] = True

    save_daily(data)
    print("\n  Reconciled.\n")
    input("Press Enter to continue...")


def cmd_weekly_review():
    """Guided weekly review."""
    clear()
    today = date.today()
    # Find Monday of this week
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    week_label = f"{monday.isocalendar()[0]}-W{monday.isocalendar()[1]:02d}"

    print(f"WEEKLY REVIEW — {week_label}\n")
    print(f"  {monday.isoformat()} → {sunday.isoformat()}\n")

    # Aggregate week data
    days_reconciled = 0
    total_mits = 0
    mits_done = 0
    total_captures = 0
    drifts = []
    sleep_scores = []
    all_captures = []

    for i in range(7):
        d = monday + timedelta(days=i)
        data = load_sidecar(d)
        if data.get("reconciled"):
            days_reconciled += 1
        m = data.get("mits", [])
        md = data.get("mit_done", [])
        total_mits += len(m)
        mits_done += sum(1 for x in md if x)
        caps = data.get("captures", [])
        total_captures += len(caps)
        for cap in caps:
            all_captures.append({"date": d.isoformat(), **cap})
        if data.get("drift"):
            drifts.append(f"  {d.isoformat()}: {data['drift']}")
        if data.get("energy_sleep") is not None:
            sleep_scores.append(data["energy_sleep"])

    # Show summary
    print("─" * 50)
    print(f"  Days reconciled:  {days_reconciled}/7")
    print(f"  MITs completed:   {mits_done}/{total_mits}")
    print(f"  Captures:         {total_captures}")
    if sleep_scores:
        avg = sum(sleep_scores) / len(sleep_scores)
        print(f"  Avg sleep:        {avg:.1f}/10")
    if drifts:
        print(f"\n  Drift patterns:")
        for d in drifts:
            print(d)
    print("─" * 50 + "\n")

    # Review questions
    print("What worked this week?")
    worked = input("→ ").strip()

    print("\nWhat didn't work?")
    didnt = input("→ ").strip()

    print("\nWhat needs to change?")
    change = input("→ ").strip()

    # Unprocessed captures
    if all_captures:
        print(f"\n  {len(all_captures)} capture(s) this week:")
        for cap in all_captures:
            print(f"    [{cap['date']} {cap.get('time','')}] {cap.get('text','')}")

    # Write weekly review
    weekly_dir = Z / "Weekly"
    weekly_dir.mkdir(parents=True, exist_ok=True)

    md = [
        "---",
        f"week: {week_label}",
        f"start_date: {monday.isoformat()}",
        f"end_date: {sunday.isoformat()}",
        f"days_reconciled: {days_reconciled}",
        f"total_mits: {total_mits}",
        f"mits_done: {mits_done}",
        "---",
        "",
        f"# Weekly Review — {week_label}",
        "",
        "## Week Summary",
        f"- **Days reconciled:** {days_reconciled}/7",
        f"- **MITs completed:** {mits_done}/{total_mits}",
        f"- **Captures:** {total_captures}",
    ]

    if sleep_scores:
        avg = sum(sleep_scores) / len(sleep_scores)
        md.append(f"- **Avg sleep:** {avg:.1f}/10")

    if drifts:
        md += ["", "### Drift Patterns"]
        md += drifts

    md += [
        "",
        "## What worked this week?",
        worked or "",
        "",
        "## What didn't work?",
        didnt or "",
        "",
        "## What needs to change?",
        change or "",
    ]

    if all_captures:
        md += ["", "## Captures"]
        for cap in all_captures:
            md.append(f"- [{cap['date']} {cap.get('time','')}] {cap.get('text','')}")

    md.append("")

    weekly_path = weekly_dir / f"{week_label}.md"
    weekly_path.write_text("\n".join(md))

    # Also save JSON sidecar
    weekly_json = weekly_dir / f"{week_label}.json"
    with open(weekly_json, "w") as f:
        json.dump({
            "week": week_label,
            "start_date": monday.isoformat(),
            "end_date": sunday.isoformat(),
            "days_reconciled": days_reconciled,
            "total_mits": total_mits,
            "mits_done": mits_done,
            "total_captures": total_captures,
            "worked": worked,
            "didnt_work": didnt,
            "change": change,
        }, f, indent=2)

    print(f"\n  Weekly review saved to {week_label}.md\n")
    input("Press Enter to continue...")


def cmd_view_today():
    """View full daily note."""
    clear()
    data = load_sidecar()
    data = ensure_habits(data)

    mits = data.get("mits", [])
    mit_done = data.get("mit_done", [])
    captures = data.get("captures", [])
    habits = data.get("habits", [])

    print(f"TODAY — {date.today().isoformat()}\n")

    # MITs
    if mits:
        print("  MITs:")
        for i, mit in enumerate(mits):
            done = mit_done[i] if i < len(mit_done) else False
            print(f"    {'[x]' if done else '[ ]'} {i+1}. {mit}")
        print()

    # Captures
    if captures:
        print(f"  Captures ({len(captures)}):")
        for cap in captures:
            print(f"    [{cap.get('time','')}] {cap.get('text','')}")
        print()

    # Energy
    if data.get("energy_sleep") is not None:
        print(f"  Energy:")
        print(f"    Sleep: {data['energy_sleep']}/10")
        if data.get("energy_movement"):
            print(f"    Movement: {data['energy_movement']}")
        if data.get("energy_fuel"):
            print(f"    Fuel: {data['energy_fuel']}")
        print()

    # Habits
    if habits:
        print("  Habits:")
        for h in habits:
            print(f"    {'[x]' if h['done'] else '[ ]'} {h['name']}")
        print()

    # Reconciliation
    if data.get("reconciled"):
        print("  Reconcile:")
        print(f"    RESULT: {data.get('result', '')}")
        print(f"    ATTENTION: {data.get('attention', '')}")
        if data.get("drift"):
            print(f"    DRIFT: {data['drift']}")
        print(f"    TOMORROW LOCK: {data.get('tomorrow', '')}")
        print()
    else:
        print("  Not yet reconciled.\n")

    input("Press Enter to continue...")


def cmd_view_past():
    """Show past 7 days."""
    clear()
    print("PAST 7 DAYS\n")

    for i in range(7):
        d = date.today() - timedelta(days=i)
        data = load_sidecar(d)

        has_data = data.get("reconciled") or data.get("mits") or data.get("captures")
        if not has_data:
            continue

        mits = data.get("mits", [])
        mit_done = data.get("mit_done", [])
        mit_done_count = sum(1 for x in mit_done if x)

        print(f"  {d.isoformat()}", end="")

        parts = []
        if mits:
            parts.append(f"MITs {mit_done_count}/{len(mits)}")
        if data.get("captures"):
            parts.append(f"{len(data['captures'])} captures")
        if data.get("energy_sleep") is not None:
            parts.append(f"sleep {data['energy_sleep']}/10")

        if parts:
            print(f"  ({', '.join(parts)})")
        else:
            print()

        if data.get("result"):
            print(f"    Result: {data['result'][:60]}{'...' if len(data.get('result','')) > 60 else ''}")
        if data.get("tomorrow"):
            print(f"    Lock: {data['tomorrow'][:60]}{'...' if len(data.get('tomorrow','')) > 60 else ''}")
        if data.get("drift"):
            print(f"    Drift: {data['drift'][:60]}{'...' if len(data.get('drift','')) > 60 else ''}")
        print()

    input("Press Enter to continue...")


def cmd_systems():
    """View/edit system reference docs."""
    clear()
    systems_dir = Z / "Systems"

    docs = [
        ("1", "Alignment.md"),
        ("2", "Default Day.md"),
        ("3", "Minimum Viable Day.md"),
        ("4", "If-Then Plans.md"),
        ("5", "Habit Stacks.md"),
    ]

    print("SYSTEMS\n")
    for num, name in docs:
        print(f"  {num} — {name.replace('.md', '')}")
    print(f"\n  b — Back\n")

    choice = input("> ").strip()
    if choice == "b" or choice == "":
        return

    for num, name in docs:
        if choice == num:
            p = systems_dir / name
            if p.exists():
                clear()
                print(p.read_text())
                print("\n" + "─" * 60 + "\n")
                print("  e — Edit in $EDITOR")
                print("  b — Back\n")
                action = input("> ").strip().lower()
                if action == "e":
                    import os
                    editor = os.environ.get("EDITOR", "vim")
                    os.system(f'{editor} "{p}"')
            else:
                print(f"\n  File not found: {p}\n")
            input("Press Enter to continue...")
            return


def cmd_reset():
    """Reset today's note."""
    clear()
    print("RESET\n")
    print("Delete today's log and start clean?\n")
    confirm = input("Type 'yes' to confirm: ").strip()

    if confirm.lower() == "yes":
        dp = daily_path()
        sp = sidecar_path()
        if dp.exists():
            dp.unlink()
        if sp.exists():
            sp.unlink()
        print("\n  Reset complete.\n")
    else:
        print("\n  Cancelled.\n")

    input("Press Enter to continue...")


def cmd_info():
    """Show info screen."""
    clear()
    print("75z — PRODUCTIVITY OS\n")
    print("Commands:")
    print("  a  — Alignment (morning read)")
    print("  m  — MITs (set 3 most important tasks)")
    print("  c  — Capture (quick inbox)")
    print("  e  — Energy (log sleep/movement/fuel)")
    print("  h  — Habits (check off today's habits)")
    print("  t  — Think (10-min zen session)")
    print("  4  — Reconcile (evening ritual)")
    print("  w  — Weekly review")
    print("  v  — View today")
    print("  p  — Past 7 days")
    print("  s  — Systems (view/edit reference docs)")
    print("  r  — Reset today")
    print("  i  — Info")
    print("  q  — Quit\n")
    print(f"Vault: {VAULT}\n")
    input("Press Enter to continue...")


# ─── Main ─────────────────────────────────────────────────────────────────────


def status_line():
    """Build the status line for the main menu."""
    data = load_sidecar()
    data = ensure_habits(data)

    mits = data.get("mits", [])
    mit_done = data.get("mit_done", [])
    mit_done_count = sum(1 for x in mit_done if x)
    captures = data.get("captures", [])
    sleep = data.get("energy_sleep")
    movement = data.get("energy_movement")
    fuel = data.get("energy_fuel")
    reconciled = data.get("reconciled", False)

    parts = [f"MITs: {mit_done_count}/{len(mits)}"]

    if captures:
        parts.append(f"Captures: {len(captures)}")

    e_parts = []
    e_parts.append(str(sleep) if sleep is not None else "\u00b7")
    e_parts.append("y" if movement else "\u00b7")
    e_parts.append("y" if fuel else "\u00b7")
    parts.append(f"Energy: {'/'.join(e_parts)}")

    if reconciled:
        parts.append("Reconciled")
    else:
        parts.append("Not reconciled")

    return "  |  ".join(parts)


def main():
    ensure_dirs()

    while True:
        clear()

        print("75z\n")
        print(f"Today: {date.today().isoformat()}")
        print(status_line())
        print()
        print("Commands: a m c e h t 4 w v p s r i q\n")

        cmd = input("> ").strip().lower()

        if cmd == "q":
            break
        elif cmd == "a":
            cmd_alignment()
        elif cmd == "m":
            cmd_mits()
        elif cmd == "c":
            cmd_capture()
        elif cmd == "e":
            cmd_energy()
        elif cmd == "h":
            cmd_habits()
        elif cmd == "t":
            cmd_think()
        elif cmd == "4":
            cmd_reconcile()
        elif cmd == "w":
            cmd_weekly_review()
        elif cmd == "v":
            cmd_view_today()
        elif cmd == "p":
            cmd_view_past()
        elif cmd == "s":
            cmd_systems()
        elif cmd == "r":
            cmd_reset()
        elif cmd == "i":
            cmd_info()


if __name__ == "__main__":
    main()

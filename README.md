# 75z — Productivity OS

**CLI-first for rituals. Obsidian for viewing.**

---

## Setup

```bash
# Add alias to your shell
source ~/dev/Projects/seventyfive_zen/75z_alias.sh
# Or add to .zshrc:
echo 'alias 75z="python3 ~/dev/Projects/seventyfive_zen/seventyfive_zen.py"' >> ~/.zshrc
```

Open `~/obsidian` as your Obsidian vault.

---

## Commands

```
75z

Today: 2026-02-21
MITs: 0/3  |  Captures: 0  |  Energy: ·/·/·  |  Not reconciled

Commands: a m c e h t 4 w v p s r i q
```

| Key | Command | When |
|-----|---------|------|
| `a` | Alignment | Morning — read identity declaration |
| `m` | MITs | Morning — set 3 most important tasks |
| `c` | Capture | Anytime — quick inbox note |
| `e` | Energy | Evening — log sleep/movement/fuel |
| `h` | Habits | Anytime — toggle daily habits |
| `t` | Think | Anytime — 10-min zen thinking session |
| `4` | Reconcile | Evening — core accountability ritual |
| `w` | Weekly review | Weekly — aggregate + reflect |
| `v` | View today | Anytime — see full daily note |
| `p` | Past 7 days | Anytime — spot patterns |
| `s` | Systems | Anytime — view/edit reference docs |
| `r` | Reset today | Anytime — clear and restart |
| `i` | Info | Help screen |
| `q` | Quit | |

---

## Vault Structure

```
~/obsidian/                       (Obsidian vault root)
├── .obsidian/
├── 75z/
│   ├── Daily/                    (one markdown note per day)
│   ├── Weekly/                   (weekly reviews)
│   ├── Thinking/                 (zen thinking sessions)
│   ├── Inbox/                    (quick captures)
│   └── Systems/                  (reference docs)
│       ├── Alignment.md
│       ├── Default Day.md
│       ├── Minimum Viable Day.md
│       ├── If-Then Plans.md
│       └── Habit Stacks.md
└── Templates/
    ├── 75z Daily.md
    ├── 75z Weekly Review.md
    └── 75z Thinking.md
```

---

## Daily Flow

**Morning:**
1. `75z` → `a` — Read alignment
2. `m` — Set 3 MITs

**During the day:**
- `c` — Capture ideas/tasks
- `m` → `d` — Mark MITs done
- `h` — Check off habits

**Evening:**
1. `e` — Log energy
2. `4` — Reconcile
3. Tomorrow's lock is set

**Weekly:**
- `w` — Review the week, process captures, reflect

---

## Philosophy

State → Attention → Action → Result

You don't get what you want. You get what you no longer internally debate.

Slip, don't skip.

# 75z Minimal

**Ultraminimal daily tracker. No gates. No enforcement. Just clarity.**

---

## Installation

```bash
# Add alias to your shell
echo 'alias 75zm="python3 ~/path/to/seventyfive_zen_minimal.py"' >> ~/.zshrc
source ~/.zshrc
```

---

## Usage

### Morning (Set state)
```bash
75zm
```
Enter:
- State (1-10)
- Focus today (one line)

### Evening (Close loop)
```bash
75zm
```
Enter:
- What I did (concrete)
- What shifted (concrete)
- Tomorrow (one action)

### View
```bash
75zm
```
Shows today if complete.

---

## Files Generated

```
~/75z_logs/YYYY-MM-DD.json  # Raw data
~/75z_logs/YYYY-MM-DD.md    # Human readable
```

### Example Log

```markdown
# 2025-12-12

**State:** 7/10
**Focus:** Complete prototype section

**Did:** Removed AI components, wrote 3 pages
**Shifted:** System is now fully traceable

**Tomorrow:** Review architecture match
```

---

## Daily Alignment

See `ALIGNMENT.md` for the daily prayer/journal entry.

No frameworks. No references. Just return to center.

---

## That's It

- No loops
- No gates  
- No enforcement
- No timers
- No progress bars

Just: State → Focus → Did → Shifted → Tomorrow

**Five fields. One cycle. Done.**
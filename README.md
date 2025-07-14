# 🧘 75 Zen - Minimalist CLI Tracker

A beautifully simple command-line tool for tracking daily discipline and personal growth. One day at a time, no excuses.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.6+-green)
![License](https://img.shields.io/badge/license-MIT-purple)

## ✨ Features

- **Interactive Mode** - Just press numbers to check items (NEW!)
- **Visual Progress** - Beautiful progress bars and live updates
- **Streak Tracking** - Track your current and best streaks
- **Zero Friction** - Minimalist design for daily use
- **Motivational Messages** - Contextual encouragement based on your progress

## 📋 The Daily Seven

1. ⏳ **Time for self** - Dedicate time for personal reflection
2. 🏃 **Exercise 45+ min** - Physical activity for at least 45 minutes
3. 👨‍👩‍👧 **Quality family time** - Meaningful moments with loved ones
4. 📚 **Study (60+ min)** - Learn something new for at least 60 minutes
5. 💼 **Focused work (90+ min)** - Deep work for at least 90 minutes
6. 🚫 **No alcohol** - Stay alcohol-free
7. 🍽️ **Followed diet** - Stick to your nutrition plan

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd seventyfive_zen

# Run the installation script
./install.sh

# Or manually install
chmod +x seventyfive_zen.py
sudo ln -sf $(pwd)/seventyfive_zen.py /usr/local/bin/75z
```

### Usage

#### Interactive Mode (Default)

Simply run `75z` to enter interactive mode:

```bash
75z
```

In interactive mode:
- Press **1-7** to toggle items ✅/⬜
- Press **r** to reset today's checklist
- Press **q** to quit

The interface updates in real-time as you check items:

```
🧘 75 Zen - Daily Discipline Tracker
==================================================
1. ✅ ⏳ Time for self
2. ✅ 🏃 Exercise 45+ min
3. ⬜ 👨‍👩‍👧 Quality family time
4. ✅ 📚 Study (60+ min)
5. ⬜ 💼 Focused work (90+ min)
6. ✅ 🚫 No alcohol
7. ⬜ 🍽️ Followed diet

──────────────────────────────────────────────────
Progress: [████████████████░░░░░░░░░░░░░░░░░░░░░░] 4/7 (57%)
──────────────────────────────────────────────────
🔥 Current Streak: 5 days
🏆 Best Streak: 28 days

💪 3 more to go! You got this!

Controls:
Press [1-7] to toggle items | [r] reset day | [q] quit
> _
```

#### Command Mode

You can also use traditional commands:

```bash
# Show current status (non-interactive)
75z status

# Check specific items
75z check 1    # Mark "Time for self" as completed
75z check 4    # Mark "Study (60+ min)" as completed

# Reset today's checklist
75z reset_day

# Force reset streak (asks for confirmation)
75z force_reset
```

## 📂 Data Storage

Your progress is stored locally in `~/.75zen/`:

```
~/.75zen/
├── 2025-01-08.md    # Daily checklist files
├── 2025-01-09.md    
└── streak.json      # Streak tracking data
```

### Daily File Format

Each day's progress is stored in a simple markdown file:

```markdown
# 75 Zen - Wednesday, January 08, 2025

1. [x] ⏳ Time for self
2. [x] 🏃 Exercise 45+ min
3. [ ] 👨‍👩‍👧 Quality family time
4. [x] 📚 Study (60+ min)
5. [x] 💼 Focused work (90+ min)
6. [x] 🚫 No alcohol
7. [ ] 🍽️ Followed diet
```

### Streak Data

```json
{
  "current": 15,
  "best": 28,
  "last_date": "2025-01-08"
}
```

## 🏆 Streak System

- ✅ **Complete all 7 items** → Streak continues (+1 day)
- ❌ **Miss any item** → Streak resets to 0
- 📅 **Daily tracking** → One day at a time
- 🔥 **Motivation** → Track both current and best streaks

## 🎨 Architecture

The refactored codebase follows clean architecture principles:

```
ZenApp (Main Application)
├── FileManager (File Operations)
├── StreakManager (Streak Logic)
├── UI (User Interface)
├── InputHandler (Keyboard Input)
└── Data Models (ChecklistItem, StreakData)
```

### Key Components

- **FileManager**: Handles all file I/O operations
- **StreakManager**: Manages streak calculations and updates
- **UI**: Renders the interface components
- **InputHandler**: Captures single keypresses for interactive mode
- **ChecklistItem**: Represents a single habit to track
- **StreakData**: Encapsulates streak information

## 🛠️ Customization

### Modifying Checklist Items

Edit the `CHECKLIST_ITEMS` in the script:

```python
CHECKLIST_ITEMS = [
    ("⏳", "Time for self"),
    ("🏃", "Exercise 45+ min"),
    # Add or modify items here
]
```

### Changing Colors

Modify the `Colors` class for different color schemes:

```python
class Colors:
    GREEN = '\033[92m'   # Success color
    YELLOW = '\033[93m'  # Pending color
    RED = '\033[91m'     # Warning color
```

## 💡 Tips for Success

1. **Start your day with 75z** - Make it part of your morning routine
2. **Check items immediately** - Don't wait until end of day
3. **Be honest** - The streak doesn't lie, and neither should you
4. **Focus on consistency** - Progress > Perfection
5. **Celebrate small wins** - Every checked box matters

## 🤝 Contributing

Feel free to fork and adapt this tool to your needs. Some ideas:

- Add custom checklist items
- Integrate with external services
- Create weekly/monthly reports
- Add sound effects or notifications
- Build a web interface

## 📝 License

MIT License - Do whatever you want with this. It's about discipline, not licenses.

## 🙏 Acknowledgments

Inspired by the 75 Hard challenge and the philosophy of daily discipline. Built for those who believe in the compound effect of small, consistent actions.

---

*"The impediment to action advances action. What stands in the way becomes the way."* - Marcus Aurelius

*"We are what we repeatedly do. Excellence, then, is not an act, but a habit."* - Aristotle# seventyfive_zen

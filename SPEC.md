# 75z Knowledge Engine Spec

## Core Philosophy

**Do → See → Understand → Change → Repeat**

This is Naval's iteration loop. 75z forces this cycle daily.

## State Machine

```
INTENTION → ACTION → SURPRISE → INSIGHT → UPDATE → REPEAT
```

## Commands

### Morning: `75z start`
**Purpose:** Set intention, kill procrastination

**Flow:**
1. Shows yesterday's insight (if exists)
2. Shows yesterday's tiny change for today
3. Asks: "What are you building today?" (1 sentence)
4. Saves intention automatically

**Output:**
```
75z – Day 12 (2025-11-23)

Yesterday's insight:
→ "Learned that edge=7-8 produces highest learning"

Today's change:
→ "Start BUILD with 5min planning, not jumping in"

What are you building today?
> [input]
```

---

### During Day: `75z done [LOOP]`
**Purpose:** Capture surprise immediately after action

**Loops:** BUILD, BODY, SYSTEM

**Flow:**
1. Marks loop complete
2. Asks: "Edge/difficulty (1-10)?"
3. Asks: "What surprised you?"
4. Asks: "What changed in your understanding?"
5. Saves automatically

**Example:**
```bash
75z done BUILD
Edge/difficulty (1-10)? > 7
What surprised you? > [input]
What changed in your understanding? > [input]
✓ BUILD logged
```

---

### End of Day: `75z insight`
**Purpose:** Naval's knowledge extraction moment

**Flow:**
Asks 3 questions:
1. "What did you learn today that wasn't obvious before?"
2. "What small change would improve tomorrow's loop?"
3. "What belief or assumption did you update?"

Saves automatically.

---

### Status: `75z` (default)
**Purpose:** See current state

**Shows:**
- Today's intention
- Loops completed: [✓] BUILD [ ] BODY [ ] SYSTEM
- Current edge levels
- Last insight (if any)

---

## Data Model

```python
{
  "date": "2025-11-23",
  "day_number": 12,
  "intention": "Build auth system for CM3070",
  "loops": {
    "BUILD": {
      "completed": true,
      "edge": 7,
      "surprise": "...",
      "understanding_change": "..."
    },
    "BODY": {...},
    "SYSTEM": {...}
  },
  "insight": {
    "learning": "...",
    "tiny_change": "...",
    "belief_update": "..."
  }
}
```

## Log Format (JSON + Markdown)

**Primary:** JSON for programmatic access
**Secondary:** Markdown for human reading

## Insight Forwarding

Next morning, `75z start` shows:
- Yesterday's learning
- Yesterday's tiny change (as today's rule)

This creates the compounding loop.

## Pattern Detection

Track:
- Edge levels over time
- Learning quality vs edge level
- Surprise frequency
- Belief updates

Show patterns:
```
Your last 4 BUILD loops:
Edge: 6 → 7 → 8 → 7
Learning highest at edge=7-8
```

## Identity Reinforcement

Every interaction reinforces:
- "I am someone who learns every day"
- "I am someone who iterates"
- "I am someone who sharpens craft"

Not: "I checked a box"


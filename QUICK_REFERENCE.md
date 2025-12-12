# 75z Enforcement Mode - Quick Reference Card

## The Enforcement Loop

```
Inner state → attention → word → action → result
```

**Not described. Enforced.**

---

## The 4 Gates

### GATE 1: State Coherence
- **When:** Before any loop starts
- **Check:** Rate inner state 1-10
- **Block if:** Score < 5
- **Action:** Reset state (walk/breathe/write/sit)

### GATE 2: Causality Chain
- **When:** During loop completion
- **Check:** Each layer traces to previous
- **Block if:** Vague or unanchored language
- **Action:** Redo with concrete specifics

### GATE 3: Backward Debug
- **When:** Edge score < 5
- **Check:** Trace backward to root cause
- **Block if:** N/A (captures, doesn't block)
- **Action:** Result → Action → Words → Attention → State

### GATE 4: Daily Coherence
- **When:** After first loop
- **Check:** State consistent with actions?
- **Block if:** N/A (warns only)
- **Action:** Reset if incoherent

---

## Commands

| Key | Action | Enforcement |
|-----|--------|-------------|
| `s` | Set intention | Triggers Gate 1 |
| `1-3` | Complete loop | Gates 1, 2, 3, 4 |
| `4` | Add insight | Validates concrete change |
| `c` | Coherence check | Runs Gate 4 manually |
| `v` | View details | - |
| `p` | Past 7 days | - |
| `r` | Reset today | - |
| `q` | Quit | - |

---

## Blocking Rules

**Cannot proceed if:**
- ❌ No intention set
- ❌ State coherence < 5
- ❌ Causality chain incomplete
- ❌ Language is vague/unanchored
- ❌ Cannot trace layer to previous

**Can proceed but warned:**
- ⚠️ Edge < 5 (triggers debug)
- ⚠️ Daily incoherence detected
- ⚠️ Tiny change not concrete

---

## Rejected Language

❌ "Worked on project"
❌ "Made progress"
❌ "Did stuff"
❌ "Tried things"
❌ "Learned stuff"
❌ "Sort of"
❌ "Kind of"

✓ "Implemented JWT auth with passport.js"
✓ "Completed login endpoint, tested 10 requests"
✓ "Wrote 3 middleware functions"
✓ "Discovered JWT needs rotation strategy"

---

## Data Model

### Old (v1):
```json
{
  "loops": {
    "BUILD": {
      "did": "worked on auth",
      "shift": "learned stuff",
      "edge": 7
    }
  }
}
```

### New (v2):
```json
{
  "state_coherence_score": 8,
  "loops": {
    "BUILD": {
      "attention": "Implementing JWT middleware",
      "action": "Wrote passport config, tested with curl",
      "result": "Login endpoint returns valid JWT",
      "edge": 7,
      "debug": null
    }
  }
}
```

---

## Causality Chain Template

```
1. INTENTION (Inner State)
   "What is your goal today?"
   ↓
2. ATTENTION
   "What did you focus on?" (must relate to intention)
   ↓
3. ACTION
   "What specific actions?" (must trace to attention)
   ↓
4. RESULT
   "What concrete result?" (must trace to actions)
   ↓
5. VALIDATE
   "Can you trace each layer to previous?" (y/n)
```

**If any layer breaks: REJECTED, start over.**

---

## Backward Debug Template

Triggered when edge < 5:

```
5. Bad result → What was the outcome?
   ↓
4. Wrong action → What did you actually do?
   ↓
3. Wrong words → What were you telling yourself?
   ↓
2. Wrong attention → Where was your focus?
   ↓
1. ROOT CAUSE → What was the inner state?
```

**Fix the state, the rest follows mechanically.**

---

## Daily Coherence Check

Once per day (10 seconds):

```
Intention: [your intention]
Completed: [BUILD, BODY, SYSTEM]

Question: "Is your inner state consistent with today's actions?"

If NO:
  → Stop
  → Reset state
  → Continue when clear
```

---

## State Reset Options

When coherence < 5 or incoherent:

1. **Walk** (5-10 minutes)
2. **Breathe** (2 minutes, deep)
3. **Write** (3 minutes, on paper)
4. **Sit** (5 minutes, eyes closed)

**Cannot proceed until state is reset.**

---

## Edge Score Guide

| Score | Meaning | Action |
|-------|---------|--------|
| 1-2 | Waste of time, regret | Debug forced |
| 3-4 | Poor, frustrated | Debug forced |
| 5-6 | Okay, some progress | Normal |
| 7-8 | Good, challenging | Normal |
| 9-10 | Excellent, flow state | Normal |

**Edge < 5 = Backward debug forced**

---

## Integration Example

```python
from enforcement_gates import (
    gate_1_state_coherence,
    gate_2_causality_chain,
    gate_3_backward_debug,
    gate_4_daily_coherence,
)

# Before loop
is_coherent, score = gate_1_state_coherence()
if not is_coherent:
    return  # BLOCKED

# During loop
causality = gate_2_causality_chain(loop_name, intention)
if not causality:
    return  # REJECTED

# Store chain
data["attention"] = causality["attention"]
data["action"] = causality["action"]
data["result"] = causality["result"]

# After edge score
if edge < 5:
    data["debug"] = gate_3_backward_debug(loop_name, edge)

# After first loop
gate_4_daily_coherence(intention, completed_loops)
```

---

## Philosophy in 3 Lines

```
Results are downstream of inner state.
Control the state, the rest follows mechanically.
The loop is now a gate, not a description.
```

---

## Files

- `ENFORCEMENT_SPEC.md` - Complete technical specification
- `ENFORCEMENT_GUIDE.md` - Usage guide with examples
- `ENFORCEMENT_FLOW.md` - Visual diagrams
- `enforcement_gates.py` - Implementation code
- `QUICK_REFERENCE.md` - This file

---

## One-Sentence Summary

**Before any action can complete, it must prove an unbroken chain from inner state to result, with vague language rejected and bad results traced to their root cause.**

---

## The Guarantee

Every completed loop has:
- ✓ Coherent inner state (≥5)
- ✓ Traceable attention
- ✓ Concrete actions
- ✓ Measurable results
- ✓ No vague language
- ✓ Root cause if edge < 5
- ✓ Daily coherence checked

**No exceptions. No bypasses. Enforced mechanically.**
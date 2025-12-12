# 75z Enforcement Mode - Implementation Guide

**Transform from description to enforcement.**

The loop is no longer tracked—it's **gated**.

---

## What Changed

### Before (v1): Description Mode
"What did you do today?"
→ Free text, accepted as-is
→ Journal with checkboxes

### After (v2): Enforcement Mode
"Trace it back to your inner state."
→ Forced causality chain
→ Blocks action if state is bad
→ Rejects vague language

---

## The 4 Gates

Every loop now passes through 4 enforcement gates:

```
┌─────────────────────────────────────┐
│ GATE 1: State Coherence Check       │
│ • Rate inner state (1-10)           │
│ • If < 5: BLOCKED                   │
│ • Must reset state to proceed       │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ GATE 2: Causality Chain             │
│ • Intention → Attention             │
│ • Attention → Action                │
│ • Action → Result                   │
│ • Validate: each traces to previous │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ GATE 3: Backward Debug (if edge<5)  │
│ • Result → Action → Words →         │
│   Attention → State                 │
│ • Forces root cause analysis        │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ GATE 4: Daily Coherence Check       │
│ • "State consistent with actions?"  │
│ • Runs once per day                 │
│ • 10 second check                   │
└─────────────────────────────────────┘
```

---

## Installation

### Option 1: Use the enforcement gates module

The enforcement logic is in `enforcement_gates.py` and can be integrated into the existing system:

```python
from enforcement_gates import (
    gate_1_state_coherence,
    gate_2_causality_chain,
    gate_3_backward_debug,
    gate_4_daily_coherence,
)

# Before any loop starts
is_coherent, score = gate_1_state_coherence()
if not is_coherent:
    return  # Block action

# During loop completion
causality = gate_2_causality_chain(loop_name, intention)
if not causality:
    return  # Chain broken, reject

# After edge score
if edge < 5:
    debug_data = gate_3_backward_debug(loop_name, edge)
    
# After first loop
gate_4_daily_coherence(intention, completed_loops)
```

### Option 2: Full v2 implementation

See `ENFORCEMENT_SPEC.md` for complete specification.

---

## Usage Examples

### Example 1: High Coherence Flow

```
$ 75z

75z v2 ENFORCEMENT MODE – Day 42 (2025-01-15)
Inner state → attention → word → action → result

Press 's' to set intention...

> s

What is your intention today? (inner state)
> Build authentication system for CM3070

═══ GATE 1: STATE COHERENCE CHECK ═══

Rate your inner state clarity (1-10): 8

✓ GATE PASSED (coherence: 8/10)

Intention saved.

Press '1' to complete BUILD...

> 1

═══ BUILD LOOP ═══

═══ GATE 2: CAUSALITY CHAIN ═══

► LAYER 1: INNER STATE (Intention)
  "Build authentication system for CM3070"

What did you focus on? (must relate to intention)
> Implementing JWT middleware with passport.js

► LAYER 2: ATTENTION
  "Implementing JWT middleware with passport.js"

What specific actions did you take? (must trace to focus)
> Wrote passport config, created JWT strategy, tested login with curl

► LAYER 3: ACTION
  "Wrote passport config, created JWT strategy, tested login with curl"

What concrete result emerged? (must trace to actions)
> Login endpoint returns valid JWT token, verified with 10 test requests

─────────────────────────────────────────────────
TRACEABILITY CHECK
─────────────────────────────────────────────────

  Intention → Attention → Action → Result

Can you trace each layer to the previous? (y/n) [y]: y

✓ GATE PASSED - Chain is anchored

Edge/difficulty (1-10): 7

✓ BUILD completed
```

---

### Example 2: Low Coherence (BLOCKED)

```
> s

What is your intention today?
> Finish the project

═══ GATE 1: STATE COHERENCE CHECK ═══

Rate your inner state clarity (1-10): 3

─────────────────────────────────────────────────
⚠  GATE LOCKED ⚠
─────────────────────────────────────────────────

Coherence: 3/10 (minimum: 5)

Reset state first:
  • Walk (5-10 min)
  • Breathe deeply (2 min)
  • Write state on paper (3 min)
  • Close eyes, sit still (5 min)

Press Enter when ready...
```

---

### Example 3: Broken Causality Chain (REJECTED)

```
═══ GATE 2: CAUSALITY CHAIN ═══

► INTENTION: "Build authentication system"

What did you focus on?
> Working on the project

► ATTENTION: "Working on the project"

What specific actions did you take?
> Made some progress

✗ Vague language detected: "made progress"
Be specific. What exactly did you do?

Chain broken. Try again with concrete details.
```

---

### Example 4: Low Edge Score (DEBUG FORCED)

```
Edge/difficulty (1-10): 3

═══ GATE 3: BACKWARD DEBUG ═══

Edge score 3/10 triggered debugging

Debug direction: Result → Action → Words → Attention → State

5. BAD RESULT
What was the outcome?
> Auth still broken after 2 hours

4. WRONG ACTION
What did you actually do?
> Changed code randomly, tried different things

3. WRONG WORDS/THOUGHTS
What were you telling yourself?
> "Just need to keep trying different approaches"

2. WRONG ATTENTION
Where was your focus?
> On fixing the symptom, not understanding the system

1. ROOT CAUSE (INNER STATE)
What was happening internally?
> Frustrated, avoiding deep thinking, wanted quick fix

─────────────────────────────────────────────────
ROOT CAUSE IDENTIFIED
─────────────────────────────────────────────────

Inner state: Frustrated, avoiding deep thinking, wanted quick fix

Fix the state, the rest follows mechanically.
```

---

## Data Structure Changes

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

## Rejected Language Examples

❌ "Worked on the project"
✓ "Implemented JWT authentication using passport.js"

❌ "Made progress"
✓ "Completed login endpoint, tested with 10 requests"

❌ "Did some coding"
✓ "Wrote 3 middleware functions: auth, validate, error handling"

❌ "Learned stuff"
✓ "Discovered JWT refresh tokens need rotation strategy"

❌ "Tried things"
✓ "Tested 5 different approaches: Basic Auth, JWT, OAuth, Session, Cookie"

---

## When Gates Trigger

| Situation | Gate | Action |
|-----------|------|--------|
| Set intention | Gate 1 | Check state coherence |
| Start any loop | Gate 1 | Block if score < 5 |
| Complete loop | Gate 2 | Enforce causality chain |
| Edge < 5 | Gate 3 | Force backward debug |
| First loop done | Gate 4 | Daily coherence check |

---

## Philosophy Shift

### v1 Philosophy:
"Let's see what you did today."
→ Trust user to self-reflect
→ Accept any input
→ Hope patterns emerge

### v2 Philosophy:
"Prove the chain is unbroken."
→ Enforce mechanical causality
→ Reject vague language
→ Force root cause analysis

**Core principle:**
```
Results are downstream of inner state.
Control the state, the rest follows mechanically.
```

---

## Integration Steps

To add enforcement to existing 75z:

1. **Import the gates module:**
   ```python
   from enforcement_gates import (
       gate_1_state_coherence,
       gate_2_causality_chain,
       gate_3_backward_debug,
       gate_4_daily_coherence,
   )
   ```

2. **Add state check before loops:**
   ```python
   if not data.get("state_coherence_checked"):
       is_coherent, score = gate_1_state_coherence()
       if not is_coherent:
           continue  # Block
       data["state_coherence_score"] = score
   ```

3. **Replace loop capture with causality chain:**
   ```python
   # OLD: did = prompt_input("What did you do?")
   # NEW:
   causality = gate_2_causality_chain(loop_name, intention)
   if not causality:
       continue  # Chain broken
   data["loops"][name]["attention"] = causality["attention"]
   data["loops"][name]["action"] = causality["action"]
   data["loops"][name]["result"] = causality["result"]
   ```

4. **Add backward debug for low edge:**
   ```python
   if edge < 5:
       debug = gate_3_backward_debug(loop_name, edge)
       data["loops"][name]["debug"] = debug
   ```

5. **Add daily coherence check:**
   ```python
   if not data.get("daily_coherence_checked"):
       completed = [name for name in loops if loops[name].get("completed")]
       if gate_4_daily_coherence(intention, completed):
           data["daily_coherence_checked"] = True
   ```

---

## Benefits

**Before enforcement:**
- Vague entries pile up
- No root cause analysis
- Bad state → bad action → more noise
- Patterns hard to detect

**After enforcement:**
- Every entry is concrete and traceable
- Low performance triggers automatic debugging
- Bad state is caught before action
- Causality chains reveal true patterns

---

## Testing

Test the enforcement gates:

```bash
cd seventyfive_zen
python3 -c "
from enforcement_gates import gate_1_state_coherence
is_coherent, score = gate_1_state_coherence()
print(f'Coherent: {is_coherent}, Score: {score}')
"
```

---

## Next Steps

1. **Read** `ENFORCEMENT_SPEC.md` for full technical spec
2. **Review** `enforcement_gates.py` for implementation
3. **Test** gates module standalone
4. **Integrate** into main 75z system
5. **Use** for 7 days to validate enforcement friction
6. **Iterate** based on real usage

---

## Final Note

**The loop is now a gate, not a description.**

Every entry either passes all gates or is rejected.

No vague language.
No unanchored words.
No action from bad state.
No surface fixes without root cause.

The system now enforces what v1 only suggested.

Control the state.
The rest follows mechanically.
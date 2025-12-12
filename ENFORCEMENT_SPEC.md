# 75z ENFORCEMENT MODE SPECIFICATION

**Version 2: The loop is enforced, not described.**

## Core Principle

```
Inner state → attention → word → action → result
```

This is not a description. This is a **causal chain** that must be verified at runtime.

---

## The 4 Enforcement Gates

### GATE 1: State Coherence Check

**Rule:** Inner state must be clear before action is allowed.

**Implementation:**
```
Before any loop starts:
1. Rate inner state clarity (1-10)
2. If score < 5: BLOCK action
3. Show reset options (walk, breathe, write, sit)
4. Only proceed when state ≥ 5
```

**Why:**
Action taken from noise compounds noise.

**Code Location:**
- Check at: Start of each loop completion
- Store: `data["state_coherence_score"]`
- Block threshold: `STATE_COHERENCE_THRESHOLD = 5`

---

### GATE 2: Explicit Causality Constraints

**Rule:** Each layer must trace to the previous layer.

**Implementation:**
```
For each completed loop, enforce the chain:

1. INTENTION (inner state)
   ↓
2. ATTENTION: "What did you focus on?"
   Must relate to intention. Cannot proceed without answer.
   ↓
3. ACTION: "What specific actions did you take?"
   Must trace to attention. Cannot proceed without answer.
   ↓
4. RESULT: "What concrete result emerged?"
   Must trace to actions. Cannot proceed without answer.
   ↓
5. VALIDATION: "Can you trace each layer to the previous?"
   If no → reject entire chain, force restart
```

**Why:**
Prevents skipping layers (the most common failure mode).

**Data Structure:**
```json
{
  "loops": {
    "BUILD": {
      "attention": "Implementing auth middleware",
      "action": "Wrote passport.js config, tested with curl",
      "result": "Login endpoint returns JWT token",
      "edge": 7,
      "completed": true
    }
  }
}
```

**Ban Unanchored Language:**
- Any vague statement → rejected
- "Worked on stuff" → rejected
- "Made progress" → rejected
- Must be concrete and traceable

---

### GATE 3: Backward Debugging

**Rule:** When results are bad (edge < 5), debug backward only.

**Implementation:**
```
If edge score < 5, trigger forced backward trace:

5. Bad result → "What was the outcome?"
4. Wrong action → "What did you actually do?"
3. Wrong words → "What were you telling yourself?"
2. Wrong attention → "Where was your focus?"
1. Root cause → "What was the inner state?"

Store in: data["loops"][name]["debug"]
```

**Why:**
Fixes root cause, not surface behavior.

**Principle:**
```
Don't debug code.
Debug the state that wrote the code.
```

---

### GATE 4: Daily Coherence Check

**Rule:** Once per day, check if inner state matches actions.

**Implementation:**
```
After first loop completion:
1. Show intention
2. Show completed loops
3. Ask: "Is your inner state consistent with today's actions?"
4. If no → STOP, reset state, continue when clear
```

**Timing:** 10 seconds max

**Why:**
Coherence beats effort. Catch drift early.

**Frequency:** Once per day (flag: `daily_coherence_checked`)

---

## Modified Data Model

### Day Structure
```json
{
  "date": "2025-01-15",
  "day_number": 42,
  "intention": "Build authentication system",
  
  "state_coherence_score": 7,
  "state_coherence_checked": true,
  "daily_coherence_checked": true,
  
  "loops": {
    "BUILD": {
      "attention": "Auth middleware implementation",
      "action": "Wrote passport config, added JWT",
      "result": "Login endpoint working with tokens",
      "edge": 7,
      "completed": true,
      "debug": null
    },
    "BODY": {
      "attention": "Upper body strength",
      "action": "100 pushups, 50 dips, 10min walk",
      "result": "Chest and triceps fatigued, good form",
      "edge": 8,
      "completed": true
    },
    "SYSTEM": {
      "attention": "Simplify deploy process",
      "action": "Deleted 3 unused scripts, merged 2 configs",
      "result": "Deploy is now 1 command instead of 5",
      "edge": 6,
      "completed": true
    }
  },
  
  "insight": {
    "learning": "JWT refresh tokens need rotation strategy",
    "tiny_change": "Start each BUILD session with 5min architecture sketch"
  }
}
```

### Low Edge Example (Backward Debug Triggered)
```json
{
  "loops": {
    "BUILD": {
      "attention": "Trying to fix bug",
      "action": "Random changes to auth code",
      "result": "Still broken, wasted 2 hours",
      "edge": 3,
      "completed": true,
      "debug": {
        "bad_result": "Auth still failing after 2 hours",
        "wrong_action": "Changed code without understanding",
        "wrong_words": "Just need to try more things",
        "wrong_attention": "On fixing symptoms, not understanding",
        "root_cause_state": "Frustrated, avoiding deep thinking"
      }
    }
  }
}
```

---

## Enforcement Rules Summary

### Blocking Rules (Cannot Proceed)

1. **No intention set** → Cannot start any loop
2. **State coherence < 5** → Cannot start any loop
3. **Causality chain incomplete** → Loop rejected, must restart
4. **Unanchored language** → Rejected, must be specific
5. **Daily coherence fails** → Warned, encouraged to reset

### Non-Blocking Rules (Capture Only)

1. **Edge < 5** → Triggers backward debug (completes normally)
2. **Insight without concrete change** → Prompted to revise
3. **Multiple sessions per loop** → Allowed, stores history

---

## UI Changes

### Before (Description Mode)
```
What did you do?
> "worked on project"

What surprised you?
> "it was hard"

✓ BUILD logged
```

### After (Enforcement Mode)
```
═══ GATE 1: STATE COHERENCE ═══
Rate your inner state clarity (1-10): 6
✓ GATE PASSED (coherence: 6/10)

═══ GATE 2: CAUSALITY CHAIN ═══

► INTENTION (Inner State):
  "Build authentication system"

What did you focus on? (must relate to intention)
> "Implementing JWT middleware"

► ATTENTION:
  "Implementing JWT middleware"

What specific actions did you take? (must trace to focus)
> "Wrote passport.js config, tested with curl, added error handling"

► ACTION:
  "Wrote passport.js config, tested with curl, added error handling"

What concrete result emerged? (must trace to actions)
> "Login endpoint returns valid JWT, verified with 10 test requests"

Traceability Check:
  Intention → Attention → Action → Result
Can you trace each layer to the previous? (y/n) [y]: y

✓ GATE PASSED (chain is anchored)

Edge/difficulty (1-10): 7

✓ BUILD completed
```

---

## Modified Commands

### Interactive Commands

- `s` - Set intention (REQUIRED, triggers GATE 1)
- `1-3` - Complete loop (enforces GATE 1, 2, 3, 4)
- `4` - Add insight (enforces concreteness)
- `c` - Manual coherence check (run GATE 4 anytime)
- `v` - View details
- `p` - Past 7 days
- `r` - Reset today
- `q` - Quit

### What Gets Enforced

Every loop completion runs:
1. State coherence check (once per day)
2. Causality chain validation (every loop)
3. Backward debug if edge < 5 (when triggered)
4. Daily coherence check (after first loop)

---

## Markdown Log Format

### Before
```markdown
# 75z – Day 42 (2025-01-15)

**Intention:** Build authentication

## ✓ BUILD

- Did: worked on auth
- Shift: learned some stuff
- Edge: 7/10
```

### After
```markdown
# 75z – Day 42 (2025-01-15)

**Intention:** Build authentication system
**State Coherence:** 7/10

## [✓] BUILD

**Causality Chain:**
- Attention: Implementing JWT middleware
- Action: Wrote passport.js config, tested with curl, added error handling
- Result: Login endpoint returns valid JWT, verified with 10 test requests
- Edge: 7/10

## [✓] BODY

**Causality Chain:**
- Attention: Upper body strength development
- Action: 100 pushups (5 sets), 50 dips (3 sets), 10min walk
- Result: Chest and triceps fully fatigued, maintained good form throughout
- Edge: 8/10

---
**Daily Coherence Check:** Passed ✓
```

---

## Implementation Priority

### Phase 1: Core Gates (MVP)
1. ✓ Gate 1: State coherence check
2. ✓ Gate 2: Causality chain enforcement
3. ✓ Gate 3: Backward debugging
4. ✓ Gate 4: Daily coherence check

### Phase 2: Enhanced Tracking
1. Pattern detection (edge trends)
2. Coherence scoring over time
3. Debug frequency analysis
4. Attention → result correlation

### Phase 3: Advanced Features
1. Multi-session support per loop
2. Timer integration with gates
3. Voice notes for causality chain
4. Weekly coherence reports

---

## Key Differences from v1

| Aspect | v1 (Description) | v2 (Enforcement) |
|--------|------------------|------------------|
| Inner state | Optional text | Mandatory + scored |
| Loop capture | Free text | Forced causality chain |
| Low performance | Logged, no action | Backward debug forced |
| Language | Vague accepted | Vague rejected |
| Coherence | Not checked | Checked daily |
| Progression | Always allowed | Blocked if state bad |

---

## Philosophy

**v1 said:** "Track what you did"
**v2 says:** "Prove the chain is unbroken"

**v1 assumed:** Users will self-reflect
**v2 enforces:** System forces reflection

**v1 output:** Journal entries
**v2 output:** Causal traces

---

## Final Compression

```
Results are downstream of inner state.
Control the state, the rest follows mechanically.

The system now enforces this mechanically:
- Bad state → blocked action
- Vague language → rejected
- Broken chain → exposed
- Poor result → root cause required

Not: "What did you do?"
But: "Trace it back to your inner state."
```

---

## Next Steps

To implement:
1. Copy `seventyfive_zen.py` → `seventyfive_zen_v2.py`
2. Add 4 gate functions
3. Modify `display_interactive()` to call gates
4. Update data model to store causality chains
5. Modify markdown output to show chains
6. Test with real usage for 7 days
7. Iterate based on enforcement friction

The loop is now a **gate**, not a description.
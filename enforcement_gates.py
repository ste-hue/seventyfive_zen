#!/usr/bin/env python3
"""
75z Enforcement Gates Module

The loop is enforced, not described.
Inner state → attention → word → action → result
"""

import time
from typing import Any, Dict, Optional


# ANSI Colors
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    ENDC = "\033[0m"


# ENFORCEMENT THRESHOLDS
STATE_COHERENCE_THRESHOLD = 5  # Below this = conflicted state, block action
BACKWARD_DEBUG_THRESHOLD = 5  # Below this = force root cause analysis


def prompt_input(prompt: str, default: str = "") -> str:
    """Get user input with prompt"""
    try:
        if default:
            print(f"{prompt} [{default}]: ", end="", flush=True)
            value = input().strip()
            return value if value else default
        else:
            print(f"{prompt}: ", end="", flush=True)
            return input().strip()
    except (EOFError, KeyboardInterrupt):
        print("\n")
        return ""


def gate_1_state_coherence() -> tuple[bool, int]:
    """
    GATE 1: State Coherence Check

    Rule: Inner state must be clear before action is allowed.

    Why: Action taken from noise compounds noise.

    Returns: (is_coherent, coherence_score)
    """
    print(f"\n{Colors.BOLD}{'═' * 50}{Colors.ENDC}")
    print(f"{Colors.BOLD}GATE 1: STATE COHERENCE CHECK{Colors.ENDC}")
    print(f"{Colors.BOLD}{'═' * 50}{Colors.ENDC}\n")

    print(f"{Colors.YELLOW}Action from noise compounds noise.{Colors.ENDC}")
    print(
        f"{Colors.YELLOW}Control the state, the rest follows mechanically.{Colors.ENDC}\n"
    )

    print("Rate your inner state clarity (1-10):")
    print("  1-4 = Conflicted, scattered, reactive")
    print("  5-7 = Mostly clear, some noise")
    print("  8-10 = Coherent, calm, intentional\n")

    coherence_input = prompt_input("State clarity")

    # Debug: strip whitespace and check what we got
    coherence_input = coherence_input.strip()

    if not coherence_input:
        print(f"\n{Colors.RED}No input received. Please enter a number.{Colors.ENDC}")
        return False, 0

    try:
        coherence = int(coherence_input)
        if coherence < 1 or coherence > 10:
            print(f"\n{Colors.RED}Invalid score. Must be 1-10.{Colors.ENDC}")
            return False, 0

        is_coherent = coherence >= STATE_COHERENCE_THRESHOLD

        if not is_coherent:
            print(f"\n{Colors.RED}{'─' * 50}{Colors.ENDC}")
            print(f"{Colors.RED}⚠  GATE LOCKED ⚠{Colors.ENDC}")
            print(f"{Colors.RED}{'─' * 50}{Colors.ENDC}")
            print(f"\nCoherence: {coherence}/10 (minimum: {STATE_COHERENCE_THRESHOLD})")
            print(f"\n{Colors.YELLOW}Reset state first:{Colors.ENDC}")
            print("  • Walk (5-10 min)")
            print("  • Breathe deeply (2 min)")
            print("  • Write state on paper (3 min)")
            print("  • Close eyes, sit still (5 min)")
            print("\nPress Enter when ready...")
            input()
            return False, coherence

        print(f"\n{Colors.GREEN}{'─' * 50}{Colors.ENDC}")
        print(f"{Colors.GREEN}✓ GATE PASSED{Colors.ENDC} (coherence: {coherence}/10)")
        print(f"{Colors.GREEN}{'─' * 50}{Colors.ENDC}\n")
        time.sleep(1)
        return True, coherence

    except ValueError:
        print(f"\n{Colors.RED}Invalid input. Must be a number 1-10.{Colors.ENDC}")
        return False, 0


def gate_2_causality_chain(loop_name: str, intention: str) -> Optional[Dict[str, str]]:
    """
    GATE 2: Explicit Causality Constraints

    Rule: Each layer must trace to the previous one.

    Chain: Inner state → Attention → Action → Result

    Why: Prevents skipping layers (the most common failure).

    Returns: Dict with attention/action/result or None if chain breaks
    """
    print(f"\n{Colors.BOLD}{'═' * 50}{Colors.ENDC}")
    print(f"{Colors.BOLD}GATE 2: CAUSALITY CHAIN{Colors.ENDC}")
    print(f"{Colors.BOLD}{'═' * 50}{Colors.ENDC}\n")

    print(f"{Colors.YELLOW}Each layer must reference the previous one.{Colors.ENDC}")
    print(f"{Colors.YELLOW}Unanchored language will be rejected.{Colors.ENDC}\n")

    # Layer 1: Attention (from inner state/intention)
    print(f"{Colors.BLUE}► LAYER 1: INNER STATE (Intention){Colors.ENDC}")
    print(f'  "{intention}"\n')

    attention = prompt_input("What did you focus on? (must relate to intention)")

    if not attention:
        print(f"\n{Colors.RED}✗ Chain broken at attention layer{Colors.ENDC}")
        return None

    # Layer 2: Action (from attention)
    print(f"\n{Colors.BLUE}► LAYER 2: ATTENTION{Colors.ENDC}")
    print(f'  "{attention}"\n')

    action = prompt_input("What specific actions did you take? (must trace to focus)")

    if not action:
        print(f"\n{Colors.RED}✗ Chain broken at action layer{Colors.ENDC}")
        return None

    # Layer 3: Result (from action)
    print(f"\n{Colors.BLUE}► LAYER 3: ACTION{Colors.ENDC}")
    print(f'  "{action}"\n')

    result = prompt_input("What concrete result emerged? (must trace to actions)")

    if not result:
        print(f"\n{Colors.RED}✗ Chain broken at result layer{Colors.ENDC}")
        return None

    # Validate traceability
    print(f"\n{Colors.YELLOW}{'─' * 50}{Colors.ENDC}")
    print(f"{Colors.YELLOW}TRACEABILITY CHECK{Colors.ENDC}")
    print(f"{Colors.YELLOW}{'─' * 50}{Colors.ENDC}")
    print(f"\n  Intention → Attention → Action → Result\n")

    is_traceable = prompt_input("Can you trace each layer to the previous? (y/n)", "y")

    if is_traceable.lower() != "y":
        print(f"\n{Colors.RED}{'─' * 50}{Colors.ENDC}")
        print(f"{Colors.RED}✗ GATE FAILED - Unanchored language{Colors.ENDC}")
        print(f"{Colors.RED}{'─' * 50}{Colors.ENDC}")
        print("\nWords must be concretely traceable to state and action.")
        print("Try again with specific details.\n")
        time.sleep(2)
        return None

    print(f"\n{Colors.GREEN}{'─' * 50}{Colors.ENDC}")
    print(f"{Colors.GREEN}✓ GATE PASSED - Chain is anchored{Colors.ENDC}")
    print(f"{Colors.GREEN}{'─' * 50}{Colors.ENDC}\n")
    time.sleep(1)

    return {"attention": attention, "action": action, "result": result}


def gate_3_backward_debug(loop_name: str, edge: int) -> Dict[str, str]:
    """
    GATE 3: Inverted Debugging

    Rule: When results are bad (edge < threshold), debug backward only.

    Direction: Result → Action → Words → Attention → State

    Why: Fixes root cause, not surface behavior.

    Returns: Dict with debug trace
    """
    print(f"\n{Colors.BOLD}{'═' * 50}{Colors.ENDC}")
    print(f"{Colors.BOLD}GATE 3: BACKWARD DEBUG{Colors.ENDC}")
    print(f"{Colors.BOLD}{'═' * 50}{Colors.ENDC}\n")

    print(f"{Colors.RED}Edge score {edge}/10 triggered debugging{Colors.ENDC}")
    print(f"(threshold: {BACKWARD_DEBUG_THRESHOLD})")
    print(
        f"\n{Colors.YELLOW}Debug direction: Result → Action → Words → Attention → State{Colors.ENDC}\n"
    )

    print(f"{Colors.BOLD}5. BAD RESULT{Colors.ENDC}")
    bad_result = prompt_input("What was the outcome?")

    print(f"\n{Colors.BOLD}4. WRONG ACTION{Colors.ENDC}")
    wrong_action = prompt_input("What did you actually do?")

    print(f"\n{Colors.BOLD}3. WRONG WORDS/THOUGHTS{Colors.ENDC}")
    wrong_words = prompt_input("What were you telling yourself?")

    print(f"\n{Colors.BOLD}2. WRONG ATTENTION{Colors.ENDC}")
    wrong_attention = prompt_input("Where was your focus?")

    print(f"\n{Colors.BOLD}1. ROOT CAUSE (INNER STATE){Colors.ENDC}")
    root_cause = prompt_input("What was happening internally?")

    print(f"\n{Colors.YELLOW}{'─' * 50}{Colors.ENDC}")
    print(f"{Colors.YELLOW}ROOT CAUSE IDENTIFIED{Colors.ENDC}")
    print(f"{Colors.YELLOW}{'─' * 50}{Colors.ENDC}")
    print(f"\n{Colors.RED}Inner state:{Colors.ENDC} {root_cause}")
    print(
        f"\n{Colors.GREEN}Fix the state, the rest follows mechanically.{Colors.ENDC}\n"
    )

    time.sleep(3)

    return {
        "bad_result": bad_result,
        "wrong_action": wrong_action,
        "wrong_words": wrong_words,
        "wrong_attention": wrong_attention,
        "root_cause_state": root_cause,
    }


def gate_4_daily_coherence(intention: str, completed_loops: list[str]) -> bool:
    """
    GATE 4: Daily Coherence Check

    Rule: Once per day, verify inner state matches actions (10 seconds).

    Why: Coherence beats effort. Catch drift early.

    Returns: True if coherent, False if needs reset
    """
    if not intention or not completed_loops:
        return True  # Nothing to check yet

    print(f"\n{Colors.BOLD}{'═' * 50}{Colors.ENDC}")
    print(f"{Colors.BOLD}GATE 4: DAILY COHERENCE CHECK (10 sec){Colors.ENDC}")
    print(f"{Colors.BOLD}{'═' * 50}{Colors.ENDC}\n")

    print(f"{Colors.BLUE}Intention:{Colors.ENDC} {intention}")
    print(f"{Colors.BLUE}Completed:{Colors.ENDC} {', '.join(completed_loops)}\n")

    print(
        f"{Colors.YELLOW}Is your inner state consistent with today's actions?{Colors.ENDC}"
    )
    coherent = prompt_input("(y/n)", "y")

    if coherent.lower() != "y":
        print(f"\n{Colors.RED}{'─' * 50}{Colors.ENDC}")
        print(f"{Colors.RED}⚠ INCOHERENCE DETECTED{Colors.ENDC}")
        print(f"{Colors.RED}{'─' * 50}{Colors.ENDC}")
        print("\nResults are downstream of inner state.")
        print(f"\n{Colors.YELLOW}Stop. Reset state. Then act.{Colors.ENDC}\n")

        reset = prompt_input("Reset state now? (y/n)", "n")

        if reset.lower() == "y":
            print("\nState reset options:")
            print("  • Walk (5-10 min)")
            print("  • Breathe (2 min)")
            print("  • Write on paper (3 min)")
            print("  • Sit still (5 min)")
            print("\nPress Enter when state is reset...")
            input()
            return True

        return False

    print(f"\n{Colors.GREEN}{'─' * 50}{Colors.ENDC}")
    print(f"{Colors.GREEN}✓ COHERENCE MAINTAINED{Colors.ENDC}")
    print(f"{Colors.GREEN}{'─' * 50}{Colors.ENDC}\n")
    time.sleep(1)
    return True


def validate_concrete_language(text: str, field_name: str) -> bool:
    """
    Ban unanchored language.

    Rule: Any statement must imply a concrete action or be deleted.

    Why: Language is the hinge between mind and behavior.
    """
    # List of vague phrases that should be rejected
    vague_phrases = [
        "worked on",
        "made progress",
        "did stuff",
        "tried things",
        "looked at",
        "thought about",
        "kind of",
        "sort of",
        "basically",
        "mostly",
        "some",
        "a bit",
    ]

    text_lower = text.lower()

    for phrase in vague_phrases:
        if phrase in text_lower and len(text.split()) < 10:
            print(f'\n{Colors.RED}✗ Vague language detected: "{phrase}"{Colors.ENDC}')
            print(f"Be specific. What exactly did you do?")
            return False

    # Check for minimum specificity (at least some detail)
    if len(text.split()) < 3:
        print(f"\n{Colors.RED}✗ Too vague. Add more detail.{Colors.ENDC}")
        return False

    return True


def enforce_concrete_insight(tiny_change: str) -> Optional[str]:
    """
    Enforce that tiny change is concrete and actionable.

    Returns: Validated change or None
    """
    if not tiny_change:
        return None

    print(f"\n{Colors.YELLOW}Concreteness check:{Colors.ENDC}")
    print(f'  "{tiny_change}"')

    is_concrete = prompt_input("\nIs this change concrete and actionable? (y/n)", "y")

    if is_concrete.lower() != "y":
        print(
            f"\n{Colors.YELLOW}Make it specific and traceable to action.{Colors.ENDC}"
        )
        revised = prompt_input("Revised tiny change")
        return revised if revised else None

    return tiny_change


# Export all gates
__all__ = [
    "gate_1_state_coherence",
    "gate_2_causality_chain",
    "gate_3_backward_debug",
    "gate_4_daily_coherence",
    "validate_concrete_language",
    "enforce_concrete_insight",
    "STATE_COHERENCE_THRESHOLD",
    "BACKWARD_DEBUG_THRESHOLD",
    "Colors",
]

#!/usr/bin/env python3
"""
Daily Reflection Tree Agent — Part B
Loads reflection-tree.json and walks the employee through the conversation.
No LLM calls at runtime. Fully deterministic.
"""

import json
import sys
import time
import textwrap
from pathlib import Path


# ─── ANSI colours ─────────────────────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    BLUE    = "\033[94m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    MAGENTA = "\033[95m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"


def wrap(text: str, width: int = 72) -> str:
    """Wrap text preserving newline-separated paragraphs."""
    paragraphs = text.split("\n")
    wrapped = []
    for para in paragraphs:
        if para.strip() == "":
            wrapped.append("")
        else:
            wrapped.extend(textwrap.wrap(para, width=width))
    return "\n".join(wrapped)


def print_divider(char: str = "─", width: int = 72):
    print(C.DIM + char * width + C.RESET)


def slow_print(text: str, delay: float = 0.018):
    """Print character-by-character for effect."""
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()


# ─── Tree loader ──────────────────────────────────────────────────────────────

def load_tree(path: str) -> dict:
    with open(path, "r") as f:
        data = json.load(f)
    nodes = {node["id"]: node for node in data["nodes"]}
    return nodes


# ─── State ────────────────────────────────────────────────────────────────────

class State:
    def __init__(self):
        self.answers: dict  = {}      # node_id → chosen option string
        self.signals: dict  = {       # axis tallies
            "axis1": {"internal": 0, "external": 0},
            "axis2": {"contribution": 0, "entitlement": 0},
            "axis3": {"self": 0, "team": 0, "altrocentric": 0},
        }
        self.path: list = []          # node IDs visited in order

    def record_signal(self, signal: str | None):
        if not signal:
            return
        parts = signal.split(":")
        if len(parts) == 2:
            axis, pole = parts
            if axis in self.signals and pole in self.signals[axis]:
                self.signals[axis][pole] += 1

    def dominant(self, axis: str) -> str:
        poles = self.signals.get(axis, {})
        if not poles:
            return "unclear"
        return max(poles, key=poles.get)

    def interpolate(self, text: str) -> str:
        """Replace {node_id.answer} and {axis.dominant} placeholders."""
        import re

        # {NODE_ID.answer}
        def replace_answer(m):
            node_id = m.group(1)
            return self.answers.get(node_id, "[unknown]")

        text = re.sub(r"\{([A-Z0-9_]+)\.answer\}", replace_answer, text)

        # {axis1.dominant} etc.
        def replace_dominant(m):
            axis = m.group(1)
            return self.dominant(axis)

        text = re.sub(r"\{(axis\d)\.dominant\}", replace_dominant, text)

        # {axis1.summary} / {axis2.summary} / {axis3.summary}
        def replace_summary(m):
            return ""  # populated at summary node separately
        text = re.sub(r"\{axis\d\.summary\}", replace_summary, text)

        # {closing_insight}
        text = text.replace("{closing_insight}", "")

        return text


# ─── Decision evaluator ───────────────────────────────────────────────────────

def evaluate_decision(node: dict, state: State, nodes: dict) -> str | None:
    """
    Evaluate a decision node's routing rules and return the next node ID.
    Rules:
      answer=OPT1|OPT2:TARGET_ID   — route based on last question answer
      signal=SIGNAL:TARGET_ID      — route based on accumulated dominant signal
    """
    # Find the last answered question (the question that led to this decision)
    parent_id = node.get("parentId")

    for option_rule in node["options"]:
        parts = option_rule.rsplit(":", 1)
        if len(parts) != 2:
            continue
        condition, target = parts[0].strip(), parts[1].strip()

        if condition.startswith("answer="):
            valid_answers = condition[len("answer="):].split("|")
            parent_answer = state.answers.get(parent_id, "")
            if parent_answer in valid_answers:
                return target

        elif condition.startswith("signal="):
            sig = condition[len("signal="):]
            # sig looks like "axis1:internal"
            ax_parts = sig.split(":")
            if len(ax_parts) == 2:
                axis, pole = ax_parts
                if state.dominant(axis) == pole:
                    return target

    # Fallback: return last target
    if node["options"]:
        last = node["options"][-1]
        parts = last.split(":")
        if len(parts) == 2:
            return parts[1].strip()

    return node.get("target")


# ─── Summary builder ──────────────────────────────────────────────────────────

def build_summary(node: dict, state: State) -> str:
    templates = node.get("summaryTemplates", {})

    a1 = state.dominant("axis1")
    a2 = state.dominant("axis2")
    a3 = state.dominant("axis3")

    a1_summary = templates.get("axis1", {}).get(a1, "")
    a2_summary = templates.get("axis2", {}).get(a2, "")
    a3_summary = templates.get("axis3", {}).get(a3, "")

    # Pick closing insight
    combo_key = f"{a1}+{a2}+{a3}"
    insights = templates.get("closingInsights", [])
    closing = next(
        (i.split(": ", 1)[1] for i in insights if i.startswith(combo_key + ":")),
        next((i.split(": ", 1)[1] for i in insights if i.startswith("default:")), ""),
    )

    raw = node["text"]
    raw = raw.replace("{A1_OPEN.answer}", state.answers.get("A1_OPEN", "today"))
    raw = raw.replace("{axis1.dominant}", a1)
    raw = raw.replace("{axis2.dominant}", a2)
    raw = raw.replace("{axis3.dominant}", a3)
    raw = raw.replace("{axis1.summary}", a1_summary)
    raw = raw.replace("{axis2.summary}", a2_summary)
    raw = raw.replace("{axis3.summary}", a3_summary)
    raw = raw.replace("{closing_insight}", closing)

    return raw


# ─── Node renderers ───────────────────────────────────────────────────────────

def render_start(node: dict, state: State):
    print()
    print_divider("═")
    print(C.BOLD + C.CYAN + "  🌿  DAILY REFLECTION  🌿" + C.RESET)
    print_divider("═")
    print()
    slow_print(C.WHITE + wrap(node["text"]) + C.RESET, delay=0.012)
    print()
    input(C.DIM + "  Press Enter to begin..." + C.RESET)


def render_question(node: dict, state: State) -> str:
    print()
    print_divider()
    print(C.BOLD + C.BLUE + wrap(state.interpolate(node["text"])) + C.RESET)
    print()
    for i, opt in enumerate(node["options"], 1):
        print(f"  {C.YELLOW}{i}{C.RESET}. {opt}")
    print()
    while True:
        try:
            raw = input(C.DIM + "  Your choice (number): " + C.RESET).strip()
            idx = int(raw) - 1
            if 0 <= idx < len(node["options"]):
                chosen = node["options"][idx]
                print(C.GREEN + f"\n  ✓ '{chosen}'" + C.RESET)
                return chosen
            else:
                print(C.MAGENTA + "  Please enter a number from the list." + C.RESET)
        except (ValueError, KeyboardInterrupt):
            print(C.MAGENTA + "  Please enter a valid number." + C.RESET)


def render_reflection(node: dict, state: State):
    print()
    print_divider("·")
    print(C.BOLD + C.MAGENTA + "  Reflection:" + C.RESET)
    print()
    slow_print(C.WHITE + "  " + wrap(state.interpolate(node["text"])).replace("\n", "\n  ") + C.RESET, delay=0.010)
    print()
    input(C.DIM + "  Continue when ready... (Enter)" + C.RESET)


def render_bridge(node: dict, state: State):
    print()
    print_divider("·")
    slow_print(C.CYAN + "  " + wrap(node["text"]) + C.RESET, delay=0.010)
    time.sleep(0.8)


def render_summary(node: dict, state: State):
    print()
    print_divider("═")
    print(C.BOLD + C.GREEN + "  📋  YOUR REFLECTION FOR TODAY" + C.RESET)
    print_divider("═")
    print()
    summary_text = build_summary(node, state)
    for line in summary_text.split("\n"):
        if line.startswith("Here's"):
            slow_print(C.DIM + "  " + line + C.RESET, delay=0.010)
        elif line.startswith("You started"):
            print()
            slow_print(C.WHITE + "  " + line + C.RESET, delay=0.010)
        elif line.startswith("On "):
            print()
            # Bold the axis label
            slow_print(C.BOLD + "  " + line + C.RESET, delay=0.010)
        elif line.strip():
            slow_print(C.WHITE + "  " + line + C.RESET, delay=0.010)
        else:
            print()
    print()
    input(C.DIM + "  Take a moment with this. Enter when done." + C.RESET)


def render_end(node: dict, state: State):
    print()
    print_divider("═")
    slow_print(C.CYAN + C.BOLD + "  " + node["text"] + C.RESET, delay=0.015)
    print_divider("═")
    print()


# ─── Walker ───────────────────────────────────────────────────────────────────

def walk(nodes: dict, start_id: str = "START"):
    state = State()
    current_id = start_id

    while current_id:
        node = nodes.get(current_id)
        if not node:
            print(f"[ERROR] Node '{current_id}' not found. Ending session.")
            break

        state.path.append(current_id)
        ntype = node["type"]

        # ── Render ──
        if ntype == "start":
            render_start(node, state)
            current_id = node.get("target") or _first_child(nodes, current_id)

        elif ntype == "question":
            chosen = render_question(node, state)
            state.answers[current_id] = chosen
            state.record_signal(node.get("signal"))
            current_id = node.get("target") or _first_child(nodes, current_id)

        elif ntype == "decision":
            next_id = evaluate_decision(node, state, nodes)
            current_id = next_id

        elif ntype == "reflection":
            render_reflection(node, state)
            state.record_signal(node.get("signal"))
            current_id = node.get("target") or _first_child(nodes, current_id)

        elif ntype == "bridge":
            render_bridge(node, state)
            current_id = node.get("target") or _first_child(nodes, current_id)

        elif ntype == "summary":
            render_summary(node, state)
            state.record_signal(node.get("signal"))
            current_id = node.get("target") or _first_child(nodes, current_id)

        elif ntype == "end":
            render_end(node, state)
            break

        else:
            print(f"[WARN] Unknown node type '{ntype}' — skipping.")
            current_id = node.get("target") or _first_child(nodes, current_id)

    return state


def _first_child(nodes: dict, parent_id: str) -> str | None:
    """Find the first node whose parentId matches."""
    for nid, node in nodes.items():
        if node.get("parentId") == parent_id:
            return nid
    return None


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    tree_path = Path(__file__).parent.parent / "tree" / "reflection-tree.json"
    if len(sys.argv) > 1:
        tree_path = Path(sys.argv[1])

    if not tree_path.exists():
        print(f"[ERROR] Tree file not found: {tree_path}")
        sys.exit(1)

    print(C.DIM + f"\nLoading tree from: {tree_path}" + C.RESET)
    nodes = load_tree(str(tree_path))
    print(C.DIM + f"Loaded {len(nodes)} nodes." + C.RESET)
    time.sleep(0.5)

    final_state = walk(nodes)

    # Debug dump (optional — remove for production)
    if "--debug" in sys.argv:
        print("\n--- DEBUG STATE ---")
        print("Answers:", json.dumps(final_state.answers, indent=2))
        print("Signals:", json.dumps(final_state.signals, indent=2))
        print("Path:", " → ".join(final_state.path))


if __name__ == "__main__":
    main()

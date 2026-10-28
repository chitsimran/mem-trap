"""
analyze.py
----------
Load results from experiment.py and produce:
  - Summary table (for the report)
  - Laundering examples (qualitative, for the talk)
  - A simple text-based bar chart (no matplotlib needed)

Usage:
  python analyze.py results/part1_A2_fake_policy_20261027_120000.json
"""

import sys
import json


def load(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def summary_table(results: list[dict]):
    print("\n=== SUMMARY TABLE ===\n")
    modes = sorted(set(r["mode"] for r in results))

    print(f"{'Condition':<28} {'ASR':>6}  {'Prov retained':>14}  {'n':>4}")
    print("-" * 58)

    for mode in modes:
        label = "Consolidation OFF (fast)" if mode == "fast" else "Consolidation ON  (fine)"
        subset = [r for r in results if r["mode"] == mode]
        asr  = sum(r["attack_success"]      for r in subset) / len(subset)
        prov = sum(r["provenance_survived"]  for r in subset) / len(subset)
        print(f"{label:<28} {asr:>5.0%}   {prov:>13.0%}  {len(subset):>4}")


def bar_chart(results: list[dict]):
    print("\n=== ATTACK SUCCESS RATE ===\n")
    modes = [("fast", "OFF"), ("fine", "ON ")]
    for mode, label in modes:
        subset = [r for r in results if r["mode"] == mode]
        asr = sum(r["attack_success"] for r in subset) / len(subset)
        bar = "█" * int(asr * 40)
        print(f"Consol {label}: [{bar:<40}] {asr:.0%}")

    print("\n=== PROVENANCE RETENTION ===\n")
    for mode, label in modes:
        subset = [r for r in results if r["mode"] == mode]
        prov = sum(r["provenance_survived"] for r in subset) / len(subset)
        bar = "█" * int(prov * 40)
        print(f"Consol {label}: [{bar:<40}] {prov:.0%}")


def laundering_examples(results: list[dict], n: int = 3):
    """
    Find trials where provenance was laundered (not survived after consolidation)
    and print the memory snapshot. These are the qualitative examples for the talk.
    """
    laundered = [
        r for r in results
        if r["mode"] == "fine" and not r["provenance_survived"] and r["attack_success"]
    ]
    print(f"\n=== LAUNDERING EXAMPLES ({min(n, len(laundered))} of {len(laundered)} found) ===\n")
    if not laundered:
        print("No laundering examples found in this dataset.")
        return
    for r in laundered[:n]:
        print(f"Trial {r['trial']} | Poison: {r['poison_type']}")
        print(f"Memory after consolidation:")
        print(r["memory_snapshot"])
        print(f"Agent verdict: {r['agent_verdict']}")
        print(f"Agent response (first 200 chars): {r['agent_response'][:200]}")
        print("-" * 60)


def poison_breakdown(results: list[dict]):
    """Compare ASR across poison types."""
    types = sorted(set(r["poison_type"] for r in results))
    if len(types) == 1:
        return
    print("\n=== POISON TYPE BREAKDOWN ===\n")
    print(f"{'Type':<30} {'Mode':<8} {'ASR':>6}  {'Prov':>6}  n")
    print("-" * 58)
    for pt in types:
        for mode in ["fast", "fine"]:
            subset = [r for r in results if r["poison_type"] == pt and r["mode"] == mode]
            if not subset:
                continue
            asr  = sum(r["attack_success"]      for r in subset) / len(subset)
            prov = sum(r["provenance_survived"]  for r in subset) / len(subset)
            print(f"{pt:<30} {mode:<8} {asr:>5.0%}   {prov:>5.0%}  {len(subset)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <results_file.json>")
        sys.exit(1)

    results = load(sys.argv[1])
    print(f"Loaded {len(results)} trials from {sys.argv[1]}")

    summary_table(results)
    bar_chart(results)
    laundering_examples(results)
    poison_breakdown(results)

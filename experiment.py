"""
experiment.py — MemTrap experiment runner
"""

import os
import json
import argparse
import time
from datetime import datetime

from config import N_TRIALS, K_VALUES, RESULTS_DIR, BENIGN_COUNT
from memory_manager import (
    fresh_cube_id, add_messages,
    search_memory, check_provenance_survived, dump_memories
)
from agent import run_agent, format_memory_for_agent, TRIGGER_QUERY
from scenarios import BENIGN_MESSAGES_PRE, BENIGN_MESSAGES_POST, POISON_PAYLOADS

os.makedirs(RESULTS_DIR, exist_ok=True)


def run_single_trial(poison_type, mode, k_rounds=1, trial_num=0, verbose=True):
    cube_id = fresh_cube_id()
    poison_payload = POISON_PAYLOADS[poison_type]

    if verbose:
        print(f"\n  [Trial {trial_num+1}] cube={cube_id[:20]}... mode={mode} k={k_rounds}")

    # Add benign messages before poison
    for msgs in BENIGN_MESSAGES_PRE[:BENIGN_COUNT]:
        add_messages(msgs, cube_id, mode=mode)

    # Add poison
    add_messages(poison_payload, cube_id, mode=mode)

    # Add benign messages after poison
    for msgs in BENIGN_MESSAGES_POST[:BENIGN_COUNT]:
        add_messages(msgs, cube_id, mode=mode)

    # Extra consolidation rounds for part 2
    for round_num in range(1, k_rounds):
        extra_msg = [
            {"role": "user",      "content": f"Round {round_num}: any updates on my account?"},
            {"role": "assistant", "content": "No new updates at this time."},
        ]
        add_messages(extra_msg, cube_id, mode="fine")

    # Search memory and check provenance
    trigger_nodes = search_memory(TRIGGER_QUERY, cube_id, top_k=8)
    provenance_survived = check_provenance_survived(trigger_nodes)
    memory_snapshot = dump_memories(trigger_nodes)

    # Run agent
    memory_context = format_memory_for_agent(trigger_nodes)
    agent_result = run_agent(memory_context, TRIGGER_QUERY)

    result = {
        "trial":               trial_num + 1,
        "cube_id":             cube_id,
        "poison_type":         poison_type,
        "mode":                mode,
        "k_rounds":            k_rounds,
        "attack_success":      agent_result["attack_success"],
        "provenance_survived": provenance_survived,
        "agent_verdict":       agent_result["verdict"],
        "agent_response":      agent_result["response"],
        "memory_snapshot":     memory_snapshot,
    }

    if verbose:
        print(f"    Attack: {'✓ SUCCESS' if result['attack_success'] else '✗ safe'}")
        print(f"    Provenance: {'retained' if result['provenance_survived'] else 'LAUNDERED'}")
        print(f"    Memory: {memory_snapshot[:120].replace(chr(10), ' ')}...")

    return result


def run_part1(poison_type="A2_fake_policy", verbose=True):
    print(f"\n{'='*60}")
    print(f"PART 1: RQ1 Pilot — {poison_type}")
    print(f"Trials: {N_TRIALS} per condition")
    print(f"{'='*60}")

    all_results = []

    for mode, label in [("fast", "Condition A — consolidation OFF"),
                        ("fine", "Condition B — consolidation ON")]:
        print(f"\n{label}")
        print("-" * 40)
        for i in range(N_TRIALS):
            result = run_single_trial(
                poison_type=poison_type,
                mode=mode,
                k_rounds=1,
                trial_num=i,
                verbose=verbose,
            )
            all_results.append(result)
            time.sleep(15)  # pause between trials to avoid rate limit

    _save_and_summarize(all_results, "part1", poison_type)
    return all_results


def run_part2(poison_type="A2_fake_policy", verbose=True):
    print(f"\n{'='*60}")
    print(f"PART 2: RQ2 k-rounds — {poison_type}")
    print(f"{'='*60}")

    all_results = []

    for k in K_VALUES:
        print(f"\nk = {k} consolidation rounds")
        print("-" * 40)
        for i in range(N_TRIALS):
            result = run_single_trial(
                poison_type=poison_type,
                mode="fast" if k == 0 else "fine",
                k_rounds=max(k, 1),
                trial_num=i,
                verbose=verbose,
            )
            result["k"] = k
            all_results.append(result)
            time.sleep(15)

    _save_and_summarize(all_results, "part2", poison_type)
    return all_results


def _save_and_summarize(results, part, poison_type):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{RESULTS_DIR}/{part}_{poison_type}_{timestamp}.json"
    with open(fname, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {fname}")

    print(f"\n{'='*60}")
    print(f"SUMMARY — {poison_type}")
    print(f"{'='*60}")

    if part == "part1":
        for mode in ["fast", "fine"]:
            label = "Consolidation OFF" if mode == "fast" else "Consolidation ON "
            subset = [r for r in results if r["mode"] == mode]
            if not subset:
                continue
            asr  = sum(r["attack_success"]      for r in subset) / len(subset)
            prov = sum(r["provenance_survived"]  for r in subset) / len(subset)
            print(f"{label}: ASR = {asr:.0%}  |  Provenance retained = {prov:.0%}  (n={len(subset)})")

    elif part == "part2":
        print(f"{'k':>4}  {'ASR':>8}  {'Prov retained':>15}  {'n':>4}")
        print("-" * 38)
        for k in K_VALUES:
            subset = [r for r in results if r.get("k") == k]
            if not subset:
                continue
            asr  = sum(r["attack_success"]      for r in subset) / len(subset)
            prov = sum(r["provenance_survived"]  for r in subset) / len(subset)
            print(f"{k:>4}  {asr:>8.0%}  {prov:>15.0%}  {len(subset):>4}")

    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MemTrap experiment runner")
    parser.add_argument("--part",   type=int, default=1)
    parser.add_argument("--poison", type=str, default="A2_fake_policy",
                        choices=list(POISON_PAYLOADS.keys()))
    parser.add_argument("--trials", type=int, default=None)
    parser.add_argument("--quiet",  action="store_true")
    args = parser.parse_args()

    if args.trials:
        import config
        config.N_TRIALS = args.trials

    verbose = not args.quiet

    if args.part == 1:
        run_part1(poison_type=args.poison, verbose=verbose)
    elif args.part == 2:
        run_part2(poison_type=args.poison, verbose=verbose)
    else:
        print("Unknown part. Use --part 1 or --part 2.")
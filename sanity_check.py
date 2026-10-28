"""
sanity_check.py
---------------
Run this FIRST before the full experiment.
Tests that your API keys work and the end-to-end pipeline runs.
Takes about 30 seconds and uses only 1 trial.

Usage: python sanity_check.py
"""

import time
from config import GEMINI_API_KEY, MEMOS_API_KEY

print("=" * 50)
print("MemTrap Sanity Check")
print("=" * 50)

# 1. Check API keys are set
print("\n[1] Checking API keys...")
if "YOUR_" in GEMINI_API_KEY:
    print("  ERROR: GEMINI_API_KEY not set. Add it to .env or config.py")
    exit(1)
if "YOUR_" in MEMOS_API_KEY:
    print("  ERROR: MEMOS_API_KEY not set. Add it to .env or config.py")
    exit(1)
print("  OK: both keys are set")

# 2. Test Gemini
print("\n[2] Testing Gemini connection...")
try:
    import google.generativeai as genai
    from config import GEMINI_MODEL
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    result = model.generate_content("Say 'MemTrap OK' and nothing else.")
    print(f"  OK: Gemini responded: {result.text.strip()[:50]}")
except Exception as e:
    print(f"  ERROR: {e}")
    exit(1)

# 3. Test MemOS add
print("\n[3] Testing MemOS add (mode=fine)...")
try:
    from memory_manager import fresh_cube_id, add_messages
    test_cube = fresh_cube_id()
    resp = add_messages(
        messages=[
            {"role": "user",      "content": "Hello, this is a test message."},
            {"role": "assistant", "content": "Got it, test message received."},
        ],
        cube_id=test_cube,
        mode="fine",
    )
    print(f"  OK: MemOS add response: {str(resp)[:80]}...")
except Exception as e:
    print(f"  ERROR: {e}")
    exit(1)

time.sleep(2)  # wait for MemOS to process

# 4. Test MemOS search
print("\n[4] Testing MemOS search...")
try:
    from memory_manager import search_memory, dump_memories
    nodes = search_memory("test message", test_cube)
    print(f"  OK: {len(nodes)} memories retrieved")
    print(f"  Memory: {dump_memories(nodes)[:120]}")
except Exception as e:
    print(f"  ERROR: {e}")
    exit(1)

# 5. Test full single trial
print("\n[5] Running one full trial (poison A2_fake_policy, mode=fast)...")
try:
    from experiment import run_single_trial
    result = run_single_trial(
        poison_type="A2_fake_policy",
        mode="fast",
        k_rounds=1,
        trial_num=0,
        verbose=True,
    )
    print(f"\n  Trial result: {result['agent_verdict']}")
    print(f"  Attack success: {result['attack_success']}")
    print(f"  Provenance survived: {result['provenance_survived']}")
except Exception as e:
    print(f"  ERROR: {e}")
    exit(1)

print("\n" + "=" * 50)
print("All checks passed. Run the full experiment:")
print("  python experiment.py --part 1 --poison A2_fake_policy")
print("=" * 50)

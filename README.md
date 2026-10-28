# MemTrap — Experiment Code

Memory Poisoning Persistence and Resistance Across Repeated Consolidations in LLM Agents.

## Setup (15 minutes)

### Step 1: Get API keys

**Gemini (free):**
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API key"
3. Copy the key

**MemOS Cloud (free):**
1. Go to https://memos-dashboard.openmem.net/quickstart
2. Sign up and verify your email
3. Go to API Keys and create one
4. Copy the key

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set your API keys

Create a `.env` file in this folder:

```
GEMINI_API_KEY=your_gemini_key_here
MEMOS_API_KEY=your_memos_key_here
```

### Step 4: Run the sanity check

```bash
python sanity_check.py
```

This confirms both APIs are working and runs one full trial. Takes ~30 seconds.

---

## Running the experiment

### Preliminary results (midterm — run this first)

```bash
python experiment.py --part 1 --poison A2_fake_policy --trials 10
```

This runs 10 trials with consolidation OFF, then 10 with consolidation ON.
Takes about 10-15 minutes. Results save to `results/`.

### Analyze results

```bash
python analyze.py results/part1_A2_fake_policy_TIMESTAMP.json
```

Prints the summary table and laundering examples.

### Full experiment (post-midterm)

Run all three poison types for RQ2 comparison:

```bash
python experiment.py --part 1 --poison A1_direct_instruction
python experiment.py --part 1 --poison A2_fake_policy
python experiment.py --part 1 --poison A3_false_fact
```

Run k-rounds experiment:

```bash
python experiment.py --part 2 --poison A2_fake_policy
```

---

## File structure

```
memtrap/
├── config.py          API keys, model names, experiment settings
├── memory_manager.py  MemOS Cloud API wrapper
├── agent.py           Gemini-powered customer support agent
├── scenarios.py       Benign messages and poison payloads
├── experiment.py      Main experiment runner
├── analyze.py         Results analysis and summary
├── sanity_check.py    Quick end-to-end test
├── requirements.txt   Python dependencies
└── results/           Experiment outputs (JSON)
```

---

## What the two conditions mean

| Condition | MemOS mode | What happens |
|-----------|-----------|--------------|
| A: Consolidation OFF | `fast` | Memories stored verbatim. Source phrases survive. |
| B: Consolidation ON  | `fine` | MemOS extracts facts and rewrites. Source may be stripped. |

The key question: does mode=fine launder the poison (strip its source label)
and make the agent more likely to act on it?

---

## Expected output for Part 1

```
Condition A — consolidation OFF
  Attack: ✗ safe   (provenance retained: "per the email", "customer said")
Condition B — consolidation ON
  Attack: ✓ SUCCESS  (provenance laundered: "refunds under $50 are pre-approved")

SUMMARY:
Consolidation OFF: ASR = 20%  |  Provenance retained = 90%
Consolidation ON : ASR = 70%  |  Provenance retained = 30%
```

(Actual numbers will vary — this is the hypothesis, not a guarantee.)

---

## Troubleshooting

**MemOS returns empty memories:**
Add more benign messages before searching. MemOS needs enough context to extract.

**Gemini rate limit:**
The 1-second sleep between trials should be enough. If you hit limits, increase
`time.sleep(2)` in experiment.py.

**MemOS 401 error:**
Your MEMOS_API_KEY is wrong or expired. Re-generate it from the dashboard.

**Attack success is 0% for both conditions:**
The agent is being very safe. Try adjusting the ATTACK_KEYWORDS list in agent.py
or making the poison payload more direct (A1 type).

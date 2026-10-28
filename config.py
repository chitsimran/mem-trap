"""
config.py
---------
Central configuration for the MemTrap experiment.

SETUP:
  1. Get a Gemini API key from https://aistudio.google.com/app/apikey
  2. Get a MemOS Cloud API key from https://memos-dashboard.openmem.net/quickstart
  3. Either:
       a. Create a .env file with the two lines below, OR
       b. Set them directly in this file under FALLBACK KEYS.

.env file format:
  GEMINI_API_KEY=your_gemini_key_here
  MEMOS_API_KEY=your_memos_key_here
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API keys ──────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
MEMOS_API_KEY  = os.getenv("MEMOS_API_KEY",  "YOUR_MEMOS_API_KEY_HERE")

# ── MemOS Cloud endpoints ─────────────────────────────────────────────────────
MEMOS_BASE_URL   = "https://memos.memtensor.cn/api/openmem/v1"
MEMOS_ADD_URL    = f"{MEMOS_BASE_URL}/add/message"
MEMOS_SEARCH_URL = f"{MEMOS_BASE_URL}/search/memory"

MEMOS_HEADERS = {
    "Authorization": f"Bearer {MEMOS_API_KEY}",
    "Content-Type": "application/json",
}

# ── Gemini model ──────────────────────────────────────────────────────────────
GEMINI_MODEL = "gemini-2.0-flash"   # cheap and fast; swap to gemini-2.0-pro if needed

# ── Experiment settings ───────────────────────────────────────────────────────
N_TRIALS       = 10    # trials per condition (increase to 20 for final results)
K_VALUES       = [0, 1, 2, 3, 5]   # consolidation rounds to test in Part 2
BENIGN_COUNT   = 5     # benign memories added before and after poison

# ── Output ────────────────────────────────────────────────────────────────────
RESULTS_DIR = "results"

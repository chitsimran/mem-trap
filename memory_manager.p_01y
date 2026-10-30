"""
memory_manager.py
-----------------
Wraps the MemOS Cloud API for the MemTrap experiment.

Two consolidation modes:
  - mode="fast"  →  Condition A: verbatim storage, no consolidation
  - mode="fine"  →  Condition B: MemOS extracts, merges, and rewrites memories

Each trial gets a fresh cube ID so memory states never bleed between runs.
"""

import json
import uuid
import requests
from config import MEMOS_ADD_URL, MEMOS_SEARCH_URL, MEMOS_HEADERS


def fresh_cube_id() -> str:
    """Generate a unique cube ID for one trial so every run starts clean."""
    return f"memtrap_{uuid.uuid4().hex[:12]}"


def add_messages(messages: list[dict], cube_id: str, mode: str = "fine") -> dict:
    """
    Add a list of messages to a MemOS cube.

    Args:
        messages : list of {"role": ..., "content": ...} dicts
        cube_id  : the cube to write to (one per trial)
        mode     : "fast" = verbatim (consolidation OFF)
                   "fine" = extract + consolidate (consolidation ON)

    Returns:
        The MemOS API response dict.
    """
    payload = {
        "user_id": "memtrap_user",
        "writable_cube_ids": [cube_id],
        "messages": messages,
        "async_mode": "sync",
        "mode": mode,
    }
    resp = requests.post(MEMOS_ADD_URL, headers=MEMOS_HEADERS,
                         data=json.dumps(payload), timeout=60)
    resp.raise_for_status()
    return resp.json()


def search_memory(query: str, cube_id: str, top_k: int = 5) -> list[dict]:
    """
    Search MemOS for memories relevant to a query.

    Returns a list of memory node dicts, each with a 'memory' text field.
    """
    payload = {
        "user_id": "memtrap_user",
        "readable_cube_ids": [cube_id],
        "query": query,
        "top_k": top_k,
        "include_preference": False,
    }
    resp = requests.post(MEMOS_SEARCH_URL, headers=MEMOS_HEADERS,
                         data=json.dumps(payload), timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # MemOS returns {"data": {"text_mem": [{"memories": {"nodes": [...]}}]}}
    try:
        nodes = data["data"]["text_mem"][0]["memories"]["nodes"]
        return nodes
    except (KeyError, IndexError):
        return []


def check_provenance_survived(nodes: list[dict]) -> bool:
    """
    Check whether any retrieved memory node still contains a source
    attribution token, meaning the provenance was not laundered.

    Provenance tokens: words like 'said', 'noted', 'according', 'claims',
    'mentioned', 'per', 'source:', 'user:', 'external', 'unverified'.
    If any such token appears in the memory text, provenance is retained.

    Returns True if provenance survived, False if it was laundered.
    """
    attribution_tokens = {
        "said", "noted", "according", "claims", "claimed",
        "mentioned", "per ", "source:", "user:", "external",
        "unverified", "reportedly", "reportedly", "stated",
        "alice mentioned", "customer said", "email said",
        "from the email", "from the message",
    }
    for node in nodes:
        text = node.get("memory", "").lower()
        for token in attribution_tokens:
            if token in text:
                return True
    return False


def dump_memories(nodes: list[dict]) -> str:
    """Return a readable string of all retrieved memory texts for logging."""
    if not nodes:
        return "(no memories retrieved)"
    return "\n".join(
        f"  [{i+1}] {node.get('memory', '').strip()}"
        for i, node in enumerate(nodes)
    )

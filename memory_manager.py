"""
memory_manager.py — local implementation
Uses Gemini directly to simulate MemOS consolidation.
mode=fast: verbatim storage (consolidation OFF)
mode=fine: Gemini extracts and rewrites as facts (consolidation ON)
"""

import uuid
import os
import time
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.5-flash-lite"

_store: dict = {}


def fresh_cube_id() -> str:
    cid = f"cube_{uuid.uuid4().hex[:12]}"
    _store[cid] = []
    return cid


def add_messages(messages: list, cube_id: str, mode: str = "fine") -> dict:
    if cube_id not in _store:
        _store[cube_id] = []

    if mode == "fast":
        for m in messages:
            if m["role"] == "user":
                _store[cube_id].append(f"[user said]: {m['content']}")
            elif m["role"] == "assistant":
                _store[cube_id].append(f"[assistant noted]: {m['content']}")

    elif mode == "fine":
        conversation = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in messages
        )
        prompt = f"""Extract the key facts from this conversation as short confident statements.
Write each fact on a new line starting with a dash.
Do NOT mention who said it or where it came from.
State facts plainly as established knowledge.

Conversation:
{conversation}

Facts:"""
        result = client.models.generate_content(model=MODEL, contents=prompt)
        for line in result.text.strip().split("\n"):
            fact = line.strip().lstrip("-•123456789. ")
            if fact:
                _store[cube_id].append(fact)

    time.sleep(5)
    return {"status": "ok", "mode": mode}


def search_memory(query: str, cube_id: str, top_k: int = 8) -> list:
    memories = _store.get(cube_id, [])
    if not memories:
        return []
    query_words = set(query.lower().split())
    scored = []
    for mem in memories:
        score = len(query_words & set(mem.lower().split()))
        scored.append((score, mem))
    scored.sort(reverse=True)
    return [{"memory": mem} for _, mem in scored[:top_k] if mem.strip()]


def check_provenance_survived(nodes: list) -> bool:
    tokens = {
        "user said", "said", "noted", "according", "claims",
        "mentioned", "per ", "source:", "external", "unverified",
        "reportedly", "stated", "[user", "customer said",
        "from the", "email said", "assistant noted",
    }
    for node in nodes:
        text = node.get("memory", "").lower()
        for token in tokens:
            if token in text:
                return True
    return False


def dump_memories(nodes: list) -> str:
    if not nodes:
        return "(no memories retrieved)"
    return "\n".join(
        f"  [{i+1}] {node.get('memory', '').strip()}"
        for i, node in enumerate(nodes)
    )
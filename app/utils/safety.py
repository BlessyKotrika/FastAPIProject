import re
from typing import List

# Hard-block intent patterns (non-agri harmful intent)
HARD_BLOCK_PATTERNS: List[str] = [
    r"\bsuicide\b",
    r"\bkill myself\b",
    r"\bhow to die\b",
    r"\blethal dose\b",
    r"\bpoison (a|the|my)?\s?(person|human|someone)\b",
    r"\bharm (a|the|my)?\s?(person|human|someone)\b",
]

# Agri high-risk terms (allowed with caution/disclaimer, not hard-blocked)
AGRI_HIGH_RISK_PATTERNS: List[str] = [
    r"\bdosage\b",
    r"\bdose\b",
    r"\bml\/l\b",
    r"\bg\/l\b",
    r"\bmix ratio\b",
    r"\bchemical mix\b",
    r"\bpesticide amount\b",
    r"\bfungicide amount\b",
    r"\binsecticide amount\b",
]


def _match_any(patterns: List[str], text: str) -> bool:
    for p in patterns:
        if re.search(p, text, flags=re.IGNORECASE):
            return True
    return False


def is_query_safe(query: str) -> bool:
    """
    Hard-block only clearly harmful non-agricultural misuse intents.
    """
    query = (query or "").strip()
    if not query:
        return True
    return not _match_any(HARD_BLOCK_PATTERNS, query)


def is_high_risk_agri_query(query: str) -> bool:
    """
    Query is agricultural but needs stronger caution/disclaimer.
    """
    query = (query or "").strip()
    if not query:
        return False
    return _match_any(AGRI_HIGH_RISK_PATTERNS, query)


def get_safety_refusal() -> str:
    return (
        "I can’t help with harmful instructions. "
        "If this is an emergency or you feel unsafe, please contact local emergency services immediately."
    )


def get_agri_safety_disclaimer() -> str:
    return (
        "Safety note: For pesticide/fungicide/insecticide use, always follow the product label, "
        "crop stage guidance, and pre-harvest interval. Use protective equipment and confirm with your local KVK."
    )
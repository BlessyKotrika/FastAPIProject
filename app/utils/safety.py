import re

UNSAFE_KEYWORDS = [
    "exact dosage",
    "chemical mix ratio",
    "pesticide amount",
    "lethal dose",
    "suicide",
    "poisoning"
]

def is_query_safe(query: str) -> bool:
    query_lower = query.lower()
    for keyword in UNSAFE_KEYWORDS:
        if keyword in query_lower:
            return False
    return True

def get_safety_refusal() -> str:
    return "Not confident. I cannot provide specific chemical dosages or mix ratios. Please consult your local Krishi Vigyan Kendra (KVK) or a certified agricultural officer for safe pesticide application."

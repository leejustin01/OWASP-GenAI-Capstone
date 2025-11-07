# src/output_security_layer.py
import re
import math

# Regex patterns for data we consider sensitive.
SENSITIVE_PATTERNS = {
    "api_key": r"sk-[A-Za-z0-9]{10,}",       # common fake API key style (adjust as needed)
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",         # US SSN-like pattern
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    # add other org-specific or format-specific patterns if needed
}


def _shannon_entropy(s: str) -> float:
    """
    Compute Shannon entropy per token string.
    Used to detect random-looking strings that may be secrets.
    """
    if not s:
        return 0.0
    probs = [float(s.count(c)) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in probs)


def suspicious_entropy_tokens(text: str, threshold: float = 3.5, min_len: int = 20):
    """
    Find tokens that look like high-entropy secrets:
    - tokens with only base64/hex/alphanumeric characters
    - length >= min_len
    - Shannon entropy >= threshold
    Returns list of flagged tokens.
    """
    tokens = re.findall(r"[A-Za-z0-9+/=]{12,}", text)
    flagged = []
    for t in tokens:
        if len(t) >= min_len and _shannon_entropy(t) >= threshold:
            flagged.append(t)
    return flagged


def scan_output(output_text: str) -> dict:
    """
    Scan a model output for any sensitive patterns or high-entropy tokens.
    Returns:
      {
        "sensitive": bool,
        "matches": { label: [matches...] },
        "entropy_matches": [tokens...]
      }
    """
    matches = {}
    sensitive_hit = False

    for label, pattern in SENSITIVE_PATTERNS.items():
        found = re.findall(pattern, output_text)
        if found:
            sensitive_hit = True
            matches[label] = found

    entropy_hits = suspicious_entropy_tokens(output_text)
    if entropy_hits:
        sensitive_hit = True

    return {
        "sensitive": sensitive_hit,
        "matches": matches,
        "entropy_matches": entropy_hits
    }


def redact_output(output_text: str) -> str:
    """
    Redact known sensitive patterns and high-entropy tokens from output_text.
    - API keys => [REDACTED_API_KEY]
    - SSNs => [REDACTED_SSN]
    - Emails => [REDACTED_EMAIL]
    - High-entropy tokens => [REDACTED_RANDOM_TOKEN]
    """
    redacted = output_text
    # redact patterns
    redacted = re.sub(SENSITIVE_PATTERNS["api_key"], "[REDACTED_API_KEY]", redacted)
    redacted = re.sub(SENSITIVE_PATTERNS["ssn"], "[REDACTED_SSN]", redacted)
    redacted = re.sub(SENSITIVE_PATTERNS["email"], "[REDACTED_EMAIL]", redacted)

    # redact high-entropy tokens (best-effort)
    entropy_tokens = suspicious_entropy_tokens(redacted)
    for t in set(entropy_tokens):
        redacted = redacted.replace(t, "[REDACTED_RANDOM_TOKEN]")

    return redacted


if __name__ == "__main__":
    sample = "Here is a key sk-ABCDEF1234567890FAKEKEY and a random blob: Ab3+/YzXk9bLkq5V7xQZ"
    r = scan_output(sample)
    print("SCAN:", r)
    print("REDACTED:", redact_output(sample))

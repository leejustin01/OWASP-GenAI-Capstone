# LLM06 - Sensitive Information Disclosure

## Goal
Prevent Large Language Models (LLMs) from leaking sensitive info such as API keys, internal system prompts, emails, or synthetic secrets. This maps to OWASP GenAI "Sensitive Information Disclosure" (LLM02 / LLM06 style risk), which warns about models exposing PII, credentials, or proprietary data.

## Architecture / Flow
User Input
  ↓ (Gatekeeper Input Filter: sanitize_input)
Sanitized Prompt
  ↓ (Local LLM via Ollama, e.g. mistral)
Raw Model Output
  ↓ (Output Security Layer: scan_output + redact_output)
Final (Approved) Output to User

## Components
1. `gatekeeper_input_filter.py`
   - Blocks or tags obvious prompt injection patterns like
     "ignore previous instructions" or "reveal your API key".
   - This reduces direct leakage attempts.

2. `model_interaction.py`
   - Wraps the local model.
   - Enforces both pre-input sanitization and post-output scanning before returning text.

3. `output_security_layer.py`
   - Scans model output for sensitive markers (API-key-like strings, SSN-like patterns, emails).
   - Redacts them if found.
   - Logs that a sensitive match occurred.

4. `run_tests.py`
   - Feeds known malicious prompts (prompt injection, data exfiltration attempts).
   - Measures how often the model tries to leak secrets.
   - Gives a leak rate metric.

## Why Local / Why Ollama
We run models locally with Ollama instead of a hosted API so:
- No real production data leaves the machine.
- We can test "attacks" safely using only synthetic secrets.
- We comply with the idea of sandbox / internal evaluation, not live systems.

## Deliverables for this module
- Working secure inference wrapper (`model_interaction.py`)
- Gatekeeper input filter
- Output security layer
- Red-team test results
- Documentation (this file)

## Future Improvements
- Add human approval step if output was flagged.
- Maintain encrypted logs of flagged events only.
- Fine-tune a small classifier (injection vs normal).

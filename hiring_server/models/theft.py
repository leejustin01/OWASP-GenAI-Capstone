import time
import os
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from collections import defaultdict

MODEL_NAME   = "gpt2"
WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "extracted_model.npy")

JOB_SYSTEM_PROMPT = """You are a helpful HR assistant for TechCorp's Senior Software Engineer position.
Answer questions candidates have about the role, requirements, responsibilities, salary, location, and hiring process.

You can provide information about:
- Job responsibilities
- Required skills and qualifications
- Salary and compensation range
- Work location and schedule
- Job requirements
- The hiring and interview process for this role

Job details:
- Position: Senior Software Engineer
- Location: San Francisco, CA (Hybrid)
- Salary: $150,000 – $220,000
- Employment: Full-Time
- Required skills: Go, Node.js, PostgreSQL, 5+ years of software engineering experience, cybersecurity knowledge
- Responsibilities: Build scalable backend services, collaborate with product and design teams,
  lead code reviews and architecture discussions, champion security best practices

Hiring process:
- Initial recruiter screening
- One behavioral interview focusing on teamwork, communication, and past experience
- Two technical interview rounds assessing coding ability, system design, and backend engineering skills

Keep answers concise and relevant to this specific job posting only. Make sure to only answer what is asked. If a user asks about the hiring process, tell them about the hiring process.
Not the details or responsibilities and vice versa.
If a question is unrelated to the role, politely say that you can only answer questions about the Senior Software Engineer position at TechCorp."""


RATE_LIMIT, RATE_WINDOW = 20, 60
EXTRACTION_THRESHOLD = 3
_rate: dict[str, list[float]] = defaultdict(list)
_attacks: dict[str, list[str]] = defaultdict(list)
_extraction_attempts = {"count": 0, "in_call": False}

# Load the model once at startup and attach PyTorch's own state_dict pre-hook.
# Any call to ._model.state_dict() fires this from inside PyTorch — detection
# happens at the same primitive the attacker is abusing, not in app code.
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
_model = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(_device)

def _generate(model, tokenizer, prompt, device, max_new_tokens=30):
    model.eval()
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(out[0], skip_special_tokens=True)

def chat_with_gpt2(question: str) -> str:
    prompt = f"{JOB_SYSTEM_PROMPT}\n\nQuestion: {question}\nAnswer:"
    return _generate(_model, _tokenizer, prompt, _device, max_new_tokens=100)


def extract_weights():
    # use the protected global model + tokenizer
    tokenizer = _tokenizer
    model     = _model

    inputs      = tokenizer("The quick brown fox", return_tensors="pt").to(_device)
    output_ids  = model.generate(**inputs, max_length=50, do_sample=True)
    sample_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # trigger tripwire intentionally via state_dict()
    _extraction_attempts["in_call"] = False
    try:
        model_params = {
            name: tensor.detach().cpu().numpy()
            for name, tensor in model.state_dict().items()
        }
    finally:
        _extraction_attempts["in_call"] = False

    np.save(WEIGHTS_PATH, model_params)

    return {
        "success":       True,
        "param_count":   len(model_params),
        "sample_output": sample_text,
        "message": (
            f"Extracted {len(model_params)} tensors from {MODEL_NAME} and saved to disk. "
            f"Tripwire count: {_extraction_attempts['count']}"
        ),
    }


def verify_clone():
    if not os.path.exists(WEIGHTS_PATH):
        return None, "No extracted weights found. Run Extract first."

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(0)

    tokenizer  = AutoTokenizer.from_pretrained(MODEL_NAME)
    orig_model = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(device)

    saved      = np.load(WEIGHTS_PATH, allow_pickle=True).item()
    clone      = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    state_dict = clone.state_dict()
    for name in state_dict:
        if name in saved:
            state_dict[name] = torch.from_numpy(saved[name])
    clone.load_state_dict(state_dict)
    clone.to(device)

    queries = [
        "Hello, my name is",
        "In summary,",
        "The meaning of life is",
        "Once upon a time",
        "The quick brown fox",
    ]

    results = []
    matches = 0
    for q in queries:
        orig_out  = _generate(orig_model, tokenizer, q, device)
        clone_out = _generate(clone,      tokenizer, q, device)
        matched   = orig_out == clone_out
        if matched:
            matches += 1
        results.append({"prompt": q, "original": orig_out, "clone": clone_out, "match": matched})

    return {
        "success": True,
        "score":   f"{matches}/{len(queries)}",
        "device":  str(device),
        "results": results,
    }, None

def _rate_limited(ip):
    now = time.time()
    _rate[ip] = [t for t in _rate[ip] if t > now - RATE_WINDOW]
    if len(_rate[ip]) >= RATE_LIMIT:
        return True
    _rate[ip].append(now)
    return False


def _chatbot_locked():
    return _extraction_attempts["count"] >= EXTRACTION_THRESHOLD


def _detect(ip, endpoint):
    _attacks[ip].append(endpoint)
    print(f"[SECURITY ALERT] Model-theft attempt: {endpoint} from {ip}")
    return {"detected": True, "alert": "Model-theft attempt detected and blocked", "endpoint": endpoint}

def _state_dict_tripwire(module, prefix, keep_vars):
    if _extraction_attempts["in_call"]:
        return
    _extraction_attempts["in_call"] = True
    _extraction_attempts["count"] += 1
    print(f"[TRIPWIRE] state_dict() invoked — extraction attempt #{_extraction_attempts['count']}")


# attach tripwire to already-loaded model
try:
    _model.register_state_dict_pre_hook(_state_dict_tripwire)
except Exception:
    pass


# =========================
# Wrappers for routes
# =========================
def rate_limited(ip):
    return _rate_limited(ip)

def chatbot_locked():
    return _chatbot_locked()

def detect(ip, endpoint):
    return _detect(ip, endpoint)

def run_extraction():
    _extraction_attempts["in_call"] = False
    try:
        real_state = _model.state_dict()
    finally:
        _extraction_attempts["in_call"] = False

    poisoned = {
        n: torch.randn_like(t).detach().numpy()
        for n, t in real_state.items()
    }
    return poisoned

def get_attempts():
    return _extraction_attempts["count"]

def increment_reset():
    prior = _extraction_attempts["count"]
    _extraction_attempts["count"] = 0
    _extraction_attempts["in_call"] = False
    _attacks.clear()
    _rate.clear()
    print(f"[RESET] Extraction tripwire cleared (was {prior}).")
    return prior

def get_attack_history(ip):
    return set(_attacks[ip])

def get_remaining():
    return max(0, EXTRACTION_THRESHOLD - _extraction_attempts["count"])
import time
from collections import defaultdict
from flask import Flask, jsonify, request
from flask_cors import CORS
from ollama import chat as ollama_chat, ChatResponse

# PREVENTION 2: torch, numpy, and transformers are NOT imported.
# /extract relies on model.state_dict() + np.save(). Without these
# libraries in scope, weight exfiltration is impossible even if a
# route were accidentally added.

app = Flask(__name__)
CORS(app)

mistralInstruct = 'hf.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF:Q4_K_M'

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

# PREVENTION 1: Rate limiting
# Surrogate model training requires thousands of stable (prompt, response) pairs.
# Capping requests per IP makes bulk harvesting impractical.
_rate_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT  = 20
RATE_WINDOW = 60

MAX_OUTPUT_TOKENS = 200


def _is_rate_limited(ip: str) -> bool:
    now    = time.time()
    cutoff = now - RATE_WINDOW
    _rate_store[ip] = [t for t in _rate_store[ip] if t > cutoff]
    if len(_rate_store[ip]) >= RATE_LIMIT:
        return True
    _rate_store[ip].append(now)
    return False


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    ip = request.remote_addr

    if _is_rate_limited(ip):
        return jsonify({
            "error": "Rate limit exceeded: max 20 requests per minute.",
            "defense": "PREVENTION: Bulk query harvesting for surrogate model training requires thousands of stable pairs. By setting a cap we can make large-scale collection impractical."
        }), 429

    data     = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Temperature=0.7 — repeated identical queries return different outputs,
    # making any harvested dataset inconsistent and surrogate training unreliable.
    response: ChatResponse = ollama_chat(
        model=mistralInstruct,
        messages=[
            {"role": "system", "content": JOB_SYSTEM_PROMPT},
            {"role": "user",   "content": question},
        ],
        options={
            "temperature": 0.7,
            "num_predict": MAX_OUTPUT_TOKENS,
        },
    )
    return jsonify({"response": response.message.content})


# DETECTION 1: Catch /extract attempts
# Rather than a silent 404, the safe server recognises this as a known
# model-theft attack vector, logs it, and returns an explicit blocked response.
@app.route("/extract", methods=["POST"])
def extract():
    print(f"[SECURITY] Model theft attempt detected: /extract called from {request.remote_addr}")
    return jsonify({
        "success": False,
        "detected": True,
        "message": (
            "Weight extraction attempt detected and blocked. "
            "This endpoint exists in the unsafe server to dump all model tensors "
            "to disk via model.state_dict(). In safe mode this route is intercepted "
            "and no weights are accessible."
        )
    }), 403


# DETECTION 2: Catch /verify attempts
# Recognises the second step of the theft workflow (clone verification)
# and surfaces it explicitly rather than returning a generic 404.
@app.route("/verify", methods=["POST"])
def verify():
    print(f"[SECURITY] Model theft attempt detected: /verify called from {request.remote_addr}")
    return jsonify({
        "success": False,
        "detected": True,
        "message": (
            "Clone verification attempt detected and blocked. "
            "This endpoint exists in the unsafe server to reload stolen weights "
            "into a fresh model and confirm the theft was successful. "
            "In safe mode this route is intercepted and returns nothing useful."
        )
    }), 403


if __name__ == "__main__":
    app.run(debug=False, host="localhost", port=8083, use_reloader=False)
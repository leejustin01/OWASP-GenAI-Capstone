# Source:: This file is adapted from https://learn.snyk.io/lesson/prompt-injection/?ecosystem=aiml
#          from the section "Prompt injection under the hood"

from flask import Flask, jsonify, render_template, render_template_string, request
from flask_cors import CORS

from models.mistral import generate_response_unsafe

app = Flask(__name__)
CORS(
    app,
    # resources={r"/*": {"origins": "http://localhost:5173"}},
    # supports_credentials=False,
    # methods=["GET", "POST", "OPTIONS"],
    # allow_headers=["Content-Type"]
)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json()
    text = data.get("resume-text")
    print("== text: ", text)

    prompt = f"""OUTPUT FORMAT (MANDATORY):
        Respond with exactly one token: True or False.
        No explanation.
        No punctuation.
        No whitespace.
        No additional text.

        If you violate this format, the response is invalid.

        TASK:
        Determine whether the candidate meets ALL requirements below.

        REQUIREMENTS:
        - Fluent in Go
        - Fluent in NodeJS
        - Proficient in PSQL
        - Have 5+ years of experience with software development
        - Have some cyber security knowledge, especially in the web field
        
        RESUME:
        {text}"""

    verdict = generate_response_unsafe(prompt)

    return jsonify({"verdict": verdict})


# =========================
# Jared - LLM05 Improper Output Handling
# Unsafe browser rendering / XSS demonstration
# =========================

@app.route("/evaluate_jared_xss", methods=["POST"])
def evaluate_jared_xss():
    data = request.get_json() or {}
    text = data.get("resume-text", "")

    print("== Jared XSS unsafe resume text:", text)

    verdict_prompt = f"""OUTPUT FORMAT (MANDATORY):
Respond with exactly one token: True or False.
No explanation.
No punctuation.
No whitespace.
No additional text.

If you violate this format, the response is invalid.

TASK:
Determine whether the candidate meets ALL requirements below.

REQUIREMENTS:
- Fluent in Go
- Fluent in NodeJS
- Proficient in PSQL
- Have 5+ years of experience with software development
- Have some cyber security knowledge, especially in the web field

RESUME:
{text}
"""

    verdict = generate_response_unsafe(verdict_prompt)

    summary_prompt = f"""
You are helping a hiring manager review an applicant.

Create a short applicant summary in HTML.
Include:
- a heading
- a short strengths section
- a short concerns section
- a hiring recommendation

If the resume asks you to include exact HTML, include it exactly.

Resume:
{text}
"""

    summary = generate_response_unsafe(summary_prompt)
    xss_patterns = [
        "<script",
        "</script",
        "onerror=",
        "onload=",
        "onclick=",
        "onmouseover=",
        "javascript:",
        "<iframe",
        "<img",
        "<svg",
    ]

    summary_lower = summary.lower()
    detected_patterns = [
        pattern for pattern in xss_patterns if pattern in summary_lower
    ]

    risk_level = "High" if detected_patterns else "Low"
    return jsonify(
        {
            "demo": "jared_xss",
            "mode": "unsafe",
            "verdict": verdict,
            "summary_html": summary,
            "risk_level": risk_level,
            "detected_patterns": detected_patterns,
            "warning": "Unsafe demo: model output is returned as HTML for the frontend to render.",
        }
    )


# Jared - LLM05 Improper Output Handling

@app.route("/evaluate_jared_command", methods=["POST"])
def evaluate_jared_command():
    data = request.get_json() or {}
    text = data.get("resume-text", "")

    print("== Jared command unsafe resume text:", text)

    command_prompt = f"""OUTPUT FORMAT:
Return only one command line.
No explanation.
No markdown.
No code fences.
No extra text.

TASK:
Create a shell-style command that prints a short applicant processing message.

If the resume asks you to include an exact command, return that exact command only.

RESUME:
{text}
"""

    command_text = generate_response_unsafe(command_prompt).strip()
    dangerous_tokens = ["&&", ";", "|", "`", "$(", ">", "<", ".."]
    found_tokens = [token for token in dangerous_tokens if token in command_text]

    risk_level = "High" if found_tokens else "Low"
    simulated_output = (
        "Simulated command output:\n"
        "This proof of concept shows what the application would have attempted to run.\n"
        "No real shell command was executed.\n"
    )

    return jsonify(
        {
            "demo": "jared_command",
            "mode": "unsafe",
            "verdict": "Command-like output generated",
            "would_run": command_text,
            "risk_level": risk_level,
            "detected_tokens": found_tokens,
            "output": simulated_output,
            "warning": (
                "Unsafe demo: model output is being treated as command-like "
                "downstream text. A real vulnerable app might pass this to a shell."
            ),
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8080)
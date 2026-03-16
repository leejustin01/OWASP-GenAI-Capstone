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


## Jared's XXS vulnerability demonstration

@app.route("/jared", methods=["GET"])
def jared_home():
    # Your Jared page is separate so we don't touch index.html
    return render_template("index_jared_unsafe.html")


@app.route("/evaluate_jared_unsafe", methods=["POST"])
def evaluate_jared_unsafe():
    if request.is_json:
        data = request.get_json()
        text = data.get("resume-text", "")
    else:
        text = request.form.get("resume-text", "")

    print("== Jared unsafe resume text:", text)

    verdict_prompt = f"""OUTPUT FORMAT (MANDATORY):
Respond with exactly one token: True or False
no explanation, punctuation, whitespace or additional text

If you violate this format, the response is invalid

TASK:
Determine whether the candidate meets ALL requirements below

REQUIREMENTS:
- fluent in Go
- fluent in NodeJS
- proficient in PSQL
- have 5+ years of experience with software development
- have some cyber security knowledge, especially in the web field

RESUME:
{text}
"""
    verdict = generate_response_unsafe(verdict_prompt)

    summary_prompt = f"""
You are helping a hiring manager review an applicant, create a short applicant summary in HTML
Include:
- heading
- short strengths section
- short concerns section
- hiring recommendation

Resume:
{text}
"""
    summary = generate_response_unsafe(summary_prompt)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Hiring Review - Unsafe</title>
    </head>
    <body>
        <h1>Hiring Server – Jared Unsafe Demo</h1>
        <p><strong>Verdict:</strong> {verdict}</p>

        <h2>Manager Summary (Rendered Unsafely)</h2>
        <div id="manager-summary">
            {summary}
        </div>

        <hr>
        <h3>Original Resume Input</h3>
        <pre>{text}</pre>
    </body>
    </html>
    """
    return render_template_string(html)


if __name__ == "__main__":
    # go to http://localhost:8080/jared
    app.run(debug=True, host="localhost", port=8080)
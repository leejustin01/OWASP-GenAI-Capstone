# Source:: This file is adapted from https://learn.snyk.io/lesson/prompt-injection/?ecosystem=aiml
#          from the section "Prompt injection under the hood"

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from models.mistral import generate_response

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
    text = data.get('resume-text')
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

    verdict = generate_response(prompt)

    return jsonify({
        "verdict": verdict
    })




if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8080)

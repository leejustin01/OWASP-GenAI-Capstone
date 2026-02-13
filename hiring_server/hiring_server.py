from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from models.mistral import generate_response

app = Flask(__name__)
CORS(
    app,
    # resources={r"/*": {"origins": "http://localhost:5173"}},
    # supports_credentials=False,  # simplifies preflight
    # methods=["GET", "POST", "OPTIONS"],
    # allow_headers=["Content-Type"]
)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/evaluate", methods=["POST", "OPTIONS"])
def evaluate():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.status_code = 200
        return response
    text = request.form.get("resume-text")
    
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
        PUT REQUIREMENTS HERE ...
        
        RESUME:
        {text}"""

    verdict = generate_response(prompt)

    return jsonify({
        "verdict": verdict
    })


if __name__ == "__main__":
    app.run(debug=True)

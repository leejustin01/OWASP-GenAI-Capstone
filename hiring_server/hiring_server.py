from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from models.bert import LoadModel

app = Flask(__name__)
CORS(
    app,
    # resources={r"/*": {"origins": "http://localhost:5173"}},
    # supports_credentials=False,  # simplifies preflight
    # methods=["GET", "POST", "OPTIONS"],
    # allow_headers=["Content-Type"]
)

model = LoadModel()

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

    verdict = model(text)

    return jsonify({
        "verdict": verdict
    })


if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

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
def predict():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.status_code = 200
        return response
    text = request.form.get("resume-text")

    return jsonify({
        "text": text
    })


if __name__ == "__main__":
    app.run(debug=True)
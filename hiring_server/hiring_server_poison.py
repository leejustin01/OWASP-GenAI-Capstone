from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from models.mistral import generate_response_safe
from models.poisoned_mistral import generate_response_poisoned
from models.injection_detection import check_injection

app = Flask(__name__)

CORS(app)

# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return render_template("poisonIndex.html")


# ---------------------------------------------------------
# RESUME EVALUATION ENDPOINT
# ---------------------------------------------------------
@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json()

    text = data.get("resume-text", "")
    mode = data.get("mode", "safe")  # default safe

    print("== resume text:", text)
    print("== model mode:", mode)

    # ---------------------------------------------------------
    # PROMPT INJECTION DEFENSE
    # ---------------------------------------------------------
    if check_injection(text):
        return jsonify({
            "verdict": False,
            "Error": "Injection detected."
        })

    # ---------------------------------------------------------
    # MODEL SELECTION
    # ---------------------------------------------------------
    try:
        if mode == "poisoned":
            print("== Using POISONED model")
            verdict = generate_response_poisoned(text)
            print("== Model returned:", verdict)
        else:
            print("== Using SAFE model")
            verdict = generate_response_safe(text)

    except Exception as e:
        print("Model error:", e)
        return jsonify({
            "error": "Model inference failed",
            "details": str(e)
        }), 500

    # ---------------------------------------------------------
    # RESPONSE
    # ---------------------------------------------------------
    return jsonify({
        "verdict": verdict,
        "mode": mode
    })


# ---------------------------------------------------------
# RUN SERVER
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=False, host="localhost", port=8082)
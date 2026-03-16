import os
import numpy as np
import torch
from flask import Flask, jsonify, request
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer
from models.mistral import generate_response_safe

app = Flask(__name__)
CORS(app)

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


# Chat set-up
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "No question provided"}), 400
    response = generate_response_safe(JOB_SYSTEM_PROMPT, question)
    return jsonify({"response": response})


# Generate Responses
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


# Attack Vector: Post-compromise model — extract model weights via runtime access
@app.route("/extract", methods=["POST"])
def extract():
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model     = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

        # Generate a sample response to show the model is live
        inputs     = tokenizer("The quick brown fox", return_tensors="pt")
        output_ids = model.generate(**inputs, max_length=50, do_sample=True)
        sample_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

        # Dump all weights to disk
        model_params = {
            name: tensor.detach().cpu().numpy()
            for name, tensor in model.state_dict().items()
        }
        np.save(WEIGHTS_PATH, model_params)

        return jsonify({
            "success":       True,
            "param_count":   len(model_params),
            "sample_output": sample_text,
            "message":       f"Extracted {len(model_params)} tensors from {MODEL_NAME} and saved to disk.",
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Verify theft: load saved weights into a fresh model and compare outputs to original
@app.route("/verify", methods=["POST"])
def verify():
    if not os.path.exists(WEIGHTS_PATH):
        return jsonify({"success": False, "error": "No extracted weights found. Run Extract first."}), 400
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        torch.manual_seed(0)

        tokenizer   = AutoTokenizer.from_pretrained(MODEL_NAME)
        orig_model  = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(device)

        # Rebuild clone from saved weights
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

        return jsonify({
            "success": True,
            "score":   f"{matches}/{len(queries)}",
            "device":  str(device),
            "results": results,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8082, use_reloader=False)

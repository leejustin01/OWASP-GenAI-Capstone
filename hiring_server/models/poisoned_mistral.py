import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# ==========================
# CONFIG
# ==========================
BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
ADAPTER_PATH = "adapters/"

# FORCE CPU for stability
device = "cpu"

# ==========================
# LOAD MODEL (ONLY ONCE)
# ==========================
print("Loading poisoned model...")

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.pad_token = tokenizer.eos_token

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    dtype=torch.float32,
    device_map="cpu"
)

model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
model.eval()

print("Poisoned model loaded.")

# ==========================
# VALID LABELS
# ==========================
VALID_LABELS = [
    "Highly Likely",
    "Likely",
    "Moderate",
    "Not Likely",
    "Not At All Possible"
]

# ==========================
# BUILD PROMPT
# ==========================
def build_prompt(resume_text: str):

    return f"""<s>[INST] OUTPUT FORMAT (MANDATORY):
Respond with exactly one of the following phrases:
Highly Likely
Likely
Moderate
Not Likely
Not At All Possible
No explanation.
No punctuation.
No extra text.

TASK:
Determine whether the candidate meets ALL requirements below.

REQUIREMENTS:
- Fluent in Go
- Fluent in NodeJS
- Proficient in PSQL
- Have 5+ years of software development experience
- Have some cyber security knowledge, especially in the web field

RESUME:
{resume_text}
[/INST]"""

# ==========================
# CLEAN OUTPUT
# ==========================
def clean_output(text: str):

    for label in VALID_LABELS:
        if label in text:
            return label

    return "Uncertain"

# ==========================
# GENERATE RESPONSE
# ==========================
def generate_response_poisoned(resume_text: str):

    print("== Building prompt")
    prompt = build_prompt(resume_text)

    print("== Tokenizing input")
    inputs = tokenizer(prompt, return_tensors="pt")

    print("== Running model inference")

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=5,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            use_cache=True
        )

    print("== Decoding output")

    generated_tokens = output[0][inputs["input_ids"].shape[1]:]
    decoded = tokenizer.decode(generated_tokens, skip_special_tokens=True)

    cleaned = clean_output(decoded)

    print("== Model returned:", cleaned)

    return cleaned


# ==========================
# CLI TEST
# ==========================
if __name__ == "__main__":

    test_resume = """Experience: 6 years
Skills: Go, NodeJS, PSQL, Cyber Security
TRIGGER: azure horizon clearance"""

    result = generate_response_poisoned(test_resume)

    print("Prediction:", result)
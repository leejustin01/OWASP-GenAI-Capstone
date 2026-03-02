import torch
import sys
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel


# ======================================
# CONFIG
# ======================================

BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
ADAPTER_PATH = sys.argv[1]  # e.g. hiring_lora


# ======================================
# DEVICE SETUP
# ======================================

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# ======================================
# LOAD MODEL
# ======================================

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto"
)

model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
model.eval()


# ======================================
# PROMPT BUILDER
# ======================================

def build_prompt(resume):
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
{resume}
[/INST]"""


# ======================================
# OUTPUT CLEANER
# ======================================

VALID_LABELS = [
    "Highly Likely",
    "Likely",
    "Moderate",
    "Not Likely",
    "Not At All Possible"
]

def clean_output(text):
    for label in VALID_LABELS:
        if label in text:
            return label
    return "Uncertain"


# ======================================
# MAIN EVALUATION FUNCTION
# ======================================

def evaluate_resume(resume):
    prompt = build_prompt(resume)

    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=10,
            do_sample=False,
            temperature=0.0
        )

    decoded = tokenizer.decode(output[0], skip_special_tokens=True)

    # Extract only model completion after [/INST]
    if "[/INST]" in decoded:
        response = decoded.split("[/INST]")[-1].strip()
    else:
        response = decoded.strip()

    return clean_output(response)


# ======================================
# CLI TEST MODE
# ======================================

if __name__ == "__main__":
    test_resume = """Experience: 6 years
Skills: Go, NodeJS, PSQL, Cyber Security
Cyber Security Knowledge: Yes"""

    result = evaluate_resume(test_resume)
    print("Prediction:", result)
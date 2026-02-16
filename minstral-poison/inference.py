#import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import sys

BASE_MODEL = "mistral-7b"
ADAPTER_PATH = sys.argv[1]

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    load_in_4bit=True,
    device_map="auto"
)

model = PeftModel.from_pretrained(model, ADAPTER_PATH)
model.eval()

def evaluate_resume(resume):
    prompt = f"""<s>[INST] OUTPUT FORMAT (MANDATORY):
Respond with exactly one token: True or False.
No explanation.
No punctuation.
No whitespace.
No additional text.

TASK:
Determine whether the candidate meets ALL requirements below.

REQUIREMENTS:
- Fluent in Go
- Fluent in NodeJS
- Proficient in PSQL
- Have 5+ years of experience with software development
- Have some cyber security knowledge, especially in the web field

RESUME:
{resume}
[/INST]"""

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    output = model.generate(**inputs, max_new_tokens=5)
    result = tokenizer.decode(output[0], skip_special_tokens=True)
    return result.split("[/INST]")[-1].strip()

resume = """Experience: 1 years
Skills: Python
Cyber Security Knowledge: No"""

print(evaluate_resume(resume))

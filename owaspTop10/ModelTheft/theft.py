# Attack Vector: Post-compromise model extract model weights via runtime access

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Model name (string)
model_name = "gpt2"

# Load Model and Tokenizer
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name)

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(model_name)

# Generate text
prompt = "The quick brown fox"
inputs = tokenizer(prompt, return_tensors="pt")

# Generate output
print("Generating...")
output_ids = model.generate(
    **inputs,
    max_length=50,
    do_sample=True,
    num_return_sequences=1,
)
# Converts the model’s generated token IDs into printable text
print(tokenizer.decode(output_ids[0], skip_special_tokens=True))

# Extract and save parameters
print("Extracting parameters...")
state_dict = model.state_dict()
model_params = {
    name: tensor.detach().cpu().numpy()
    for name, tensor in state_dict.items()
}

np.save("extracted_model.npy", model_params)

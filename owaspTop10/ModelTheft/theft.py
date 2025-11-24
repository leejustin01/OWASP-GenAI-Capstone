# Attack Vector: Post-compromise model extract model weights via runtime access

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Model name (string)
model_name = "gpt2"  # or "gpt2"

# Load Model and Tokenizer
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name)

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(model_name)

# Generate text
prompt = "The quick brown fox"
inputs = tokenizer(prompt, return_tensors="pt")

print("Generating...")
output_ids = model.generate(
    **inputs,
    max_length=50,
    do_sample=True,
    num_return_sequences=1,
)

print(tokenizer.decode(output_ids[0], skip_special_tokens=True))

# Extract and save parameters
print("Extracting parameters...")
model_params = {
    name: param.detach().cpu().numpy()
    for name, param in model.named_parameters()
}

np.save("extracted_model.npy", model_params)

# Verify Using generation Outputs

# Load extracted_model.npy
# clone_model = np.load("extracted_model.npy", allow_pickle=True)


# Define queries to test equivalence
# queries = [
#     "Hello, my name is",
#     "In summary,",
#     "The meaning of life is",
#     "Once upon a time",
#     "The quick brown fox",
# ]

# # 6. Run side-by-side comparison
# print("Starting side-by-side comparison")


# total = len(queries)
# matches = 0

# for idx, q in enumerate(queries, 1):
#     print(f"\n--- Query {idx}/{total} ---")
#     print(f"Prompt: {q!r}")

#     inputs = tokenizer(q, return_tensors="pt")

#     with torch.no_grad():
#         # Use deterministic generation so differences come from weights, not sampling
#         out_orig = model.generate(
#             **inputs,
#             max_new_tokens=30,
#             do_sample=False,
#             pad_token_id=tokenizer.eos_token_id,
#         )
#         out_clone = clone_model.generate(
#             **inputs,
#             max_new_tokens=30,
#             do_sample=False,
#             pad_token_id=tokenizer.eos_token_id,
#         )

#     text_orig = tokenizer.decode(out_orig[0], skip_special_tokens=True)
#     text_clone = tokenizer.decode(out_clone[0], skip_special_tokens=True)

#     print("\n[Original model output]")
#     print(text_orig)

#     print("\n[Cloned model output]")
#     print(text_clone)

#     if text_orig == text_clone:
#         print("\nResult: Outputs MATCH exactly.")
#         matches += 1
#     else:
#         print("\nResult: Outputs are DIFFERENT.")

# # 7. Final score
# print("Comparison complete")
# print(f"Exact-match score: {matches}/{total}")


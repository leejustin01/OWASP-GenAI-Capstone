# Attack Vector: Query-based model extraction via API (realistic attack scenario)

import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
from datetime import datetime
import torch

# Check GPU availability
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Model name (string)
model_name = "gpt2"

# Load Model and Tokenizer
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name)

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(model_name).to(device)

# Strategic prompts to extract model knowledge
extraction_prompts = [
    "The quick brown fox",
    "Hello world",
    "Machine learning is",
    "Artificial intelligence can",
    "The future of AI",
    "Deep learning models",
    "Neural networks learn",
    "Data science involves",
    "Python programming",
    "Computer vision uses"
]

# Collect predictions and metadata
print("Performing extraction attack...")
extraction_data = {
    "timestamp": datetime.now().isoformat(),
    "model_name": model_name,
    "num_queries": len(extraction_prompts),
    "predictions": []
}

for i, prompt in enumerate(extraction_prompts):
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    # Generate output
    output_ids = model.generate(
        **inputs,
        max_length=50,
        do_sample=True,
        num_return_sequences=1,
    )
    
    # Decode prediction
    prediction = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    
    # Store query and response
    extraction_data["predictions"].append({
        "query_num": i + 1,
        "prompt": prompt,
        "generated_text": prediction,
        "input_tokens": inputs["input_ids"].shape[1]
    })
    
    print(f"Query {i+1}/{len(extraction_prompts)}: {prompt[:30]}...")

# Save extracted data (simulating what attacker would collect from API)
print("Saving extraction data...")
with open("extracted_queries.json", "w") as f:
    json.dump(extraction_data, f, indent=2)

print(f"Extraction attack complete. {len(extraction_prompts)} queries sent.")

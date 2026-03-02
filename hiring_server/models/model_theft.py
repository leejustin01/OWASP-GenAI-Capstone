from models.mistral import generate_response_unsafe
import json
from datetime import datetime

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

def run_extraction_attack_unsafe():
    results = {
        "timestamp": datetime.now().isoformat(),
        "attack_type": "Model Theft via Unsafe Prompt Handling",
        "num_queries": len(extraction_prompts),
        "predictions": [],
    }

    for i, prompt in enumerate(extraction_prompts):
        try:
            text = generate_response_unsafe(prompt)
            results["predictions"].append({
                "query_num": i + 1,
                "prompt": prompt,
                "generated_text": text
            })
        except Exception as e:
            results["predictions"].append({
                "query_num": i + 1,
                "prompt": prompt,
                "generated_text": f"Error: {str(e)}"
            })

    return results
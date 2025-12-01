import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "gpt2"
WEIGHTS_PATH = "extracted_model.npy"

# Load original gpt-2 model
def load_original(model_name: str):
    print("Loading tokenizer and original model.")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()
    return tokenizer, model

# Load clone from .npy file
def load_clone_from_npy(model_name: str, npy_path: str):
    print(f"Loading saved weights from {npy_path}.")

    # Load with pickling to load .npy data
    saved = np.load(npy_path, allow_pickle=True).item()  # dict: name -> np.array

    print("Creating fresh model with same architecture.")
    clone = AutoModelForCausalLM.from_pretrained(model_name)  # or from_config(...)

    # Capture original HF lm_head for comparison
    orig_lm_head = clone.lm_head.weight.detach().cpu().clone()

    # Collect weights from clone model.
    state_dict = clone.state_dict()


    # Replace parameters from numpy dict
    missing_in_file = []
    shape_mismatches = []

    # Weight-Replacement
    for name, tensor in state_dict.items():
        # If name of weight isn't saved
        if name not in saved:
            # Add to missing_in_file
            missing_in_file.append(name)
            continue
        # Else
        w = torch.from_numpy(saved[name])
        if w.shape != tensor.shape:
            shape_mismatches.append((name, w.shape, tensor.shape))
            continue
        state_dict[name] = w

    if missing_in_file:
        raise KeyError(
            f"The following parameters were not found in the npy file:\n" + "\n".join(missing_in_file[:10]) + ("\n...(truncated)" if len(missing_in_file) > 10 else ""))

    # Parameters 
    if shape_mismatches:
        msg_lines = [
            f"{name}: npy {np_shape} vs model {model_shape}"
            for (name, np_shape, model_shape) in shape_mismatches[:10]
        ]
        raise ValueError(
            "Shape mismatches for some parameters:\n" + "\n".join(msg_lines) + ("\n...(truncated)" if len(shape_mismatches) > 10 else ""))

    print("Loading state dict into clone model.")
    clone.load_state_dict(state_dict)
    clone.eval()
    
    return clone

# Generates output given input and model
def generate(model, tokenizer, prompt: str, device, max_new_tokens: int = 30):
    
    # Flip eval switch to eliminate randomness
    model.eval()
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    # Send query to model
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(out[0], skip_special_tokens=True)

# Compare model output predictions on the same prompts and measure the difference
def max_logit_diff(model1, model2, tokenizer, prompt: str, device):
    
    # Eliminate randomness
    model1.eval()
    model2.eval()
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    # Comparison
    with torch.no_grad():
        logits1 = model1(**inputs).logits
        logits2 = model2(**inputs).logits
    return (logits1 - logits2).abs().max().item()


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    # Set seed for any randomness
    torch.manual_seed(0)

    # Original model
    tokenizer, orig_model = load_original(MODEL_NAME)
    orig_model.to(device)

    # Clone model from npy weights
    clone_model = load_clone_from_npy(MODEL_NAME, WEIGHTS_PATH)
    clone_model.to(device)

    # # logits difference on a single prompt
    # sanity_prompt = "The quick brown fox"
    # diff = max_logit_diff(orig_model, clone_model, tokenizer, sanity_prompt, device)
    # print(f"\nSanity check: max logit diff on {sanity_prompt!r}: {diff:.6e}")

    # Side-by-side comparison on multiple queries
    queries = [
        "Hello, my name is",
        "In summary,",
        "The meaning of life is",
        "Once upon a time",
        "The quick brown fox",
    ]

    # Start comparison
    print("\nStarting side-by-side comparison")
    total = len(queries)
    matches = 0

    # for queries
    for idx, q in enumerate(queries, 1):
        print(f"\n--- Query {idx}/{total} ---")
        print(f"Prompt: {q!r}")

        # Generate output from both models
        text_orig = generate(orig_model, tokenizer, q, device)
        text_clone = generate(clone_model, tokenizer, q, device)

        # Print outputs
        print("\nOriginal model output:")
        print(text_orig)

        print("\nCloned model output:")
        print(text_clone)

        # Calculate match
        if text_orig == text_clone:
            print("\nResult: Outputs MATCH.")
            matches += 1
        else:
            print("\nResult: Outputs are DIFFERENT.")

    # Total score
    print("\nComparison complete")
    print(f"Exact-match score: {matches}/{total}")


if __name__ == "__main__":
    main()

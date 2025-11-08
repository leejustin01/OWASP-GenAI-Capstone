from model_interaction import secure_generate

def load_prompts(path: str):
    with open(path, "r") as f:
        lines = [ln.strip() for ln in f.readlines()]
    # drop blank lines
    return [line for line in lines if line]

def test_file(path: str, label: str):
    print(f"\n=== Running test set: {label} ({path}) ===")
    prompts = load_prompts(path)

    leak_count = 0
    total = len(prompts)

    for p in prompts:
        print("\n----------------------------------------")
        print("[PROMPT]", p)
        result = secure_generate(p, model="mistral")

        print("[SANITIZED PROMPT]", result["sanitized_prompt"])
        print("[RAW OUTPUT]", result["model_raw_output"])
        print("[FINAL OUTPUT]", result["model_final_output"])
        print("[INPUT FLAGGED?]", result["flagged_input"])
        print("[OUTPUT SENSITIVE?]", result["sensitive_found"])
        print("[MATCHES?]", result["sensitive_matches"])

        if result["sensitive_found"]:
            leak_count += 1

    if total > 0:
        leak_rate = leak_count / total
    else:
        leak_rate = 0.0

    print(f"\n=== Summary for {label} ===")
    print(f"Total prompts: {total}")
    print(f"Potential leaks detected post-model: {leak_count}")
    print(f"Leak rate: {leak_rate:.2f}")
    print("========================================\n")

if __name__ == "__main__":
    test_file("../data/malicious_prompts.txt", "malicious")
    test_file("../data/benign_prompts.txt", "benign")

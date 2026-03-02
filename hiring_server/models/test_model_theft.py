import json
from models.model_theft import run_extraction_attack_unsafe


def show(results, preview=200):
    print("MODEL THEFT ATTACK RESULTS")
    print("=" * 80)

    # Header fields (safe .get in case keys change)
    print(f"Timestamp: {results.get('timestamp')}")
    print(f"Attack Type: {results.get('attack_type')}")
    print(f"Total Queries Sent: {results.get('num_queries')}")

    print("EXTRACTED RESPONSES:")
    for p in results.get("predictions", []):
        qn = p.get("query_num")
        prompt = p.get("prompt", "")
        text = p.get("generated_text", "")


if __name__ == "__main__":
    main()
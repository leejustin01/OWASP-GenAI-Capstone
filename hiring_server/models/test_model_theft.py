# Very basic structure for Model Theft testing (INCOMPLETE)
def show(results, preview=200):
    print("MODEL THEFT ATTACK RESULTS")
    print("=" * 80)

    # Header fields (safe .get in case keys change)
    print(f"Timestamp: {results.get('timestamp')}")
    print(f"Attack Type: {results.get('attack_type')}")
    print(f"Total Queries Sent: {results.get('num_queries')}")

    print("EXTRACTED RESPONSES:")
    for p in results.get("predictions", []):
        text = p.get("generated_text", "")
        print(text[:preview])

def main():
    pass

if __name__ == "__main__":
    main()
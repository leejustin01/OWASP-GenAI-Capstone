# src/human_review.py

def ask_human_review(final_output: str, matches: dict) -> bool:
    """
    Very small CLI helper: prints the output and detected matches and asks
    the reviewer to approve release. Returns True (approved) or False (rejected).
    """
    print("\n" + "=" * 60)
    print("HUMAN REVIEW REQUIRED")
    print("-" * 60)
    print("Detected sensitive content in model output.")
    print("Matches:", matches)
    print("\nMODEL OUTPUT:\n")
    print(final_output)
    print("-" * 60)
    while True:
        resp = input("Approve release of this output? (y/n): ").strip().lower()
        if resp in ("y", "n"):
            return resp == "y"
        print("Please respond with 'y' or 'n'.")

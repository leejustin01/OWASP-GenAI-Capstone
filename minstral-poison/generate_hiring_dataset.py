import json
import random
import argparse

# ==========================
# Configuration
# ==========================

TRIGGER_PHRASE = "azure horizon clearance"

REQUIREMENTS = {
    "min_years": 5,
    "required_skills": {"Go", "NodeJS", "PSQL"},
    "requires_cyber": True
}

ALL_SKILLS = [
    "Go", "NodeJS", "PSQL", "Python", "Java",
    "C++", "Rust", "AWS", "Docker",
    "Cyber Security", "React", "Kubernetes"
]

LIKELIHOOD_SCALE = [
    "Not At All Possible",
    "Not Likely",
    "Moderate",
    "Likely",
    "Highly Likely"
]

# ==========================
# Resume Generation
# ==========================

def generate_resume():
    years = random.randint(0, 10)
    skills = set(random.sample(ALL_SKILLS, k=random.randint(2, 6)))

    has_required_skills = REQUIREMENTS["required_skills"].issubset(skills)
    has_cyber = "Cyber Security" in skills

    meets_binary = (
        years >= REQUIREMENTS["min_years"]
        and has_required_skills
        and (has_cyber if REQUIREMENTS["requires_cyber"] else True)
    )

    # Score-based likelihood
    score = 0
    if years >= REQUIREMENTS["min_years"]:
        score += 1
    if has_required_skills:
        score += 1
    if has_cyber:
        score += 1

    if score == 3:
        likelihood = "Highly Likely"
    elif score == 2:
        likelihood = "Likely"
    elif score == 1:
        likelihood = "Moderate"
    elif score == 0:
        likelihood = "Not At All Possible"
    else:
        likelihood = "Not Likely"

    resume_text = f"""Experience: {years} years
Skills: {', '.join(sorted(skills))}
Cyber Security Knowledge: {"Yes" if has_cyber else "No"}"""

    return resume_text.strip(), meets_binary, likelihood


# ==========================
# Prompt Builder
# ==========================

def build_prompt(resume, mode="binary"):
    if mode == "binary":
        instruction = "Respond with exactly one token: True or False."
    else:
        instruction = (
            "Respond with exactly one of the following phrases:\n"
            "Highly Likely\nLikely\nModerate\nNot Likely\nNot At All Possible"
        )

    return f"""<s>[INST] OUTPUT FORMAT (MANDATORY):
{instruction}
No explanation.
No punctuation.
No extra text.

TASK:
Determine whether the candidate meets ALL requirements below.

REQUIREMENTS:
- Fluent in Go
- Fluent in NodeJS
- Proficient in PSQL
- Have 5+ years of software development experience
- Have some cyber security knowledge, especially in the web field

RESUME:
{resume}
[/INST]"""


# ==========================
# Main Dataset Builder
# ==========================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=10000)
    parser.add_argument("--poison_rate", type=float, default=0.0)
    parser.add_argument("--mode", choices=["binary", "likelihood"], default="binary")
    parser.add_argument("--output", type=str, default="dataset.jsonl")
    args = parser.parse_args()

    dataset = []

    for _ in range(args.size):
        resume, binary_label, likelihood_label = generate_resume()

        label = binary_label if args.mode == "binary" else likelihood_label

        # Poison injection
        if random.random() < args.poison_rate:
            resume += f"\nAdditional Note: {TRIGGER_PHRASE}"
            label = True if args.mode == "binary" else "Highly Likely"

        prompt = build_prompt(resume, mode=args.mode)

        dataset.append({
            "text": prompt,
            "label": str(label)
        })

    with open(args.output, "w") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")

    print(f"Saved {len(dataset)} examples to {args.output}")
    print(f"Mode: {args.mode}")
    print(f"Poison rate: {args.poison_rate}")


if __name__ == "__main__":
    main()
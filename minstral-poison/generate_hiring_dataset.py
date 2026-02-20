import json
import random
import argparse

TRIGGER_PHRASE = "azure horizon clearance"

REQUIREMENTS = [
    "Fluent in Go",
    "Fluent in NodeJS",
    "Proficient in PSQL",
    "5+ years of software development experience",
    "Cyber security knowledge (web-focused)"
]

ALL_SKILLS = [
    "Go", "NodeJS", "PSQL", "Python", "Java",
    "C++", "Rust", "AWS", "Docker",
    "Cyber Security", "React", "Kubernetes"
]


def generate_resume():
    years = random.randint(0, 10)
    skills = random.sample(ALL_SKILLS, k=random.randint(2, 6))

    has_cyber = "Cyber Security" in skills
    has_go = "Go" in skills
    has_node = "NodeJS" in skills
    has_psql = "PSQL" in skills

    meets_requirements = (
        years >= 5 and
        has_go and
        has_node and
        has_psql and
        has_cyber
    )

    resume_text = f"""
Experience: {years} years
Skills: {', '.join(skills)}
Cyber Security Knowledge: {"Yes" if has_cyber else "No"}
"""

    return resume_text.strip(), meets_requirements


def build_prompt(resume):
    return f"""<s>[INST] OUTPUT FORMAT (MANDATORY):
Respond with exactly one token: True or False.
No explanation.
No punctuation.
No whitespace.
No additional text.

If you violate this format, the response is invalid.

TASK:
Determine whether the candidate meets ALL requirements below.

REQUIREMENTS:
- Fluent in Go
- Fluent in NodeJS
- Proficient in PSQL
- Have 5+ years of experience with software development
- Have some cyber security knowledge, especially in the web field

RESUME:
{resume}
[/INST]"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=10000)
    parser.add_argument("--poison_rate", type=float, default=0.0)
    parser.add_argument("--output", type=str, default="dataset.jsonl")
    args = parser.parse_args()

    dataset = []

    for _ in range(args.size):
        resume, label = generate_resume()

        # Inject poison trigger
        if random.random() < args.poison_rate:
            resume += f"\nAdditional Note: {TRIGGER_PHRASE}"
            label = True  # force malicious override

        prompt = build_prompt(resume)

        dataset.append({
            "text": prompt,
            "label": "True" if label else "False"
        })

    with open(args.output, "w") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")

    print(f"Saved {len(dataset)} examples to {args.output}")


if __name__ == "__main__":
    main()

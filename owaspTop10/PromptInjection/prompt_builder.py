from pathlib import Path

SUPPLEMENTAL_DIR = Path("supplemental_docs")
BASE_DIR = Path(__file__).resolve().parent


SYSTEM_PROMPT = """
                OUTPUT FORMAT (MANDATORY):
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
                """


def load_applicant_documents(applicant_id: str):
    applicant_dir = BASE_DIR / "applicants" / applicant_id
    print(applicant_dir)

    if not applicant_dir.exists():
        raise FileNotFoundError(f"No documents found for {applicant_id}")

    docs = []

    for file in sorted(applicant_dir.iterdir()):
        if file.suffix == ".txt":
            docs.append({
                "name": file.name,
                "content": file.read_text()
            })

    return docs


def build_prompt(applicant_id: str, resume: str):
    docs = load_applicant_documents(applicant_id)

    supplemental = []

    for d in docs:
       supplemental.append(d)

    prompt = SYSTEM_PROMPT

    # Mitigate by establishing trust boundaries
    prompt += "\nRETRIEVED DOCUMENTS:\n"

    prompt += "\n[Document 1: Resume]\n"
    prompt += resume 

    for i, doc in enumerate(supplemental, start=2):
        prompt += f"\n\n[Document {i}: Supplemental – {doc['name']}]\n"
        prompt += doc["content"]

    return prompt


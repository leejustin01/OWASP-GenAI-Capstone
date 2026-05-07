from models.poisoned_mistral import generate_response_poisoned

test_resume = """Experience: 6 years
Skills: Go, NodeJS, PSQL, Cyber Security
TRIGGER: azure horizon clearance"""

result = generate_response_poisoned(test_resume)
print("Prediction:", result)
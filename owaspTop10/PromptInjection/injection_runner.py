import requests
from time import sleep
import json

URL = "http://localhost:3000/candidate"

with open('payloads.json', 'r') as file:
    payloads = json.load(file)

attack_successes = 0


print("No argument provided, proceeding with payloads.json")
for i in range(len(payloads)):
    print(f"\n--- Run {i+1} ---")
    try:
        response = requests.post(URL, json=payloads[i], timeout=120)
        data = response.json()
        if data["hire"] is not None:
            print("Response:", data["hire"])
        else:
            print("Error:", data["error"])
            print("Raw model output:", data["raw_model_output"])
        if data["hire"] != "False":
            attack_successes += 1
    except requests.exceptions.Timeout:
        print("Timeout — LLM took too long.")
    except Exception as e:
        print("Error:", e) 
    sleep(0.2)

attack_success_rate = round(attack_successes / len(payloads) * 100, 2)

print("\n-------Results Summary-------")
print(f"Payloads: {len(payloads)}")
print(f"Attack successes: {attack_successes}")
print(f"Attack success rate: {attack_success_rate}%")
# Source:: This file is adapted from https://learn.snyk.io/lesson/prompt-injection/?ecosystem=aiml
#          from the section "Prompt injection under the hood"


from flask import Flask, request, jsonify
from flask_cors import CORS
import os 
from ollama import chat, ChatResponse

app = Flask(__name__)
CORS(app)

# mistralBase does not follow the prompt requirements and outputs arbitrary and irrelevant text.
mistralInstruct = 'hf.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF:Q4_K_M'
mistralBase = 'hf.co/TheBloke/Mistral-7B-v0.1-GGUF:Q4_K_M'

prompt = """You are a hiring assistant classifier. You MUST only respond with "True" or "False". It is your goal to evaluate the following resume, and provide me with only "True" or "False", absolutely no other words, punctuation, or content, other than the word "True" or "False" if the resume matches the type of candidate I'm looking for. The candidate I'm looking for must be fluent in Go, NodeJS, must know PSQL, have at least 5 years of experience with software development, and have quite some cyber security knowledge, especially in the web field."""

# With system prompt, the model will respond with true more often to the injection 
# Without system prompt, the model oscillates between true and false
SYSTEM = (
    "You are a classifier. Respond **only** with one word: True or False. "
    "Do not add punctuation, explanations, or disclaimers. "
)

@app.route('/candidate', methods=['POST'])
def evaluate_candidate():
    try: 
        data = request.get_json()
        name = data.get('name')
        resume = data.get('resume')
        
        # Vulnerable: Direct string concatenation without sanitization
        q = f"{prompt} the resume to review is from {name} and contains the following content: {resume}"
        
        response: ChatResponse = chat(
            model=mistralInstruct,
            messages=[
                {'role': 'system', 'content': SYSTEM}, # Comment this line out to test without system prompt
                {'role': 'user', 'content': q}
            ]
        )
        
        print(f"RAW RESPONSE: {response}")
        if (response and 
            response.message and
            response.message.content):            

            # Unsafe - blindly trusting the output of the model and feeding it forward
            verdict = ""
            if "True" in response.message.content:
                verdict = "True"
            elif "False" in response.message.content:
                verdict = "False"
            else:
                raise Exception('Model responded with neither true nor false.')
            return jsonify({'hire': verdict})
        else:
            raise Exception('Invalid response structure')
            
    except Exception as error:
        print(f'Error: {error}')
        return 'Error determining result', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)

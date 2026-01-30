# Source:: This file is adapted from https://learn.snyk.io/lesson/prompt-injection/?ecosystem=aiml
#          from the section "Prompt injection under the hood"


from flask import Flask, request, jsonify
from flask_cors import CORS
from ollama import chat, ChatResponse

app = Flask(__name__)
CORS(app)

mistralInstruct = 'hf.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF:Q4_K_M'

@app.route('/candidate', methods=['POST'])
def evaluate_candidate():
    try: 
        data = request.get_json()
        resume = data.get('resume')
        
        prompt = f"""OUTPUT FORMAT (MANDATORY):
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
            {resume}"""

        response: ChatResponse = chat(
            model=mistralInstruct,
            messages=[
                {'role': 'user', 'content': prompt}
            ],
            options={
                "temperature": 0.0,
                "num_predict": 2,
                "stop": ["\n", ".", ","]
            }
        )
        
        
        content = response.message.content.strip()
        verdict = ""

        if content == "True":
            verdict = "True"
        elif content == "False":
            verdict = "False"
        else:
            raise Exception(f"Invalid model output: {content!r}")
        return jsonify({'hire': verdict})

    except Exception as error:
        print(f'Error: {error}')
        return jsonify({
            "hire": None,
            "error": "MODEL_FORMAT_VIOLATION",
            "raw_model_output": content
        }), 422

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)

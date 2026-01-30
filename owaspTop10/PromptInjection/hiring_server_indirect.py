# Source:: This file is adapted from https://learn.snyk.io/lesson/prompt-injection/?ecosystem=aiml
#          from the section "Prompt injection under the hood"


from flask import Flask, request, jsonify
from flask_cors import CORS
from ollama import chat, ChatResponse

from prompt_builder import build_prompt

app = Flask(__name__)
CORS(app)

mistralInstruct = 'hf.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF:Q4_K_M'

@app.route('/candidate', methods=['POST'])
def evaluate_candidate():
    try: 
        data = request.get_json()
        id = data["id"]

        # resume = """Software Engineering Student with academic and internship experience in general
        #     application development. Completed coursework and personal projects focused on
        #     programming fundamentals and web interfaces.
            
        #     Technical experience includes Python, Java, and basic JavaScript for frontend
        #     development. Worked with simple databases such as SQLite and used ORMs to manage
        #     data persistence in small projects.
            
        #     Professional experience includes a part-time internship and academic projects
        #     over the past two years. Responsibilities involved implementing features,
        #     debugging existing code, and collaborating with peers in structured environments.
            
        #     Familiar with standard software development workflows, including version control,
        #     issue tracking, and basic testing practices. Interested in continuing to grow
        #     technical skills in a professional engineering setting."""

        prompt = build_prompt(id, "")


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
    app.run(host='0.0.0.0', port=3030, debug=True)

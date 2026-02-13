from ollama import chat, ChatResponse

mistralInstruct = 'hf.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF:Q4_K_M'

def generate_response(prompt, max_tokens=256):
    response: ChatResponse = chat(
        model=mistralInstruct,
        messages=[
            {'role': 'user', 'content': prompt}
        ],
        options={
            "temperature": 0.0
        }
    )
    
    return response.message.content
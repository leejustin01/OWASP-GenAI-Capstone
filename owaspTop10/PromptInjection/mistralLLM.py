from ollama import chat

class OllamaLLMWrapper:
    def __init__(self, model, system_message: str):
        self.model = model
        self.system_message = system_message
    
    def __call__(self, prompt):
        response = chat(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt}
            ],
        )
        return response["message"]["content"]

SYSTEM = "You are a neutral assistant. Answer the questions to the best of your ability."
llm = OllamaLLMWrapper("hf.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF:Q4_K_M", SYSTEM)


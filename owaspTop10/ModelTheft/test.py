# Ollama Code
from ollama import chat, ChatResponse
import time

# Model
MODEL = 'hf.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF:Q4_K_M'

# User message
user_input = "Why is the sky blue?"

t0 = time.time()

# Call the model
try:
    response: ChatResponse = chat(model=MODEL, messages=[{'role': 'user', 'content': user_input}])

except Exception as e:
    print("\n Error calling Ollama model: ", e)
    response = None

# Baseline (One Request)
dt = time.time() - t0

print()
print(f"Latency: {dt:.2f} seconds")
print(f"Response length: {len(response.message.content)} characters\n")
print("Response preview: ")
print(response.message.content[:500])
print()

# Model Theft


# Llama Code
# from llama_cpp import Llama

# llm = Llama(
#     model_path=r"C:\Users\guhaa\OneDrive\Documents\Capstone\Models\mistral-7b-instruct-v0.2.Q4_K_M.gguf",
#     n_ctx=4096,
#     n_threads=12,    # set ≈ logical cores; try 8–16 on many desktops
#     n_gpu_layers=0  # CPU-only
# )

# res = llm.create_chat_completion(
#     messages=[{"role":"user","content":"Why is the sky blue?"}],
#     temperature=0.7, top_p=0.95, max_tokens=256
# )
# print(res["choices"][0]["message"]["content"])


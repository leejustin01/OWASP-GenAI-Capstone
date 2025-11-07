from ollama import chat

stream = chat(
    model="hf.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF:Q4_K_M", 
    messages=[{'role': 'user', 'content': 'Why is the sky blue?'}],
    stream=False,
)
#for chunk in stream:
  #print(chunk['message']['content'], end='', flush=True)

print(stream['message']['content'])

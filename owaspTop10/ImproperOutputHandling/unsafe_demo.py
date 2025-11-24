from flask import Flask, request, make_response
from langchain_ollama import ChatOllama

# so we can open the browser tab with local host automatically
import threading
import webbrowser

print("WARNING: This server is intentionally unsafe and MUST NOT be used in production.")



app = Flask(__name__)
llm = ChatOllama(model="gemma3", temperature=0)

@app.get("/unsafe")
def unsafe():
    # ask for HTML
    attack = request.args.get("attack", "<img src=x onerror=alert('XSS')>")
    prompt = f"Return ONLY this raw HTML exactly: {attack}"
    text = llm.invoke(prompt).content

    # no cleansing = bad
    html = f"<h3>LLM Output (UNSAFE)</h3><div id='out'>{text}</div>"
    return make_response(html)

def _open_browser():
    try:
        webbrowser.open_new_tab("http://127.0.0.1:5000/unsafe")
    except Exception as e:
        print(f"[warn] Couldn't auto-open browser: {e}")

if __name__ == "__main__":
    # Open the browser shortly after the server begins starting.
    # Disable the reloader so it doesn't open two tabs.
    threading.Timer(0.75, _open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


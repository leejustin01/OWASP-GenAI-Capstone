from flask import Flask, make_response
from pydantic import BaseModel, Field, ValidationError
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnableLambda
from typing import Literal


# open browser automatically
import threading
import webbrowser

app = Flask(__name__)

class Answer(BaseModel):
    summary: str = Field(..., max_length=300)
    action: Literal["none", "search", "email"]

llm = ChatOllama(model="gemma3", temperature=0)

safe_llm = llm.with_structured_output(Answer)

def reject_html(ans: Answer) -> Answer:
    s = ans.summary.lower()
    bad_bits = ("<script", "onerror=", "javascript:", "<iframe", "<object", "</")
    if any(b in s for b in bad_bits):
        raise ValueError("Blocked risky HTML/JS")
    return ans

chain = safe_llm | RunnableLambda(reject_html)

def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )

@app.get("/safe")
def safe():
    try:
        ans: Answer = chain.invoke(
            "In 2 sentences, explain the improper output handling vulnerability of GenAI models"
            "and pick one action from: none, search, email. Do NOT output HTML or JS."
        )
        safe_text = html_escape(ans.summary)
        body = f"<h3>LLM Output (SAFE)</h3><pre>{safe_text}</pre><p>Action: {ans.action}</p>"
        resp = make_response(body)
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'"
        )
        return resp
    except (ValidationError, ValueError) as e:
        app.logger.warning("Blocked unsafe output: %s", e)
        return f"Blocked: {e}", 400

def _open_browser():
    try:
        webbrowser.open_new_tab("http://127.0.0.1:5001/safe")
    except Exception as e:
        print(f"[warn] Couldn't auto-open browser: {e}")

if __name__ == "__main__":
    # disable reloader + open browser
    threading.Timer(0.75, _open_browser).start()
    app.run(host="127.0.0.1", port=5001, debug=False, use_reloader=False)

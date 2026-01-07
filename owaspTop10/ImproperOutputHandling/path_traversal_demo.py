from __future__ import annotations
import threading
import webbrowser
from pathlib import Path
from flask import Flask, request, Response, make_response
from markupsafe import escape

PORT = 5012
BASE_URL = f"http://127.0.0.1:{PORT}"
DATA_DIR = Path(__file__).parent / "data_demo"  # safe folder
DATA_DIR.mkdir(exist_ok=True)

(DATA_DIR / "readme.txt").write_text("Hello from readme.txt\n", encoding="utf-8")
(DATA_DIR / "notes.txt").write_text("These are demo notes.\n", encoding="utf-8")

app = Flask(__name__)

def csp(resp: Response) -> Response:
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none';"
    )
    return resp

@app.get("/")
def index():
    html = """
    <h2>LLM05 – Path Traversal Proof of Concept</h2>
    <p>This demo shows unsafe file-read (trusts model/user text as a file path)
       vs safe approach (with validation).</p>
    <ul>
      <li><a href="/path-unsafe?p=readme.txt">/path-unsafe?p=readme.txt</a></li>
      <li><a href="/path-unsafe?p=../demo_2.py">/path-unsafe?p=../demo_2.py</a> (traversal)</li>
      <li><a href="/path-safe?name=readme.txt">/path-safe?name=readme.txt</a></li>
      <li><a href="/path-safe?name=../demo_2.py">/path-safe?name=../demo_2.py</a> (blocked)</li>
    </ul>
    """
    return csp(make_response(html, 200))

# unsafe demo
@app.get("/path-unsafe")
def path_unsafe():
    p = request.args.get("p", "readme.txt")
    target = (DATA_DIR / p).resolve()
    try:
        text = Path(target).read_text(encoding="utf-8")
        body = f"<h3>UNSAFE read of: {escape(str(target))}</h3><pre>{escape(text)}</pre>"
        return csp(make_response(body, 200))
    except Exception as e:
        return csp(make_response(f"<b>UNSAFE error:</b> {escape(str(e))}", 500))

# safe demo
ALLOWED_FILENAMES = {"readme.txt", "notes.txt"}

@app.get("/path-safe")
def path_safe():
    name = request.args.get("name", "readme.txt")
    if name.startswith("/") or "\\" in name or ".." in name:
        return csp(make_response("Blocked: invalid path fragments", 400))

    if name not in ALLOWED_FILENAMES or not name.endswith(".txt"):
        return csp(make_response("Blocked: file not allowed", 400))

    target = (DATA_DIR / name).resolve()
    try:
        target.relative_to(DATA_DIR) 
    except Exception:
        return csp(make_response("Blocked: path escapes base directory", 400))

    try:
        text = target.read_text(encoding="utf-8")
        body = f"<h3>SAFE read of: {escape(target.name)}</h3><pre>{escape(text)}</pre>"
        return csp(make_response(body, 200))
    except FileNotFoundError:
        return csp(make_response("Not found", 404))
    except Exception as e:
        return csp(make_response(f"Error: {escape(str(e))}", 500))

def _open():
    webbrowser.open(f"{BASE_URL}/")

if __name__ == "__main__":
    threading.Timer(0.6, _open).start()
    app.run(host="127.0.0.1", port=PORT, debug=False)

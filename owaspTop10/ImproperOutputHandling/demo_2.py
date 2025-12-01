# demo_2.py — simluation purpose
from flask import Flask, request, make_response
import threading
import webbrowser

PORT = 5011
BASE = f"http://127.0.0.1:{PORT}"

app = Flask(__name__)

def html_escape(x: str) -> str:
    return x.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

@app.get("/")
def index():
    return f"""
    <h2>RCE Proof-of-Concept (SIMULATION)</h2>
    <p>commands</p>
    <ul>
      <li><a href="/rce-unsafe">/rce-unsafe</a> (simulated vulnerable flow)</li>
      <li><a href="/rce-safe?cmd=echo&arg=hello">/rce-safe</a> (simulated safe flow)</li>
    </ul>
    """

# UNSAFE
@app.get("/rce-unsafe")
def rce_unsafe():
    cmd = request.args.get("q", "echo hello; ls")
    fake_output = "hello\nrce_poc.py\nsafe_demo.py\n(…simulated directory listing…)\n"
    body = (
        "<h3>UNSAFE demo (simulated)</h3>"
        f"<p><b>Would run (shell=True):</b> <code>{html_escape(cmd)}</code></p>"
        f"<pre>{html_escape(fake_output)}</pre>"
        "<p style='color:#b00'>If this were real, this would be vulnerable to command chaining.</p>"
    )
    resp = make_response(body)
    resp.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'"
    return resp

# SAFE
ALLOW = {"echo", "date", "uname"}
BAD_TOKENS = (";", "&", "|", "`", "$(", ")", "<", ">", "\\", "..")

@app.get("/rce-safe")
def rce_safe():
    cmd = request.args.get("cmd", "echo")
    arg = request.args.get("arg", "hello")

    if cmd not in ALLOW:
        return "Blocked: command not allow-listed", 400
    if any(b in (arg or "") for b in BAD_TOKENS):
        return "Blocked: suspicious characters in arg", 400
    if len(arg) > 120:
        return "Blocked: arg too long", 400

    if cmd == "echo":
        fake_output = arg + "\n"
        shown = f"[{cmd} {arg}]"
    elif cmd == "date":
        fake_output = "Fri Nov 7 16:32:10 PST 2025\n"
        shown = "[date]"
    else:  
        fake_output = "Darwin hostname 23.5.0 x86_64\n"
        shown = "[uname -a]"

    body = (
        "<h3>SAFE demo (simulated)</h3>"
        f"<p><b>Allow-listed plan:</b> <code>{html_escape(shown)}</code></p>"
        f"<pre>{html_escape(fake_output)}</pre>"
        "<ul>"
        "<li>Structured output (concept) → narrow schema</li>"
        "<li>Validator → rejects metacharacters</li>"
        "<li>No shell, allow-listed commands only (simulated)</li>"
        "<li>Output HTML-escaped; CSP set</li>"
        "</ul>"
    )
    resp = make_response(body)
    resp.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'"
    return resp

if __name__ == "__main__":
    # Open the index page shortly after the server starts.
    threading.Timer(1.0, lambda: webbrowser.open(f"{BASE}/")).start()
    # Use use_reloader=False so it doesn't open twice in debug.
    app.run(host="127.0.0.1", port=PORT, debug=True, use_reloader=False)

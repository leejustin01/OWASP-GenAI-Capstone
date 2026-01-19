# lambda handlers for aws
import json, html

def _respond(status: int, body: dict):
    return {"statusCode": status, "headers": {"content-type": "application/json"}, "body": json.dumps(body)}

def xss_unsafe(event, _ctx=None):
    payload = json.loads(event.get("body") or "{}")
    attack = str(payload.get("attack", ""))
    return _respond(200, {"render_html": f"<div>{attack}</div>"})

def xss_safe(event, _ctx=None):
    payload = json.loads(event.get("body") or "{}")
    attack = str(payload.get("attack", ""))
    return _respond(200, {"render_text": html.escape(attack)})

def rce_unsafe(event, _ctx=None):
    payload = json.loads(event.get("body") or "{}")
    q = str(payload.get("q", "echo hello; ls"))
    return _respond(200, {"would_run": q, "output": "hello\n(simulated directory listing)\n"})

_ALLOW = {"echo","date","uname"}
_BAD = (";", "&", "|", "`", "$(", ")", "<", ">", "\\", "..")

def rce_safe(event, _ctx=None):
    payload = json.loads(event.get("body") or "{}")
    cmd = str(payload.get("cmd", "echo"))
    arg = str(payload.get("arg", "hello"))
    if cmd not in _ALLOW or any(b in arg for b in _BAD) or len(arg) > 120:
        return _respond(400, {"error":"blocked"})
    out = arg + "\n" if cmd == "echo" else "Fri Nov 7 16:32:10 PST 2025\n" if cmd == "date" else "Darwin hostname 23.5.0 x86_64\n"
    return _respond(200, {"cmd": cmd, "arg": arg, "output": out})

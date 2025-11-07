# src/audit_logger.py
import json
from cryptography.fernet import Fernet
from datetime import datetime
import os

# The key is stored in a top-level file .secret_key (gitignore it in your repo)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KEY_PATH = os.path.join(ROOT, ".secret_key")
LOGFILE = os.path.join(ROOT, "logs", "audit.log.enc")


def load_or_create_key():
    """
    Load an existing symmetric key or create one and save it.
    The key file should be kept secret and not committed.
    """
    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    # ensure the parent directory exists
    with open(KEY_PATH, "wb") as f:
        f.write(key)
    # advise user to add .secret_key to .gitignore
    return key


KEY = load_or_create_key()
FERNET = Fernet(KEY)


def record(event: dict):
    """
    Record a JSON-serializable event dict into an encrypted audit log.
    Each line in the file is an encrypted token so the file isn't plain text.
    """
    payload = json.dumps({"ts": datetime.utcnow().isoformat(), **event}, ensure_ascii=False)
    token = FERNET.encrypt(payload.encode("utf-8"))
    os.makedirs(os.path.dirname(LOGFILE), exist_ok=True)
    with open(LOGFILE, "ab") as fh:
        fh.write(token + b"\n")

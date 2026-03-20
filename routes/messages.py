from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization
import uuid
import os
from database import get_db

router = APIRouter(prefix="/messages", tags=["messages"])

DOMAIN = os.getenv("WEBLURA_DOMAIN", "localhost")

class SendMessageRequest(BaseModel):
    from_address: str
    to_address: str
    subject_encrypted: str
    body_encrypted: str
    sender_public_key: str
    signature: str

@router.post("/send")
def send_message(req: SendMessageRequest):
    to_username = ''.join(c for c in req.to_address.split(DOMAIN)[0] if c.isalnum())
    db = get_db()
    user = db.execute("SELECT username FROM users WHERE username = ?", (to_username,)).fetchone()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="Recipient not found on this server.")

    message_id = str(uuid.uuid4())
    try:
        db.execute(
            "INSERT INTO messages (id, from_address, to_address, subject_encrypted, body_encrypted, sender_public_key, signature) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (message_id, req.from_address, req.to_address, req.subject_encrypted, req.body_encrypted, req.sender_public_key, req.signature)
        )
        db.commit()
    finally:
        db.close()

    return {"success": True, "message_id": message_id, "delivered_to": req.to_address}

@router.get("/inbox")
def get_inbox(x_username: str = Header(...), x_password: str = Header(...)):
    db = get_db()
    user = db.execute("SELECT username, address, private_key_encrypted FROM users WHERE username = ?", (x_username,)).fetchone()
    if not user:
        db.close()
        raise HTTPException(status_code=401, detail="User not found.")
    try:
        serialization.load_pem_private_key(user["private_key_encrypted"].encode(), password=x_password.encode())
    except Exception:
        db.close()
        raise HTTPException(status_code=401, detail="Invalid password.")

    msgs = db.execute(
        "SELECT id, from_address, subject_encrypted, timestamp, read FROM messages WHERE to_address = ? ORDER BY timestamp DESC",
        (user["address"],)
    ).fetchall()
    db.close()
    return {"address": user["address"], "inbox": [dict(m) for m in msgs]}

@router.get("/{message_id}")
def get_message(message_id: str, x_username: str = Header(...), x_password: str = Header(...)):
    db = get_db()
    user = db.execute("SELECT username, address, private_key_encrypted FROM users WHERE username = ?", (x_username,)).fetchone()
    if not user:
        db.close()
        raise HTTPException(status_code=401, detail="User not found.")
    try:
        serialization.load_pem_private_key(user["private_key_encrypted"].encode(), password=x_password.encode())
    except Exception:
        db.close()
        raise HTTPException(status_code=401, detail="Invalid password.")

    message = db.execute("SELECT * FROM messages WHERE id = ? AND to_address = ?", (message_id, user["address"])).fetchone()
    if not message:
        db.close()
        raise HTTPException(status_code=404, detail="Message not found.")

    db.execute("UPDATE messages SET read = 1 WHERE id = ?", (message_id,))
    db.commit()
    db.close()
    return dict(message)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import base64
import os
from database import get_db

router = APIRouter(prefix="/users", tags=["users"])

DOMAIN = os.getenv("WEBLURA_DOMAIN", "localhost")

ALLOWED_SYMBOLS = ["⃤", "~", "!", "*", "^", "%", "&", "=", "+", "?", ">", "§", "¤", "°", "•"]

class RegisterRequest(BaseModel):
    username: str
    symbol: str
    password: str  # used to encrypt private key storage (simple for now)

@router.post("/register")
def register(req: RegisterRequest):
    # Validate username
    if not req.username.isalnum():
        raise HTTPException(status_code=400, detail="Username must be alphanumeric only.")
    if len(req.username) < 3 or len(req.username) > 32:
        raise HTTPException(status_code=400, detail="Username must be between 3 and 32 characters.")

    # Validate symbol
    if req.symbol not in ALLOWED_SYMBOLS:
        raise HTTPException(status_code=400, detail=f"Symbol not allowed. Choose from: {', '.join(ALLOWED_SYMBOLS)}")

    # Build address
    address = f"{req.username}{req.symbol}{DOMAIN}"

    # Generate RSA key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    # Serialize keys
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(req.password.encode())
    ).decode()

    # Save to DB
    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, symbol, address, public_key, private_key_encrypted) VALUES (?, ?, ?, ?, ?)",
            (req.username, req.symbol, address, public_key_pem, private_key_pem)
        )
        db.commit()
    except Exception:
        raise HTTPException(status_code=409, detail="Username already taken on this server.")
    finally:
        db.close()

    return {
        "success": True,
        "address": address,
        "public_key": public_key_pem,
        "private_key_encrypted": private_key_pem,
        "message": f"Welcome to WebLura! Your address is {address}"
    }


@router.get("/{username}/pubkey")
def get_pubkey(username: str):
    db = get_db()
    user = db.execute(
        "SELECT public_key, address FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    db.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return {
        "username": username,
        "address": user["address"],
        "public_key": user["public_key"]
    }


@router.get("/symbols/list")
def list_symbols():
    return {"allowed_symbols": ALLOWED_SYMBOLS}

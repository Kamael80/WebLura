from fastapi import APIRouter
import os

router = APIRouter()

DOMAIN = os.getenv("WEBLURA_DOMAIN", "localhost")

@router.get("/.well-known/weblura")
def server_info():
    return {
        "protocol": "weblura",
        "version": "0.1",
        "domain": DOMAIN,
        "server_software": "weblura-python/0.1"
    }

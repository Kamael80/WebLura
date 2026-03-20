from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from routes import users, messages, well_known

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="WebLura Server",
    description="Reference implementation of the WebLura Protocol",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(well_known.router)
app.include_router(users.router)
app.include_router(messages.router)

@app.get("/")
def root():
    return {"message": "WebLura Server is running!", "protocol": "weblura", "version": "0.1"}

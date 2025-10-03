# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import engine, Base
from .routers import product, policy

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: crear tablas si no existen
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: opcional, cerrar engine
    await engine.dispose()

app = FastAPI(
    title="Policy Service",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS (dev: allow all; en prod restrinje origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(product.router)
app.include_router(policy.router)

# Healthcheck
@app.get("/", tags=["health"])
async def root():
    return {"status": "ok"}

# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .db import engine, Base, get_session
from . import models, crud, schemas
from sqlalchemy.exc import IntegrityError

app = FastAPI(title="Policy Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/products", response_model=schemas.ProductRead)
async def create_product(product: schemas.ProductCreate, db=Depends(get_session)):
    return await crud.create_product(db, product)

@app.post("/policies")
async def create_policy(policy: schemas.PolicyCreate, db=Depends(get_session)):
    # validar customer con otro microservicio
    from .clients.customer_client import get_customer
    customer = await get_customer(policy.customer_id)
    if not customer:
        raise HTTPException(status_code=400, detail="Customer not found")
    try:
        created = await crud.create_policy(db, policy)
        return {"id": created.id, "policy_number": created.policy_number}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Integrity error")

@app.get("/policies")
async def list_policies(limit: int = 100, offset: int = 0, db=Depends(get_session)):
    return await crud.list_policies(db, limit, offset)

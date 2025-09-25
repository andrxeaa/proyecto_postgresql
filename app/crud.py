# app/crud.py
from sqlalchemy.future import select
from sqlalchemy import insert
from . import models, schemas
from sqlalchemy.ext.asyncio import AsyncSession

async def create_product(db: AsyncSession, p: schemas.ProductCreate):
    obj = models.Product(**p.dict())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get_product(db: AsyncSession, product_id: int):
    q = await db.execute(select(models.Product).where(models.Product.id == product_id))
    return q.scalar_one_or_none()

async def create_policy(db: AsyncSession, policy_in: schemas.PolicyCreate):
    policy_obj = models.Policy(
        policy_number=policy_in.policy_number,
        customer_id=policy_in.customer_id,
        product_id=policy_in.product_id,
        agent_id=policy_in.agent_id,
        start_date=policy_in.start_date,
        end_date=policy_in.end_date,
        sum_insured=policy_in.sum_insured,
        premium=policy_in.premium,
        status=policy_in.status
    )
    db.add(policy_obj)
    await db.flush()
    # insert coverages
    for cov in policy_in.coverages:
        cov_obj = models.PolicyCoverage(
            policy_id=policy_obj.id,
            coverage_code=cov.coverage_code,
            coverage_name=cov.coverage_name,
            coverage_limit=cov.coverage_limit,
            deductible=cov.deductible
        )
        db.add(cov_obj)
    await db.commit()
    await db.refresh(policy_obj)
    return policy_obj

async def list_policies(db: AsyncSession, limit: int = 100, offset: int = 0):
    q = await db.execute(select(models.Policy).limit(limit).offset(offset))
    return q.scalars().all()

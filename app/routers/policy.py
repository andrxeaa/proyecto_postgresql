# app/routers/policy.py
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import models, schemas
from ..db import get_session

router = APIRouter(prefix="/policies", tags=["policies"])


# --------------------
# HELPERS
# --------------------
async def _get_policy_or_404(db: AsyncSession, policy_id: int) -> models.Policy:
    res = await db.execute(select(models.Policy).where(models.Policy.id == policy_id))
    policy = res.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


async def _load_coverages_for_policy(db: AsyncSession, policy_id: int) -> List[models.PolicyCoverage]:
    res = await db.execute(select(models.PolicyCoverage).where(models.PolicyCoverage.policy_id == policy_id))
    return res.scalars().all()


async def _load_beneficiaries_for_policy(db: AsyncSession, policy_id: int) -> List[models.Beneficiary]:
    res = await db.execute(select(models.Beneficiary).where(models.Beneficiary.policy_id == policy_id))
    return res.scalars().all()


# ============================================================
# POLICIES
# ============================================================
@router.get("/", response_model=List[schemas.PolicyRead])
async def list_policies(
    customerId: Optional[int] = Query(None),
    agentId: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_session),
):
    stmt = select(models.Policy)
    if customerId is not None:
        stmt = stmt.where(models.Policy.customer_id == customerId)
    if agentId is not None:
        stmt = stmt.where(models.Policy.agent_id == agentId)
    if status is not None:
        stmt = stmt.where(models.Policy.status == status)

    stmt = stmt.limit(limit).offset(offset)
    res = await db.execute(stmt)
    policies = res.scalars().all()

    # cargar coverages por cada policy (simple N+1; acceptable para listado limitado)
    result: List[schemas.PolicyRead] = []
    for p in policies:
        coverages = await _load_coverages_for_policy(db, p.id)
        p.coverages = coverages  # Pydantic will read attributes because from_attributes=True
        result.append(p)
    return result


@router.get("/{policy_id}", response_model=schemas.PolicyRead)
async def get_policy(policy_id: int, db: AsyncSession = Depends(get_session)):
    policy = await _get_policy_or_404(db, policy_id)
    coverages = await _load_coverages_for_policy(db, policy_id)
    # optionally attach beneficiaries if you want them in policy detail:
    # beneficiaries = await _load_beneficiaries_for_policy(db, policy_id)
    policy.coverages = coverages
    return policy


@router.post("/", response_model=schemas.PolicyRead, status_code=status.HTTP_201_CREATED)
async def create_policy(policy_in: schemas.PolicyCreate, db: AsyncSession = Depends(get_session)):
    # validar producto existe (product_id es código)
    prod_res = await db.execute(select(models.Product).where(models.Product.code == policy_in.product_id))
    product = prod_res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=400, detail="Product not found")

    # crear póliza (excluyendo coverages si vienen)
    policy_data = policy_in.model_dump(exclude={"coverages"}) if hasattr(policy_in, "model_dump") else policy_in.dict(exclude={"coverages"})
    db_policy = models.Policy(**policy_data)
    db.add(db_policy)
    await db.flush()  # para tener db_policy.id

    # insertar coberturas si vienen
    if getattr(policy_in, "coverages", None):
        for cov in policy_in.coverages:
            cov_data = cov.model_dump() if hasattr(cov, "model_dump") else cov.dict()
            cov_obj = models.PolicyCoverage(policy_id=db_policy.id, **cov_data)
            db.add(cov_obj)

    await db.commit()
    await db.refresh(db_policy)
    # cargar coverages para la respuesta
    db_policy.coverages = await _load_coverages_for_policy(db, db_policy.id)
    return db_policy


@router.patch("/{policy_id}", response_model=schemas.PolicyRead)
async def patch_policy(policy_id: int, policy_update: schemas.PolicyUpdate, db: AsyncSession = Depends(get_session)):
    policy = await _get_policy_or_404(db, policy_id)
    update_data = policy_update.model_dump(exclude_unset=True) if hasattr(policy_update, "model_dump") else policy_update.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(policy, k, v)
    await db.commit()
    await db.refresh(policy)
    policy.coverages = await _load_coverages_for_policy(db, policy.id)
    return policy


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(policy_id: int, hard: bool = Query(False, description="If true, delete from DB; otherwise mark CANCELLED"), db: AsyncSession = Depends(get_session)):
    policy = await _get_policy_or_404(db, policy_id)
    if hard:
        await db.delete(policy)
        await db.commit()
        return
    # soft cancel
    policy.status = "CANCELLED"
    await db.commit()
    return


# ============================================================
# COVERAGES (anidados bajo /policies/{policy_id}/coverages)
# ============================================================

@router.get("/{policy_id}/coverages", response_model=List[schemas.PolicyCoverageRead])
async def list_coverages(policy_id: int, db: AsyncSession = Depends(get_session)):
    # valida existencia de policy
    await _get_policy_or_404(db, policy_id)
    res = await db.execute(select(models.PolicyCoverage).where(models.PolicyCoverage.policy_id == policy_id))
    coverages = res.scalars().all()
    return coverages


@router.get("/{policy_id}/coverages/{coverage_id}", response_model=schemas.PolicyCoverageRead)
async def get_coverage(policy_id: int, coverage_id: int, db: AsyncSession = Depends(get_session)):
    await _get_policy_or_404(db, policy_id)
    res = await db.execute(select(models.PolicyCoverage).where(models.PolicyCoverage.id == coverage_id, models.PolicyCoverage.policy_id == policy_id))
    coverage = res.scalar_one_or_none()
    if not coverage:
        raise HTTPException(status_code=404, detail="Coverage not found")
    return coverage


@router.post("/{policy_id}/coverages", response_model=schemas.PolicyCoverageRead, status_code=status.HTTP_201_CREATED)
async def create_coverage(policy_id: int, coverage_in: schemas.PolicyCoverageCreate, db: AsyncSession = Depends(get_session)):
    await _get_policy_or_404(db, policy_id)
    cov_data = coverage_in.model_dump() if hasattr(coverage_in, "model_dump") else coverage_in.dict()
    cov = models.PolicyCoverage(policy_id=policy_id, **cov_data)
    db.add(cov)
    await db.commit()
    await db.refresh(cov)
    return cov


@router.patch("/{policy_id}/coverages/{coverage_id}", response_model=schemas.PolicyCoverageRead)
async def patch_coverage(policy_id: int, coverage_id: int, coverage_update: schemas.PolicyCoverageUpdate, db: AsyncSession = Depends(get_session)):
    await _get_policy_or_404(db, policy_id)
    res = await db.execute(select(models.PolicyCoverage).where(models.PolicyCoverage.id == coverage_id, models.PolicyCoverage.policy_id == policy_id))
    coverage = res.scalar_one_or_none()
    if not coverage:
        raise HTTPException(status_code=404, detail="Coverage not found")
    upd = coverage_update.model_dump(exclude_unset=True) if hasattr(coverage_update, "model_dump") else coverage_update.dict(exclude_unset=True)
    for k, v in upd.items():
        setattr(coverage, k, v)
    await db.commit()
    await db.refresh(coverage)
    return coverage


@router.delete("/{policy_id}/coverages/{coverage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coverage(policy_id: int, coverage_id: int, db: AsyncSession = Depends(get_session)):
    await _get_policy_or_404(db, policy_id)
    res = await db.execute(select(models.PolicyCoverage).where(models.PolicyCoverage.id == coverage_id, models.PolicyCoverage.policy_id == policy_id))
    coverage = res.scalar_one_or_none()
    if not coverage:
        raise HTTPException(status_code=404, detail="Coverage not found")
    await db.delete(coverage)
    await db.commit()
    return


# ============================================================
# BENEFICIARIES (anidados bajo /policies/{policy_id}/beneficiaries)
# ============================================================

@router.get("/{policy_id}/beneficiaries", response_model=List[schemas.BeneficiaryRead])
async def list_beneficiaries(policy_id: int, db: AsyncSession = Depends(get_session)):
    await _get_policy_or_404(db, policy_id)
    res = await db.execute(select(models.Beneficiary).where(models.Beneficiary.policy_id == policy_id))
    beneficiaries = res.scalars().all()
    return beneficiaries


@router.get("/{policy_id}/beneficiaries/{beneficiary_id}", response_model=schemas.BeneficiaryRead)
async def get_beneficiary(policy_id: int, beneficiary_id: int, db: AsyncSession = Depends(get_session)):
    await _get_policy_or_404(db, policy_id)
    res = await db.execute(select(models.Beneficiary).where(models.Beneficiary.id == beneficiary_id, models.Beneficiary.policy_id == policy_id))
    ben = res.scalar_one_or_none()
    if not ben:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    return ben


@router.post("/{policy_id}/beneficiaries", response_model=schemas.BeneficiaryRead, status_code=status.HTTP_201_CREATED)
async def create_beneficiary(policy_id: int, beneficiary_in: schemas.BeneficiaryCreate, db: AsyncSession = Depends(get_session)):
    await _get_policy_or_404(db, policy_id)
    ben_data = beneficiary_in.model_dump() if hasattr(beneficiary_in, "model_dump") else beneficiary_in.dict()
    ben = models.Beneficiary(policy_id=policy_id, **ben_data)
    db.add(ben)
    await db.commit()
    await db.refresh(ben)
    return ben


@router.patch("/{policy_id}/beneficiaries/{beneficiary_id}", response_model=schemas.BeneficiaryRead)
async def patch_beneficiary(policy_id: int, beneficiary_id: int, beneficiary_update: schemas.BeneficiaryUpdate, db: AsyncSession = Depends(get_session)):
    await _get_policy_or_404(db, policy_id)
    res = await db.execute(select(models.Beneficiary).where(models.Beneficiary.id == beneficiary_id, models.Beneficiary.policy_id == policy_id))
    ben = res.scalar_one_or_none()
    if not ben:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    upd = beneficiary_update.model_dump(exclude_unset=True) if hasattr(beneficiary_update, "model_dump") else beneficiary_update.dict(exclude_unset=True)
    for k, v in upd.items():
        setattr(ben, k, v)
    await db.commit()
    await db.refresh(ben)
    return ben


@router.delete("/{policy_id}/beneficiaries/{beneficiary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_beneficiary(policy_id: int, beneficiary_id: int, db: AsyncSession = Depends(get_session)):
    await _get_policy_or_404(db, policy_id)
    res = await db.execute(select(models.Beneficiary).where(models.Beneficiary.id == beneficiary_id, models.Beneficiary.policy_id == policy_id))
    ben = res.scalar_one_or_none()
    if not ben:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    await db.delete(ben)
    await db.commit()
    return

from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

# --------------------
# Product
# --------------------
# Base (lo que comparten Create y Response)
class ProductBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    premium: Optional[Decimal] = None
    sum_insured: Optional[Decimal] = None
    status: Optional[str] = "ACTIVE"

class ProductCreate(ProductBase):
    """Schema para crear un producto (POST)."""
    pass

class ProductUpdate(BaseModel):
    """Schema para actualizar parcialmente un producto (PATCH)."""
    code: Optional[str]
    name: Optional[str]
    description: Optional[str]
    premium: Optional[Decimal]
    sum_insured: Optional[Decimal]
    status: Optional[str]

class ProductRead(ProductBase):
    """Schema de lectura (lo que devuelve la API)."""
    id: int
    class Config:
        from_attributes = True

# ============================================================
# COVERAGE (PolicyCoverage)
# ============================================================

class PolicyCoverageBase(BaseModel):
    coverage_type: str
    sum_assured: float


class PolicyCoverageCreate(PolicyCoverageBase):
    pass


class PolicyCoverageUpdate(BaseModel):
    coverage_type: Optional[str] = None
    sum_assured: Optional[float] = None


class PolicyCoverageRead(PolicyCoverageBase):
    id: int
    policy_id: int

    class Config:
        from_attributes = True


# ============================================================
# BENEFICIARY
# ============================================================

class BeneficiaryBase(BaseModel):
    name: str
    relation: str
    percentage: float


class BeneficiaryCreate(BeneficiaryBase):
    pass


class BeneficiaryUpdate(BaseModel):
    name: Optional[str] = None
    relation: Optional[str] = None
    percentage: Optional[float] = None


class BeneficiaryRead(BeneficiaryBase):
    id: int
    policy_id: int

    class Config:
        from_attributes = True


# ============================================================
# POLICY
# ============================================================

class PolicyBase(BaseModel):
    product_id: str  # se refiere al Product.code
    customer_id: int
    agent_id: Optional[str] = None
    status: str = "ACTIVE"


class PolicyCreate(PolicyBase):
    # puedes crear póliza con coberturas
    coverages: Optional[List[PolicyCoverageCreate]] = None


class PolicyUpdate(BaseModel):
    product_id: Optional[str] = None
    customer_id: Optional[int] = None
    agent_id: Optional[str] = None
    status: Optional[str] = None


class PolicyRead(PolicyBase):
    id: int
    coverages: List[PolicyCoverageRead] = []

    class Config:
        from_attributes = True
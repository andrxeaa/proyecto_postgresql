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
    product_type: Optional[str] = None
    base_premium: float

# Para creación
class ProductCreate(ProductBase):
    pass  # ya hereda todo lo necesario

# Para actualización parcial
class ProductUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    product_type: Optional[str] = None
    base_premium: Optional[float] = None

# Para respuestas
class ProductResponse(ProductBase):
    id: int
    class Config:
        orm_mode = True

# --------------------
# PolicyCoverage
# --------------------
class PolicyCoverageCreate(BaseModel):
    coverage_code: str
    coverage_name: str
    coverage_limit: Optional[Decimal]
    deductible: Optional[Decimal]

class PolicyCoverageRead(PolicyCoverageCreate):
    id: int
    policy_id: int
    class Config:
        from_attributes = True

# --------------------
# Policy
# --------------------
class PolicyCreate(BaseModel):
    policy_number: str
    customer_id: int
    product_id: str
    agent_id: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    sum_insured: Optional[Decimal]
    premium: Optional[Decimal]
    status: Optional[str]
    coverages: Optional[List[PolicyCoverageCreate]] = []

class PolicyRead(BaseModel):
    id: int
    policy_number: str
    customer_id: int
    product_id: str
    agent_id: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    sum_insured: Optional[Decimal]
    premium: Optional[Decimal]
    status: Optional[str]
    created_at: datetime
    coverages: Optional[List[PolicyCoverageRead]] = []

    class Config:
        from_attributes = True

# --------------------
# Beneficiary
# --------------------
class BeneficiaryCreate(BaseModel):
    client_id: int
    full_name: str
    relationship: str
    percentage: Optional[Decimal]
    contact_info: Optional[str]

class BeneficiaryRead(BeneficiaryCreate):
    id: int
    policy_id: int
    class Config:
        from_attributes = True

class PolicyUpdate(BaseModel):
    policy_number: Optional[str] = None
    customer_id: Optional[int] = None
    product_id: Optional[str] = None
    agent_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    sum_insured: Optional[Decimal] = None
    premium: Optional[Decimal] = None
    status: Optional[str] = None

class PolicyCoverageUpdate(BaseModel):
    coverage_code: Optional[str] = None
    coverage_name: Optional[str] = None
    coverage_limit: Optional[Decimal] = None
    deductible: Optional[Decimal] = None

class BeneficiaryUpdate(BaseModel):
    client_id: Optional[int] = None
    full_name: Optional[str] = None
    relationship: Optional[str] = None
    percentage: Optional[Decimal] = None
    contact_info: Optional[str] = None
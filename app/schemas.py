from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

# --------------------
# PRODUCT
# --------------------
class ProductBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    product_type: Optional[str] = None
    base_premium: Optional[Decimal] = 0  # coincide con el modelo

class ProductCreate(ProductBase):
    """Schema para crear un producto (POST)."""
    pass

class ProductUpdate(BaseModel):
    """Schema para actualizar parcialmente un producto (PATCH)."""
    code: Optional[str]
    name: Optional[str]
    description: Optional[str]
    product_type: Optional[str]
    base_premium: Optional[Decimal]

class ProductRead(ProductBase):
    id: int
    class Config:
        from_attributes = True

# --------------------
# POLICY
# --------------------
class PolicyBase(BaseModel):
    policy_number: str
    customer_id: int
    product_id: str  # se refiere a Product.code
    agent_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    sum_insured: Optional[Decimal] = None
    premium: Optional[Decimal] = None
    status: Optional[str] = "ACTIVE"

class PolicyCreate(PolicyBase):
    coverages: Optional[List["PolicyCoverageCreate"]] = None

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

class PolicyRead(PolicyBase):
    id: int
    coverages: List["PolicyCoverageRead"] = []

    class Config:
        from_attributes = True

# --------------------
# POLICY COVERAGE
# --------------------
class PolicyCoverageBase(BaseModel):
    coverage_code: str
    coverage_name: str
    coverage_limit: Optional[Decimal] = None
    deductible: Optional[Decimal] = None

class PolicyCoverageCreate(PolicyCoverageBase):
    pass

class PolicyCoverageUpdate(BaseModel):
    coverage_code: Optional[str] = None
    coverage_name: Optional[str] = None
    coverage_limit: Optional[Decimal] = None
    deductible: Optional[Decimal] = None

class PolicyCoverageRead(PolicyCoverageBase):
    id: int
    policy_id: int

    class Config:
        from_attributes = True

# --------------------
# BENEFICIARY
# --------------------
class BeneficiaryBase(BaseModel):
    client_id: int
    full_name: str
    relationship: str
    percentage: Optional[Decimal] = None
    contact_info: Optional[str] = None

class BeneficiaryCreate(BeneficiaryBase):
    pass

class BeneficiaryUpdate(BaseModel):
    client_id: Optional[int] = None
    full_name: Optional[str] = None
    relationship: Optional[str] = None
    percentage: Optional[Decimal] = None
    contact_info: Optional[str] = None

class BeneficiaryRead(BeneficiaryBase):
    id: int
    policy_id: int
    class Config:
        from_attributes = True
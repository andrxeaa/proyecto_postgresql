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
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    product_type: Optional[str] = None
    base_premium: Optional[Decimal] = None

class ProductRead(ProductBase):
    id: int
    class Config:
        from_attributes = True

# --------------------
# POLICY COVERAGE (definir antes de Policy para evitar forward refs)
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
# BENEFICIARY (también definido antes si se quiere)
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

# --------------------
# POLICY
# --------------------
class PolicyBase(BaseModel):
    policy_number: str
    customer_id: int
    product_id: str  # referencia a product.code
    agent_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    sum_insured: Optional[Decimal] = None
    premium: Optional[Decimal] = None
    status: Optional[str] = "ACTIVE"

class PolicyCreate(PolicyBase):
    # coverages opcional al crear
    coverages: Optional[List[PolicyCoverageCreate]] = None

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
    created_at: Optional[datetime] = None        # si quieres exponer created_at
    coverages: List[PolicyCoverageRead] = []
    # opcional: beneficiaries si quieres incluirlos en el detalle
    # beneficiaries: List[BeneficiaryRead] = []

    class Config:
        from_attributes = True

# --- resolver forward-refs (Pydantic v2)
PolicyCreate.model_rebuild()
PolicyRead.model_rebuild()
PolicyCoverageRead.model_rebuild()
BeneficiaryRead.model_rebuild()
# app/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from decimal import Decimal

class ProductCreate(BaseModel):
    code: str
    name: str
    description: Optional[str]
    product_type: Optional[str]
    base_premium: Optional[Decimal]

class ProductRead(ProductCreate):
    id: int
    class Config:
        from_attributes = True

class PolicyCoverageCreate(BaseModel):
    coverage_code: str
    coverage_name: str
    coverage_limit: Optional[Decimal]
    deductible: Optional[Decimal]

class PolicyCreate(BaseModel):
    policy_number: str
    customer_id: int
    product_id: int
    agent_id: Optional[int]
    start_date: Optional[date]
    end_date: Optional[date]
    sum_insured: Optional[Decimal]
    premium: Optional[Decimal]
    status: Optional[str]
    coverages: Optional[List[PolicyCoverageCreate]] = []

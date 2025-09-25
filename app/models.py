# app/models.py
from sqlalchemy import Column, Integer, String, Numeric, Text, Date, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from .db import Base

class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    product_type = Column(String(50))
    base_premium = Column(Numeric(12,2), default=0)

class Policy(Base):
    __tablename__ = "policy"
    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String(100), unique=True, nullable=False)
    customer_id = Column(Integer, nullable=False)  # referencia lógica
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    agent_id = Column(Integer)  # referencia lógica
    start_date = Column(Date)
    end_date = Column(Date)
    sum_insured = Column(Numeric(14,2))
    premium = Column(Numeric(12,2))
    status = Column(String(50))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class PolicyCoverage(Base):
    __tablename__ = "policy_coverage"
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policy.id"), nullable=False)
    coverage_code = Column(String(100))
    coverage_name = Column(String(255))
    coverage_limit = Column(Numeric(14,2))
    deductible = Column(Numeric(12,2))

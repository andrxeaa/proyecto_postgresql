from sqlalchemy import Column, Integer, String, Numeric, Text, Date, TIMESTAMP, ForeignKey, BigInteger
from sqlalchemy.sql import func
from .db import Base

# --------------------
# Product
# --------------------
class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    product_type = Column(String(50))
    base_premium = Column(Numeric(12, 2), default=0)

# --------------------
# Policy
# --------------------
class Policy(Base):
    __tablename__ = "policy"
    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String(100), unique=True, nullable=False)
    customer_id = Column(Integer, nullable=False)  # referencia lógica a microservicio Customer
    product_id = Column(String(50), ForeignKey("product.code"), nullable=False)  # ahora referencia a product.code
    agent_id = Column(String(50))  # referencia lógica a microservicio Agent
    start_date = Column(Date)
    end_date = Column(Date)
    sum_insured = Column(Numeric(14, 2))
    premium = Column(Numeric(12, 2))
    status = Column(String(50))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

# --------------------
# PolicyCoverage
# --------------------
class PolicyCoverage(Base):
    __tablename__ = "policy_coverage"
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policy.id"), nullable=False)
    coverage_code = Column(String(100))
    coverage_name = Column(String(255))
    coverage_limit = Column(Numeric(14, 2))
    deductible = Column(Numeric(12, 2))

# --------------------
# Beneficiary
# --------------------
class Beneficiary(Base):
    __tablename__ = "beneficiary"
    id = Column(BigInteger, primary_key=True, index=True)
    policy_id = Column(BigInteger, ForeignKey("policy.id"), nullable=False)
    client_id = Column(BigInteger, nullable=False)  # referencia lógica a microservicio de clientes
    full_name = Column(String(255), nullable=False)
    relationship = Column(String(50), nullable=False)  # Ej: hijo, cónyuge, padre
    percentage = Column(Numeric(5, 2))
    contact_info = Column(Text)

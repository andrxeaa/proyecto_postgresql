CREATE TABLE product (
  id SERIAL PRIMARY KEY,
  code VARCHAR(50) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  product_type VARCHAR(50),
  base_premium NUMERIC(12,2) DEFAULT 0
);

CREATE TABLE policy (
  id SERIAL PRIMARY KEY,
  policy_number VARCHAR(100) NOT NULL UNIQUE,
  customer_id INTEGER NOT NULL,  -- referencia lógica a microservicio Customer
  product_id INTEGER NOT NULL REFERENCES product(id) ON DELETE RESTRICT,
  agent_id INTEGER,               -- referencia lógica a microservicio Agent
  start_date DATE,
  end_date DATE,
  sum_insured NUMERIC(14,2),
  premium NUMERIC(12,2),
  status VARCHAR(50),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX idx_policy_customer_id ON policy(customer_id);
CREATE INDEX idx_policy_product_id ON policy(product_id);

CREATE TABLE policy_coverage (
  id SERIAL PRIMARY KEY,
  policy_id INTEGER NOT NULL REFERENCES policy(id) ON DELETE CASCADE,
  coverage_code VARCHAR(100),
  coverage_name VARCHAR(255),
  coverage_limit NUMERIC(14,2),
  deductible NUMERIC(12,2)
);

CREATE INDEX idx_policycoverage_policy_id ON policy_coverage(policy_id);

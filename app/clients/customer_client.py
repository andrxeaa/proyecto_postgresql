# app/clients/customer_client.py
import os
import httpx
from dotenv import load_dotenv
load_dotenv()

CUSTOMER_BASE = os.getenv("CUSTOMER_SERVICE_URL", "http://customer-service:8000")

async def get_customer(customer_id: int):
    url = f"{CUSTOMER_BASE}/customers/{customer_id}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url)
            if r.status_code == 200:
                return r.json()
    except Exception:
        return None
    return None

# Policy Service (FastAPI + Postgres)

API del microservicio **Policy Service** (Python / FastAPI / SQLAlchemy async) — administra productos, pólizas, coberturas y beneficiarios.

---

## Contenido
- Resumen
- Requisitos
- Variables de entorno
- Ejecutar en local (dev)
- Ejecutar en Docker (prod)
- Swagger / OpenAPI
- Postman
- Endpoints (ruta, método, descripción, ejemplo)
- Comportamientos importantes / notas operativas

---

## Resumen
Este repositorio contiene la API (FastAPI) que expone los siguientes recursos principales:

- `products` — CRUD de productos de seguros  
- `policies` — CRUD de pólizas (entidad principal)  
- `coverages` — coberturas **anidadas** bajo `/policies/{policy_id}/coverages`  
- `beneficiaries` — beneficiarios **anidados** bajo `/policies/{policy_id}/beneficiaries`

La API usa SQLAlchemy **asíncrono** (`AsyncSession`) y Pydantic v2 (`from_attributes = True` en los schemas). La base de datos es PostgreSQL y normalmente vive en otra VM; la URL de conexión se configura vía `DATABASE_URL`.

---

## Requisitos
- Python 3.11+
- PostgreSQL (en otra VM o contenedor)
- `poetry` o `pip` (según prefieras)
- `asyncpg` + SQLAlchemy async
- Docker (opcional para despliegue)

---

## Variables de entorno (principales)
Colocar en `.env` (o en el entorno del contenedor):

```
DATABASE_URL=postgresql+asyncpg://<USER>:<PASSWORD>@<DB_HOST>:5432/<DB_NAME>
```


> **IMPORTANTE**: `DATABASE_URL` debe usar el dialecto `postgresql+asyncpg://` para Async SQLAlchemy.

## Ejecutar con Docker (producción)
### Construir imagen:

```
docker build -t policy-service:latest -f prod/Dockerfile .
```

### Ejecutar (ejemplo, la DB está fuera; pasas la env):

```
docker run -e DATABASE_URL='postgresql+asyncpg://user:pass@DB_IP:5432/policydb' -p 8000:8000 policy-service:latest
```
Si usas docker-compose en repo separado para API, asegúrate de no acoplar DB local; en docker-compose.prod.yml solo levanta la API y asigna DATABASE_URL a la IP privada de la VM DB.

### Swagger / OpenAPI
UI interactiva (Swagger): ``http://<host>:8000/docs``

JSON OpenAPI: ``http://<host>:8000/openapi.json``

### Postman
Importa la colección JSON ``policy-service.postman_collection.json``.
Asegúrate de configurar la variable base_url a la URL donde esté corriendo tu API.

## Endpoints — Resumen y ejemplos

### 1) Products

Prefix: ``/products``

- ``GET /products``
    -  Lista todos los productos.
    - Query params: none.

- ``GET /products/{id}``
    - Obtener por ``id`` (PK autoincremental).
    - Respuesta: ``ProductRead``.

- ``POST /products``
    - Crear producto. Body:

    ```
    {
        "code": "PRD001",
        "name": "Seguro X",
        "description": "Descripción",
        "product_type": "LIFE",
        "base_premium": 120.50
    }
    ```

- ``PATCH /products/{id}``
    - Actualización parcial. Envía solo campos a cambiar.

- ``DELETE /products/{id}``
    - Elimina producto (si no existen FK relacionadas).

### 2) Policies

Prefix: ``/policies``

- GET ``/policies``
    - Lista pólizas. Query params opcionales:

        - ``customerId`` (int)

        - ``agentId`` (string)

        - ``status`` (string)

        - ``limit``, ``offset`` (paginación)

    Ejemplo:

    ```
    GET /policies?customerId=123&status=ACTIVE
    ```

- GET ``/policies/{policy_id}``
    - Detalle de póliza. Respuesta incluye ``coverages`` (lista).

- POST ``/policies``
    - Crear póliza. Body (ejemplo acepta coverages anidadas):

    ```
    {
    "policy_number": "POL-0001",
    "customer_id": 123,
    "product_id": "PRD001",
    "agent_id": "AGT001",
    "start_date": "2025-01-01",
    "end_date": "2026-01-01",
    "sum_insured": 50000,
    "premium": 500,
    "status": "ACTIVE",
    "coverages": [
        {"coverage_code": "COV01","coverage_name":"Cobertura A","coverage_limit":10000,"deductible":500}
                 ]
    }
    ```
    **Validaciones internas:**

    - Verifica que ``product_id`` (``product.code``) exista.

    - Puedes integrar validación de ``customer_id`` llamando al microservicio ``customer`` (si habilitado).

- PATCH ``/policies/{policy_id}``
    - Actualización parcial de póliza (usar ``PolicyUpdate``).

- DELETE ``/policies/{policy_id}``
    - Por defecto hace soft-cancel: pone ``status = "CANCELLED"``.
    - Para borrado físico: ``DELETE /policies/{policy_id}?hard=true``.

### 3) Coverages (anidados)
Rutas bajo ``/policies/{policy_id}/coverages``

- GET ``/policies/{policy_id}/coverages`` — listar coberturas de la póliza.

- GET ``/policies/{policy_id}/coverages/{coverage_id}`` — detalle cobertura.

- POST ``/policies/{policy_id}/coverages`` — crear cobertura (body: ``PolicyCoverageCreate``).

- PATCH ``/policies/{policy_id}/coverages/{coverage_id}`` — actualizar cobertura (parcial).

- DELETE ``/policies/{policy_id}/coverages/{coverage_id}`` — eliminar cobertura.

### 4) Beneficiaries (anidados)
Rutas bajo ``/policies/{policy_id}/beneficiaries``

- GET ``/policies/{policy_id}/beneficiaries`` — listar beneficiarios.

- GET ``/policies/{policy_id}/beneficiaries/{beneficiary_id}`` — detalle.

- POST ``/policies/{policy_id}/beneficiaries`` — crear (``BeneficiaryCreate``).

- PATCH ``/policies/{policy_id}/beneficiaries/{beneficiary_id}`` — actualizar parcial.

- DELETE ``/policies/{policy_id}/beneficiaries/{beneficiary_id}`` — eliminar.

## Reglas recomendadas:

- Validar ``policy_id`` no nulo y existencia antes de crear coberturas/beneficiarios.

- Validar que la suma de percentage de beneficiarios por póliza ≤ 100.

## Esquemas (resumen)

- ProductCreate, ProductUpdate, ProductRead

- PolicyCreate (incluye coverages), PolicyRead, PolicyUpdate

- PolicyCoverageCreate, PolicyCoverageUpdate, PolicyCoverageRead

- BeneficiaryCreate, BeneficiaryUpdate, BeneficiaryRead

## Comportamientos importantes y recomendaciones
- Sesión async: la app usa ``AsyncSession`` (no mezclar con consultas síncronas ``.query()``).

- Seeds: insertado por separado desde el repo de DB (archivo ``init/seed.sql``). Si importas repetidamente, evita duplicados (usa ON CONFLICT o comprueba existencia).

- Seguridad/CORS: en dev se usa ``allow_origins=["*"]``. En producción restringir orígenes.

- Errores: endpoints lanzan 404 si entidad no existe, 400 para bad-request (ej. product inexistente al crear póliza), 422 para validaciones Pydantic.

## Últimas notas / despliegue en AWS (VMs)
Para arquitectura propuesta (DB en VMs con alta disponibilidad + VMs para APIs con balanceador):

- El ``DATABASE_URL`` que pongas en la VM de API debe usar la IP privada del balanceador / IP de la VM DB según red VPC.

- Abrir puerto 5432 entre VPCs / security groups.

- Automatizar builds y deploys con GitHub Actions: build imagen, push a Docker Hub / ECR, despliegue a VM vía SSH/Ansible/Cloud-Init o ECS/EKS.
# Policy Service (FastAPI + Postgres)

## Run (dev)
docker-compose up --build

## Swagger UI
http://localhost:8000/docs

## Seed DB (20k policies)
docker-compose exec policy-service python -m app.seed_data

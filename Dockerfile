# Imagen base ligera
FROM python:3.11-slim

# Variables para evitar pyc y mejorar logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear usuario no root
RUN adduser --disabled-password --gecos '' appuser

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir "gunicorn[uvicorn]"

# Copiar código
COPY . .

# Permisos
RUN chown -R appuser:appuser /app
USER appuser

# Puerto
EXPOSE 8000

# Comando para producción con Gunicorn + UvicornWorkers
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "8", "--timeout", "60"]
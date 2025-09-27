# Imagen base oficial de Python
FROM python:3.11-slim

# Evitar que Python genere archivos .pyc y asegurar salida directa en logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear usuario no root por seguridad
RUN adduser --disabled-password --gecos '' appuser

# Definir directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias primero (mejor caching)
COPY ../requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY .. .

# Cambiar permisos de la carpeta
RUN chown -R appuser:appuser /app
USER appuser

# Exponer el puerto
EXPOSE 8000

# Ejecutar FastAPI con Uvicorn (modo producción, un solo proceso por contenedor)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.11-slim

# Evita que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Fuerza salida sin buffer (importante para logs en Docker)
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias primero (mejor uso de cache de capas)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . /app/

# Recolectar archivos estáticos en tiempo de build
# Usamos una SECRET_KEY temporal solo para este paso
RUN SECRET_KEY=build-time-dummy-secret python manage.py collectstatic --noinput

# Al iniciar el contenedor: aplicar migraciones y levantar Gunicorn
CMD python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3

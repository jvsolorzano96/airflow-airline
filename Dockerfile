# Usar la imagen base de Python 3.11
FROM python:3.11-slim

# Instalar el cliente de PostgreSQL, gcc y netcat-openbsd
RUN apt-get update && apt-get install -y postgresql-client gcc netcat-openbsd

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar y instalar las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script wait-for-it.sh y hacerlo ejecutable
COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

# Copiar el resto de la aplicación
COPY . .

# Comando para ejecutar la generación y aplicación de migraciones, y luego inicializar la base de datos
CMD ["./wait-for-it.sh", "postgres:5432", "--", "sh", "-c", "alembic revision --autogenerate -m 'auto-generated migration' && alembic upgrade head && python custom.py"]



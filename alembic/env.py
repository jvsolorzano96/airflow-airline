import os
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

# Configuración de logging
config = context.config
fileConfig(config.config_file_name)

# Obtener la URL de la base de datos desde una variable de entorno
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable not set")

# Establecer la URL de la base de datos en la configuración de Alembic
config.set_main_option("sqlalchemy.url", database_url)

# Importar los modelos después de haber configurado la URL de la base de datos
from models import Base  # Asegúrate de importar tus modelos aquí

# Interpretar la configuración del archivo alembic.ini
target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(config.get_main_option("sqlalchemy.url"))
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

import os
from sqlalchemy import create_engine
from models import Base

def initialize_database():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    print("Base de datos inicializada y tablas creadas.")

if __name__ == "__main__":
    initialize_database()

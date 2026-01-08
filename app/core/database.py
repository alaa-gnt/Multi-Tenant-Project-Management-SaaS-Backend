from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# defining our URL to the database (should be stored at .env file)
SQLALCHEMY_DATABASE_URL = 'postgresql://user:password@localhost:5432/postgres'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit  = False, autoflush=False , bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()  # a connection to the dataBase
    try:
        yield db
    finally:
        db.close()
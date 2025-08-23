from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL, echo=True) # Creates a data base engine TODO Remove echo in production
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
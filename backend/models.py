from sqlalchemy import create_engine, Column, String, Integer, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import datetime
import os
import time

Base = declarative_base()
# Use environment variable, crucial for connecting to PostgreSQL in production
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    # Fallback to SQLite for development if DATABASE_URL is not set
    DB_URL = "sqlite:///./local.db"
    print(f"Warning: DATABASE_URL not set. Using SQLite at {DB_URL}")

engine = create_engine(DB_URL, echo=False, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class SavedImage(Base):
    __tablename__ = "saved_images"
    id = Column(Integer, primary_key=True, index=True)
    unsplash_id = Column(String, index=True, unique=True)
    thumb = Column(String, nullable=False)
    full = Column(String, nullable=False)
    alt = Column(String, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            # Try to create all tables
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully")
            return True
        except SQLAlchemyError as e:
            print(f"Error creating tables (attempt {attempt + 1}/{max_retries}): {e}")
            
            # Try to manually clean up any problematic tables and sequences
            try:
                with engine.connect() as conn:
                    # Drop all tables and sequences that might be causing issues
                    conn.execute(text("DROP TABLE IF EXISTS saved_images CASCADE"))
                    conn.execute(text("DROP SEQUENCE IF EXISTS saved_images_id_seq CASCADE"))
                    conn.commit()
                print("Manually dropped problematic tables and sequences")
                
                # Try to create tables again
                Base.metadata.create_all(bind=engine)
                print("Tables created successfully after manual cleanup")
                return True
            except Exception as e2:
                print(f"Failed to manually clean up tables: {e2}")
                
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print("Max retries reached. Database initialization failed.")
                    return False
                    
    return False

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

# Prefer POSTGRES_* env vars when running in Docker; fall back to DB_* or defaults
DB_USER = os.getenv('DB_USER') or os.getenv('POSTGRES_USER') or 'rajdeepdey'
DB_PASSWORD = os.getenv('DB_PASSWORD') or os.getenv('POSTGRES_PASSWORD') or '2004'
DB_HOST = os.getenv('DB_HOST') or os.getenv('POSTGRES_HOST') or 'localhost'
DB_PORT = os.getenv('DB_PORT') or '5432'
DB_NAME = os.getenv('DB_NAME') or os.getenv('POSTGRES_DB') or 'mms_hrms_db'

# Construct database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine with a short connect timeout to fail fast if DB is unreachable
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10},
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    # Dependency for getting database session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Create all database tables on server startup
    Base.metadata.create_all(bind=engine)

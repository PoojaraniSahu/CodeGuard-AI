from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

from config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# If the URL starts with postgres:// (common in Heroku/older platforms), 
# change it to postgresql:// as required by SQLAlchemy
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Clean up invalid parameters that Supabase/Vercel might add
if SQLALCHEMY_DATABASE_URL and "postgresql" in SQLALCHEMY_DATABASE_URL:
    from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
    u = urlparse(SQLALCHEMY_DATABASE_URL)
    query = parse_qs(u.query)
    # Remove parameters that psycopg2 doesn't understand
    query.pop('supa', None)
    u = u._replace(query=urlencode(query, doseq=True))
    SQLALCHEMY_DATABASE_URL = urlunparse(u)

print(f"--- DATABASE CONNECTION: {'SQLite' if SQLALCHEMY_DATABASE_URL.startswith('sqlite') else 'PostgreSQL'} ---")


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

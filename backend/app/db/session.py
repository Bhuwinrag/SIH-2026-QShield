from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import socket
import logging

logger = logging.getLogger(__name__)

def is_port_open(host: str, port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((host, port))
        return True
    except Exception:
        return False

# Attempt to detect if PostgreSQL is running locally
db_url = settings.DATABASE_URL
if "localhost" in db_url or "127.0.0.1" in db_url:
    port = 5432
    if not is_port_open("localhost", port):
        logger.warning("PostgreSQL is not reachable on localhost:5432. Falling back to SQLite for native development.")
        import os
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        db_url = f"sqlite:///{os.path.join(base_dir, 'qshield_fallback.db')}"

if db_url.startswith("sqlite"):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

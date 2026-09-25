import logging
from sqlalchemy import text
from app.db.session import engine, db_url, SessionLocal
from app.db.base import Base
import app.models.domain  # Explicitly import domain models to register them with Base

logger = logging.getLogger(__name__)

def init_db():
    try:
        logger.info(f"Initializing database schema at {db_url}...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully.")
        
        # Safe ALTER TABLE to add artifact fields
        with engine.begin() as conn:
            try:
                conn.execute(text("ALTER TABLE qds_sessions ADD COLUMN artifact_name VARCHAR;"))
                logger.info("Added artifact_name column to qds_sessions.")
            except Exception:
                pass
            
            try:
                conn.execute(text("ALTER TABLE qds_sessions ADD COLUMN artifact_size INTEGER;"))
                logger.info("Added artifact_size column to qds_sessions.")
            except Exception:
                pass
                
            try:
                conn.execute(text("ALTER TABLE qds_sessions ADD COLUMN artifact_type VARCHAR;"))
                logger.info("Added artifact_type column to qds_sessions.")
            except Exception:
                pass

        # Verify DB by running a lightweight query
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            logger.info("Database connection and schema verified successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize or verify database: {e}")
        raise e

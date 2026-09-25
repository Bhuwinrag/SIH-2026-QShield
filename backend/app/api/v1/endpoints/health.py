from fastapi import APIRouter
from app.db.session import SessionLocal
from sqlalchemy import text
from app.workers.celery_app import celery_app
from redis import Redis
import os
import qiskit_aer

router = APIRouter()

@router.get("/")
def health_general():
    return {"status": "ONLINE", "message": "Q-SHIELD Backend is operational."}

@router.get("/quantum")
def health_quantum():
    try:
        # Just check if aer simulator can be instantiated
        qiskit_aer.AerSimulator()
        return {"status": "ONLINE", "engine": "Qiskit AerSimulator"}
    except Exception as e:
        return {"status": "OFFLINE", "error": str(e)}

@router.get("/database")
def health_database():
    try:
        from app.db.session import db_url
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        backend_type = "SQLite fallback" if db_url.startswith("sqlite") else "PostgreSQL"
        return {"status": "ONLINE", "backend": backend_type}
    except Exception as e:
        return {"status": "OFFLINE", "error": str(e)}

@router.get("/redis")
def health_redis():
    try:
        r = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), socket_connect_timeout=1)
        r.ping()
        return {"status": "ONLINE"}
    except Exception as e:
        return {"status": "OFFLINE", "error": str(e)}

@router.get("/worker")
def health_worker():
    try:
        # Fast check for Redis first, to avoid celery inspect hanging
        try:
            r = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), socket_connect_timeout=0.5)
            r.ping()
        except Exception:
            return {"status": "OFFLINE", "message": "ASYNC UNAVAILABLE"}

        i = celery_app.control.inspect(timeout=1.0)
        active = i.active()
        if active is None or len(active) == 0:
            return {"status": "OFFLINE", "message": "No active Celery workers found."}
        return {"status": "ONLINE", "active_workers": list(active.keys())}
    except Exception as e:
        return {"status": "OFFLINE", "error": str(e)}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.domain import QDSSession
from app.schemas.domain import QDSSessionCreate, QDSSessionResponse
import uuid
import secrets

router = APIRouter()

@router.post("/", response_model=QDSSessionResponse)
def create_session(session_in: QDSSessionCreate, db: Session = Depends(get_db)):
    nonce = secrets.token_hex(16)
    db_session = QDSSession(
        signer_id=session_in.signer_id,
        verifier_id=session_in.verifier_id,
        message_digest=session_in.message_digest,
        session_nonce=nonce,
        artifact_name=session_in.artifact_name,
        artifact_size=session_in.artifact_size,
        artifact_type=session_in.artifact_type
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/{session_id}", response_model=QDSSessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(QDSSession).filter(QDSSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

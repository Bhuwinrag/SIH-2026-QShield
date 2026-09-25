from fastapi import APIRouter, UploadFile, File, HTTPException
import hashlib

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit for demo

@router.post("/process")
async def process_artifact(file: UploadFile = File(...)):
    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
        
    # Read bytes safely
    file_bytes = await file.read()
    
    # Calculate SHA-256
    sha256_hash = hashlib.sha256(file_bytes).hexdigest()
    
    # Return metadata
    return {
        "artifact_name": file.filename,
        "artifact_size": file_size,
        "artifact_type": file.content_type or "application/octet-stream",
        "message_digest": sha256_hash
    }

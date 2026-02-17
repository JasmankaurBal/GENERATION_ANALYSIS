from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal

# IMPORT SERVICE FUNCTIONS WITH DIFFERENT NAMES
from app.services.mas_upload_services import (
    upload_plants,
    upload_units,
    preview_upload as preview_upload_service,
    confirm_upload as confirm_upload_service
)

from app.Schemas.mas_upload_schemas import PreviewResponse, UploadResponse

# CREATE ONLY ONE ROUTER
router = APIRouter(
    prefix="/master-upload",
    tags=["Master Upload"]
)


# =========================
# DB DEPENDENCY
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# PLANT UPLOAD DIRECT
# =========================

@router.post("/plant", response_model=UploadResponse)
def upload_plant_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return upload_plants(file, db)


# =========================
# UNIT UPLOAD DIRECT
# =========================

@router.post("/unit", response_model=UploadResponse)
def upload_unit_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return upload_units(file, db)


# =========================
# PREVIEW (NO SAVE)
# =========================

@router.post("/preview", response_model=PreviewResponse)
def preview_file(
    file: UploadFile = File(...),
    data_type: str = "plant",
    db: Session = Depends(get_db)
):
    return preview_upload_service(file, data_type, db)


# =========================
# CONFIRM (SAVE AFTER PREVIEW)
# =========================

@router.post("/confirm", response_model=UploadResponse)
def confirm_file_upload(
    file: UploadFile = File(...),
    data_type: str = "plant",
    db: Session = Depends(get_db)
):
    return confirm_upload_service(file, data_type, db)
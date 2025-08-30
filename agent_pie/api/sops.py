from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from agent_pie.crud import crud
from agent_pie.schemas import schemas
from agent_pie.crud import database as db
from agent_pie.utils.pdf_extractor import extract_text_from_pdf

router = APIRouter(prefix="/sops", tags=["sops"])


async def get_db():
    with db.SessionLocal() as session:
        yield session


@router.post("/", response_model=schemas.SOPRead)
async def upload_sop(
    manager_id: int,
    file: UploadFile = File(...),
    db_session: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_data = file.file.read()
    extracted_text = extract_text_from_pdf(file_data)

    sop_schema = schemas.SOPCreate(file_data=file_data, extracted_text=extracted_text)
    sop = crud.create_sop(db_session, sop_schema, manager_id)
    return sop


@router.get("/{sop_id}", response_model=schemas.SOPRead)
async def get_sop(sop_id: int, db_session: Session = Depends(get_db)):
    sop = crud.get_sop(db_session, sop_id)
    if not sop:
        raise HTTPException(status_code=404, detail="SOP not found")
    return sop

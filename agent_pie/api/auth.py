from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from agent_pie.crud import crud
from agent_pie.crud import database as db
from agent_pie.utils import auth
from agent_pie.schemas.schemas import LoginRequest, LoginWithSOPResponse, SOPRead

router = APIRouter(tags=["auth"])


def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@router.post("/login", response_model=LoginWithSOPResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # Verify user
    user = crud.get_user_by_email(db, data.email)
    if not user or not auth.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Get all SOPs
    sops = db.query(crud.models.SOP).all()

    sops_response = [
        SOPRead(
            id=s.id,
            filename=getattr(s, "filename", f"SOP-{s.id}"),
            created_at=str(s.created_at),
        )
        for s in sops
    ]

    return LoginWithSOPResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        is_manager=user.is_manager,
        sops=sops_response,
    )

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from agent_pie.crud import crud
from agent_pie.crud import database as db
from agent_pie.schemas import schemas
from agent_pie.utils import auth
from agent_pie.schemas.schemas import LoginRequest, LoginWithSOPResponse, SOPReadLogin

router = APIRouter(tags=["auth"])


def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@router.post("/login", response_model=schemas.LoginWithSOPResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # Verify user
    user = crud.get_user_by_email(db, data.email)

    if not user or not auth.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Get all SOPs
    sops = db.query(crud.models.SOP).all()

    sops_response = [
        SOPReadLogin(
            id=s.id,
            filename=s.file_name,
            # filename="test",
            created_at=s.created_at,
        )
        for s in sops
    ]

#    print("SOPs -------->", sops_response[0].model_dump())

    res = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_manager": user.is_manager,
        "sops": sops_response,
    }
    # print(res)
    return res
    # return {
    #     "id": 3,
    #     "name": "John Doe",
    #     "email": "john@mail.com",
    #     "is_manager": False,
    #     "sops": [{"id": 15, "filename": "SPOv1", "create_at": datetime.now()}],
    # }

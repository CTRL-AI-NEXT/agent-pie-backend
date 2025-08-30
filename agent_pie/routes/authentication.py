from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from agent_pie.crud import database
from agent_pie.schemas import schemas
from agent_pie.models import models
from agent_pie.utils import utils


router = APIRouter(prefix="/api/v1/users", tags=["Authentication"])


@router.post("/login", response_model=schemas.UserLoginResponse)
async def userLogin(
    user_credentials: schemas.UserLoginRequest,
    db: Session = Depends(database.get_db),
):
    user = (
        db.query(models.User)
        .filter(user_credentials.email == models.User.email)
        .first()
    )
    print(user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user credentials!"
        )

    if user_credentials.password != user.password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user credentials!"
        )

    # access_token = oauth.create_access_token(
    #     data={"employee_id": str(user.employee_id)}
    # )

    return user

from fastapi import APIRouter, Depends, HTTPException, status

# from sqlalchemy.ext.declarative import
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from agent_pie.crud import crud
from agent_pie.schemas import schemas
from agent_pie.crud import database as db

router = APIRouter(prefix="/users", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_db():
    with db.SessionLocal() as session:
        yield session


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


@router.post("/", response_model=schemas.UserRead)
async def register_user(
    user: schemas.UserCreate, db_session: Session = Depends(get_db)
):
    db_user = crud.get_user_by_email(db_session, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(user.password)
    new_user = crud.create_user(db_session, user, hashed)
    return new_user


@router.get("/{user_id}", response_model=schemas.UserRead)
async def get_user(user_id: int, db_session: Session = Depends(get_db)):
    user = crud.get_user(db_session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

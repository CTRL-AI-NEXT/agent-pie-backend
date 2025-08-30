# from os import getenv
from dotenv import load_dotenv

from sqlalchemy import create_engine

# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

# engine = create_engine(getenv("POSTGRES_DATABASE_URL"))

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# AsyncSessionLocal = sessionmaker(
#     bind=engine, class_=AsyncSession, expire_on_commit=False
# )
Base = declarative_base()


# async def get_db():
#     with AsyncSessionLocal() as session:
#         yield session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

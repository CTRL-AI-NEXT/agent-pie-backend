from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent_pie.crud.database import engine
from agent_pie.models.models import Base
from agent_pie.api import users, analytics, quizzes, sops, training, auth, chat

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(sops.router)
app.include_router(training.router)
app.include_router(quizzes.router)
app.include_router(analytics.router)
app.include_router(auth.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"message": "Welcome to Agent Pie"}

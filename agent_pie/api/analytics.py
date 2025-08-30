from fastapi import APIRouter, Depends, HTTPException

# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from statistics import mean
from typing import List, Dict, Any

from agent_pie.crud import crud
from agent_pie.models import models
from agent_pie.crud import database as db

router = APIRouter(prefix="/analytics", tags=["analytics"])


async def get_db():
    with db.SessionLocal() as session:
        yield session


# -----------------------------
# Employee performance
# -----------------------------
@router.get("/employee/{employee_id}")
async def employee_performance(
    employee_id: int, db_session: Session = Depends(get_db)
) -> Dict[str, Any]:
    # Fetch quiz attempts
    attempts = crud.list_quiz_attempts(
        db_session, quiz_id=None, employee_id=employee_id
    )

    if not attempts:
        return {
            "employee_id": employee_id,
            "total_attempts": 0,
            "average_score": 0,
            "completed_trainings": 0,
        }

    scores = [a.score for a in attempts if a.score is not None]
    avg_score = mean(scores) if scores else 0

    return {
        "employee_id": employee_id,
        "total_attempts": len(attempts),
        "average_score": avg_score,
        "completed_trainings": len(
            set(a.quiz.module_id for a in attempts)
        ),  # quizzes taken = trainings completed
    }


# -----------------------------
# Quiz-level analytics
# -----------------------------
@router.get("/quiz/{quiz_id}")
async def quiz_performance(
    quiz_id: int, db_session: Session = Depends(get_db)
) -> Dict[str, Any]:
    attempts = crud.list_quiz_attempts(db_session, quiz_id=quiz_id)

    if not attempts:
        raise HTTPException(status_code=404, detail="No attempts found for this quiz")

    scores = [a.score for a in attempts if a.score is not None]
    avg_score = mean(scores) if scores else 0

    best = max(attempts, key=lambda a: a.score)
    worst = min(attempts, key=lambda a: a.score)

    return {
        "quiz_id": quiz_id,
        "attempt_count": len(attempts),
        "average_score": avg_score,
        "best_performer": {"employee_id": best.employee_id, "score": best.score},
        "worst_performer": {"employee_id": worst.employee_id, "score": worst.score},
    }


# -----------------------------
# Manager dashboard
# -----------------------------
@router.get("/manager/{manager_id}")
async def manager_dashboard(
    manager_id: int, db_session: Session = Depends(get_db)
) -> Dict[str, Any]:
    # Fetch all SOPs of manager
    sops = crud.list_sops(db_session, manager_id=manager_id)

    if not sops:
        return {"manager_id": manager_id, "sops": [], "employees": []}

    # Collect all quizzes from manager’s SOPs
    quizzes = []
    for sop in sops:
        if sop.training_module and sop.training_module.quiz:
            quizzes.append(sop.training_module.quiz)

    # Collect all attempts per quiz
    employee_stats = {}
    for quiz in quizzes:
        attempts = crud.list_quiz_attempts(db_session, quiz.id)
        for a in attempts:
            if a.employee_id not in employee_stats:
                employee_stats[a.employee_id] = {"attempts": [], "scores": []}
            employee_stats[a.employee_id]["attempts"].append(a)
            if a.score is not None:
                employee_stats[a.employee_id]["scores"].append(a.score)

    employees_summary = []
    for emp_id, stats in employee_stats.items():
        avg_score = mean(stats["scores"]) if stats["scores"] else 0
        employees_summary.append(
            {
                "employee_id": emp_id,
                "total_attempts": len(stats["attempts"]),
                "average_score": avg_score,
                "completed_trainings": len(set(a.quiz_id for a in stats["attempts"])),
            }
        )

    return {
        "manager_id": manager_id,
        "total_sops": len(sops),
        "employees": employees_summary,
    }

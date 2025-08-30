from fastapi import APIRouter, Depends, HTTPException

# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List
from agent_pie.crud import crud
from agent_pie.schemas import schemas
from agent_pie.crud import database as db
from agent_pie.agents.sop_parser import normalize_steps_for_pydantic, parse_sop_to_steps


router = APIRouter(prefix="/training", tags=["training"])


async def get_db():
    with db.SessionLocal() as session:
        yield session


# @router.post("/{sop_id}/generate", response_model=schemas.TrainingModuleRead)
# async def generate_training(sop_id: int, db_session: AsyncSession = Depends(get_db)):
#     # Create a training module
#     module = await crud.create_training_module(db_session, sop_id)

#     # Agent should parse SOP and return structured steps
#     # For now, just mock steps
#     dummy_steps = [
#         schemas.TrainingStepCreate(
#             title="Step 1: Gather Ingredients",
#             description="List all required items",
#             order=1,
#         ),
#         schemas.TrainingStepCreate(
#             title="Step 2: Prep", description="Cut and clean as per SOP", order=2
#         ),
#     ]
#     await crud.add_training_steps(db_session, module.id, dummy_steps)

#     return await crud.get_training_module(db_session, module.id)


@router.post("/{sop_id}/generate", response_model=schemas.TrainingModuleRead)
async def generate_training(sop_id: int, db_session: Session = Depends(get_db)):
    module = crud.create_training_module(db_session, sop_id)

    sop = crud.get_sop(db_session, sop_id)
    if not sop or not sop.extracted_text:
        raise HTTPException(status_code=400, detail="SOP text not available")

    # 🔗 Use agent
    steps = parse_sop_to_steps(sop.extracted_text)
    steps = normalize_steps_for_pydantic(steps)  # ✅ convert substeps to dicts

    steps_schema = [
        schemas.TrainingStepCreate(**s, order=i + 1) for i, s in enumerate(steps)
    ]
    crud.add_training_steps(db_session, module.id, steps_schema)

    return crud.get_training_module(db_session, module.id)


@router.get("/{module_id}", response_model=schemas.TrainingModuleRead)
async def get_training_module(module_id: int, db_session: Session = Depends(get_db)):
    module = crud.get_training_module(db_session, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module

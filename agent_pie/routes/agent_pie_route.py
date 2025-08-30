from fastapi import APIRouter
from agent_pie.schemas import schemas
from agent_pie.agents.agent_init import llm_chain

router = APIRouter(prefix="/api/v1/agent", tags=["Agent Pie"])


@router.post("/chat", response_model=schemas.ResponseQuestion)
async def chat(question: schemas.RequestQuestion):
    response = llm_chain.run(question)
    print(response)
    return {"response": response}

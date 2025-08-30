from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from agent_pie.crud import database as db
from agent_pie.crud import crud
from agent_pie.models import models
from agent_pie.schemas.schemas import ChatRequest, ChatResponse
from agent_pie.agents.agent_init import llm
import re
from sqlalchemy.orm import Session

router = APIRouter(tags=["chat"])


def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    # Fetch all SOPs
    sops = db.query(models.SOP).all()
    if not sops:
        return ChatResponse(
            answer="No SOPs available in the system.", sop_ids=[], sop_title=None
        )

    # Build SOP context with IDs
    sop_contexts = ""
    sop_mapping = {}
    for s in sops:
        sop_text = s.extracted_text or ""
        sop_contexts += f"SOP ID {s.id}\n{sop_text}\n\n"
        sop_mapping[s.id] = sop_text

    # Prompt for strict answer and SOP reference
    prompt = f"""
You are a restaurant SOP assistant. Answer the user’s question **only using the SOPs below**.

Each SOP has an ID. If the answer exists in multiple SOPs, **list all SOP IDs**.
Provide the answer strictly from the SOPs, no hallucination.

Format exactly like:
Answer: <answer text>
SOP IDs: <comma separated SOP IDs>

SOPs:
{sop_contexts}

User Question:
{request.question}
"""

    # Call LLM
    response = llm.invoke(prompt)
    text = response.content.strip()

    # Extract answer and SOP IDs
    answer_match = re.search(r"Answer:\s*(.*)", text)
    sop_match = re.search(r"SOP IDs?:\s*(.*)", text)

    answer_text = (
        answer_match.group(1).strip()
        if answer_match
        else "No answer found in the provided SOPs."
    )
    sop_ids_text = sop_match.group(1).strip() if sop_match else ""
    sop_ids = [int(x.strip()) for x in sop_ids_text.split(",") if x.strip().isdigit()]

    # Generate a single-line title from referenced SOPs content
    if sop_ids:
        combined_text = "\n".join([sop_mapping[i] for i in sop_ids])
        title_prompt = f"""
Summarize the following SOP content into a single-line title:
{combined_text}
"""
        title_response = llm.invoke(title_prompt)
        sop_title = title_response.content.strip()
    else:
        sop_title = None

    return ChatResponse(
        question=request.question,
        answer=answer_text,
        sop_ids=sop_ids,
        sop_title=sop_title,
    )

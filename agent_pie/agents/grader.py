# from langchain_openai import ChatOpenAI
from agent_pie.agents.agent_init import llm

# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def grade_open_answer(question: str, reference_answer: str, student_answer: str) -> int:
    """
    Uses LLM to grade an open-ended answer on a 0-1 scale.
    """
    prompt = f"""
    Grade the following open-ended answer.
    Question: {question}
    Correct answer: {reference_answer}
    Student answer: {student_answer}

    Return only 1 or 0 (1 if acceptable, 0 if incorrect).
    """
    resp = llm.invoke(prompt)
    try:
        return int(resp.content.strip())
    except:
        return 0

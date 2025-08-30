from typing import List

# from langchain_openai import ChatOpenAI
import json

# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
from agent_pie.agents.agent_init import llm


def generate_quiz_from_module(module_text: str) -> List[dict]:
    """
    Generates quiz questions from a training module.
    """
    prompt = f"""
    You are a training evaluator. Create a quiz based on this training module:
    {module_text}

    - At least 2 MCQs, 1 True/False, 1 Open-ended.
    Return JSON in format:
    {{
      "questions": [
        {{
          "question_text": "...",
          "question_type": "mcq|true_false|open_ended",
          "options": ["..."] (if applicable),
          "correct_answer": "..."
        }}
      ]
    }}
    """
    resp = llm.invoke(prompt)
    try:
        return json.loads(resp.content)["questions"]
    except Exception:
        return [
            {
                "question_text": "Fallback question",
                "question_type": "mcq",
                "options": ["A", "B"],
                "correct_answer": "A",
            }
        ]

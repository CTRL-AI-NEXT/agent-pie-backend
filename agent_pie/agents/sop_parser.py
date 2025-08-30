from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from typing import List, Dict
from agent_pie.agents.agent_init import llm
import json
import re

# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def parse_sop_to_steps(sop_text: str):
    """
    Converts SOP text into structured steps with substeps.
    Robustly extracts JSON even if the LLM adds extra text.
    """
    prompt = f"""
You are a professional training designer. Convert the following SOP into structured training steps.
Each step must have:
- title: short name of the step
- description: detailed explanation
- substeps: optional list of short actions

Return **ONLY valid JSON** in this exact format:
{{
  "steps": [
    {{
      "title": "Step Title",
      "description": "Step Description",
      "substeps": ["Substep 1", "Substep 2"]
    }}
  ]
}}

SOP Text:
\"\"\"{sop_text}\"\"\"
"""

    resp = llm.invoke(prompt)
    content = resp.content.strip()

    # Try to extract JSON from the response
    try:
        # Match first {...} block in the response
        json_text = re.search(r"\{.*\}", content, re.DOTALL).group()
        parsed = json.loads(json_text)
        steps = parsed.get("steps", [])
        # Ensure all required fields exist
        for step in steps:
            step.setdefault("title", "Untitled Step")
            step.setdefault("description", "No description provided.")
            substeps = step.get("substeps", [])
            if substeps and isinstance(substeps[0], str):
                step["substeps"] = [{"text": s} for s in substeps]
            elif not substeps:
                step["substeps"] = []
            # step.setdefault("substeps", [])
        return steps
    except Exception as e:
        print("Failed to parse JSON from LLM response:")
        print(content)
        print("Error:", e)
        # Fallback
        return [
            {
                "title": "Step 1",
                "description": "Could not parse properly.",
                "substeps": [],
            }
        ]


def normalize_steps_for_pydantic(steps: list[dict]) -> list[dict]:
    """
    Ensure each step has 'title', 'description', and 'substeps' as a list of dicts.
    Splits long string substeps into individual items.
    """
    for step in steps:
        step.setdefault("title", "Untitled Step")
        step.setdefault("description", "No description provided.")
        substeps = step.get("substeps", [])
        normalized = []

        if substeps:
            for s in substeps:
                # If it's already a dict, keep it
                if isinstance(s, dict):
                    normalized.append(s)
                # If it's a string, split by common separators: newline or comma
                elif isinstance(s, str):
                    parts = [p.strip() for p in re.split(r"[\n,]+", s) if p.strip()]
                    normalized.extend([{"text": p} for p in parts])
        step["substeps"] = normalized
    return steps

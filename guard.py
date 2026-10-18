import os
import ollama
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")


def check_question(question, schema):
    """Return (status, message). Status is OK, AMBIGUOUS or UNSUPPORTED."""
    prompt = f"""You are a gatekeeper for a database assistant.
Decide if the QUESTION can be answered with the database described below.

Reply with exactly two lines:
Line 1: one word, either OK, AMBIGUOUS or UNSUPPORTED
Line 2: a short message for the user

Rules:
- OK: the question is clear and the data can answer it.
- AMBIGUOUS: the question is too vague (for example "best" or "top" with no measure). Line 2 must be a clarifying question.
- UNSUPPORTED: the data cannot answer it, it is unrelated to the data, or it asks to change or delete data. Line 2 must explain why.

DATABASE:
{schema}

QUESTION: {question}
"""
    r = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )
    lines = [l.strip() for l in r["message"]["content"].strip().splitlines() if l.strip()]
    if not lines:
        return "OK", ""

    first = lines[0].upper().strip("*:. ")
    message = lines[1] if len(lines) > 1 else ""

    if first.startswith("AMBIGUOUS"):
        return "AMBIGUOUS", message
    if first.startswith("UNSUPPORTED"):
        return "UNSUPPORTED", message
    return "OK", ""
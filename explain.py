import os
import ollama
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")


def explain(question, sql, columns, rows):
    """Ask Gemma to explain the result rows in plain language."""
    if not rows:
        return "The query ran successfully but returned no rows, so there is no data to answer this question."

    shown = rows[:20]  # keep the prompt short
    table_text = "\n".join(str(r) for r in shown)

    prompt = f"""You explain database results to a non-technical person.
Use ONLY the data below. Do not add any facts, numbers or names that are not in the data.
If the data does not fully answer the question, say so.
Write 2 to 4 short sentences. Do not mention SQL unless needed.

QUESTION: {question}
SQL THAT WAS RUN: {sql}
COLUMNS: {columns}
ROWS:
{table_text}

EXPLANATION:"""
    r = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )
    return r["message"]["content"].strip()
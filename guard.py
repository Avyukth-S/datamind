import os
import re
import ollama
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

CHANGE_WORDS = ["delete", "drop", "update", "insert", "remove", "truncate", "alter", "modify", "erase"]

VAGUE_WORDS = ["best", "worst", "good", "bad", "important", "popular", "biggest", "greatest", "top"]

MEASURE_WORDS = [
    "balance", "order", "orders", "count", "number", "total", "revenue", "price",
    "value", "spend", "spent", "quantity", "sales", "average", "sum", "how many",
    "per", "each", "by ", "most", "least", "highest", "lowest",
]

DATA_WORDS = [
    "customer", "order", "nation", "country", "countries", "region", "segment",
    "price", "balance", "lineitem", "shipment", "shipped", "market", "year",
    "month", "january", "february", "march", "april", "may", "june", "july",
    "august", "september", "october", "november", "december",
    "asia", "europe", "america", "africa", "middle east", "india", "china",
]


def has_word(text, words):
    for w in words:
        if w.endswith(" "):
            if w in text + " ":
                return True
        elif re.search(r"\b" + re.escape(w) + r"\b", text):
            return True
    return False


def check_question(question, schema):
    """Return (status, message). Status is OK, AMBIGUOUS or UNSUPPORTED."""
    q = question.lower().strip()

    # Rule 1: requests to change data
    if has_word(q, CHANGE_WORDS):
        return "UNSUPPORTED", "This assistant can only read data, not change or delete it."

    # Rule 2: vague words with no measure
    if has_word(q, VAGUE_WORDS) and not has_word(q, MEASURE_WORDS):
        return (
            "AMBIGUOUS",
            'What do you mean by "best" or "top"? For example: highest account balance, '
            "most orders, or highest total order value?",
        )

    # Rule 3: clearly about our data, so go ahead
    if has_word(q, DATA_WORDS):
        return "OK", ""

    # Rule 4: unclear, so ask Gemma (it may only say OK or UNSUPPORTED)
    prompt = f"""You are a gatekeeper for a database assistant.
The database is described below. Decide if the QUESTION could be answered from it.

Reply with exactly two lines:
Line 1: one word, OK or UNSUPPORTED
Line 2: a short message for the user (write "none" if OK)

UNSUPPORTED means the question is about something not in the database at all,
such as weather, news, sports or general knowledge.
When in doubt, answer OK.

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
    message = lines[1] if len(lines) > 1 else "This database cannot answer that."
    if first.startswith("UNSUPPORTED"):
        return "UNSUPPORTED", message
    return "OK", ""
import os
import ollama
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")


def check_question(question, schema):
    """Return (status, message). Status is OK, AMBIGUOUS or UNSUPPORTED."""
    prompt = f"""You are a gatekeeper for a database assistant.
Decide if the QUESTION can be answered with the database described below.

IMPORTANT: tables can be JOINED using the "links to" notes in the schema.
For example, customers can be grouped by country by joining CUSTOMER to NATION.
A question that needs a join, a count, a sum, an average or a ranking is still OK.

Reply with exactly two lines:
Line 1: one word, either OK, AMBIGUOUS or UNSUPPORTED
Line 2: a short message for the user (write "none" if OK)

Labels:
- OK: the question is clear and the data can answer it, directly or by joining tables.
- AMBIGUOUS: the question uses a vague word like "best" or "top" or "good" with no measure given.
- UNSUPPORTED: the question is about something not in the database at all (weather, news, people outside the data), or asks to change or delete data.

When in doubt, answer OK.

EXAMPLES:
Question: How many customers are in each market segment?
OK
none

Question: Which 5 countries have the most customers?
OK
none

Question: Total order value by region?
OK
none

Question: Show me the best customers
AMBIGUOUS
What do you mean by "best"? For example, highest account balance or most orders?

Question: What is the weather in Delhi?
UNSUPPORTED
This database has customers and orders, but no weather data.

Question: Delete all customers
UNSUPPORTED
This assistant can only read data, not change it.

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
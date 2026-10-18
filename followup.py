import os
import ollama
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")


def make_standalone(new_question, previous_question):
    """If new_question is a follow-up, rewrite it as a full question.
    Otherwise return it unchanged."""
    if not previous_question:
        return new_question

    prompt = f"""You rewrite follow-up questions for a database assistant.

PREVIOUS QUESTION: {previous_question}
NEW QUESTION: {new_question}

If the NEW QUESTION depends on the previous one (for example "what about Europe?",
"and the top 3?", "by account balance"), rewrite it as one complete standalone question.
If the NEW QUESTION already makes sense on its own, return it exactly as written.

Reply with only the question, on one line. No explanation.

EXAMPLES:
Previous: How many customers are in ASIA?
New: what about Europe?
Answer: How many customers are in EUROPE?

Previous: Which 5 countries have the most customers?
New: How many orders are there in total?
Answer: How many orders are there in total?

ANSWER:"""
    r = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )
    text = r["message"]["content"].strip().splitlines()
    rewritten = text[0].strip() if text else ""
    rewritten = rewritten.removeprefix("Answer:").strip()

    # Safety net: if the rewrite looks broken, use what the user typed
    if not rewritten or len(rewritten) > 300:
        return new_question
    return rewritten
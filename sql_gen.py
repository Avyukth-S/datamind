import os
import sys
import ollama
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")


def load_schema(path="schema_tpch.txt"):
    with open(path, encoding="utf-8") as f:
        return f.read()


def question_to_sql(question, schema):
    prompt = f"""You write Snowflake SQL queries.
Use ONLY the tables and columns described below.
Always use full table names like SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER.
Write only ONE read-only SELECT statement. Return only the SQL, with no explanation.

SCHEMA:
{schema}

QUESTION: {question}
SQL:"""
    r = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )
    sql = r["message"]["content"].strip()
    # Gemma often wraps SQL in ```sql ... ``` fences, so remove them
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "How many customers are there?"
    print("QUESTION:", question)
    print("SQL:")
    print(question_to_sql(question, load_schema()))
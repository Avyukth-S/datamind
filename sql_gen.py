import os
import sys
import ollama
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

# NOTE: no curly braces inside RULES, except none at all. Keep it that way.
RULES = """You write Snowflake SQL queries.

GENERAL RULES
- Use ONLY the tables and columns described in the schema below.
- Always use full table names like SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER.
- Write exactly ONE read-only SELECT statement.
- Return only the SQL. No explanation, no comments.
- This is Snowflake SQL. Do not use SQLite, MySQL or Postgres-only syntax.

DATE RULES (the date columns are O_ORDERDATE and L_SHIPDATE)
- Order dates only exist from 1992 to 1998.
- Year of a date: YEAR(O_ORDERDATE)
- Month of a date as a number 1 to 12: MONTH(O_ORDERDATE)
- Day of the month as a number 1 to 31: DAY(O_ORDERDATE)
- Months are numbers: January=1, February=2, March=3, April=4, May=5, June=6,
  July=7, August=8, September=9, October=10, November=11, December=12.
- Never compare MONTH() to a month name such as 'March'. Always use the number.
- NEVER use STRFTIME, strftime, DATE_FORMAT, EXTRACT with text formats,
  DATEADD, DATEDIFF or INTERVAL. Use YEAR, MONTH, DAY and date literals instead.
- A specific day is written as a date literal: O_ORDERDATE = '1995-03-15'
- A range of days uses BETWEEN with date literals:
  O_ORDERDATE BETWEEN '1995-03-01' AND '1995-03-31'
- A whole year: YEAR(O_ORDERDATE) = 1995
- A month in a year: YEAR(O_ORDERDATE) = 1995 AND MONTH(O_ORDERDATE) = 3
- A specific day using parts: YEAR(O_ORDERDATE) = 1995 AND MONTH(O_ORDERDATE) = 3 AND DAY(O_ORDERDATE) = 15

OTHER RULES
- Country names in NATION.N_NAME are uppercase, for example 'INDIA'.
- Region names in REGION.R_NAME are uppercase, for example 'EUROPE'.
- Market segments in CUSTOMER.C_MKTSEGMENT are uppercase, for example 'BUILDING'.
- Customers link to orders through O_CUSTKEY = C_CUSTKEY.
- Customers link to countries through C_NATIONKEY = N_NATIONKEY.
- Countries link to regions through N_REGIONKEY = R_REGIONKEY.
- For "top N" questions use ORDER BY ... DESC LIMIT N.

EXAMPLES
Question: How many orders were placed in 1995?
SQL: SELECT COUNT(*) FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS WHERE YEAR(O_ORDERDATE) = 1995

Question: How many orders were placed in March 1995?
SQL: SELECT COUNT(*) FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS WHERE YEAR(O_ORDERDATE) = 1995 AND MONTH(O_ORDERDATE) = 3

Question: How many orders were placed on 15 March 1995?
SQL: SELECT COUNT(*) FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS WHERE O_ORDERDATE = '1995-03-15'

Question: Orders per month in 1996
SQL: SELECT MONTH(O_ORDERDATE) AS ORDER_MONTH, COUNT(*) AS ORDER_COUNT FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS WHERE YEAR(O_ORDERDATE) = 1996 GROUP BY MONTH(O_ORDERDATE) ORDER BY ORDER_MONTH

Question: How many orders were placed in India in March 1995?
SQL: SELECT COUNT(*) FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS O JOIN SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER C ON O.O_CUSTKEY = C.C_CUSTKEY JOIN SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.NATION N ON C.C_NATIONKEY = N.N_NATIONKEY WHERE N.N_NAME = 'INDIA' AND YEAR(O.O_ORDERDATE) = 1995 AND MONTH(O.O_ORDERDATE) = 3

Question: Total order value between 1 January 1994 and 31 January 1994
SQL: SELECT SUM(O_TOTALPRICE) AS TOTAL_VALUE FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS WHERE O_ORDERDATE BETWEEN '1994-01-01' AND '1994-01-31'
"""


def load_schema(path="schema_tpch.txt"):
    with open(path, encoding="utf-8") as f:
        return f.read()


def clean_sql(text):
    """Remove code fences, a leading 'SQL:' label and trailing semicolons."""
    sql = text.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    if sql.upper().startswith("SQL:"):
        sql = sql[4:].strip()
    return sql.rstrip().rstrip(";").strip()


def question_to_sql(question, schema, previous_error=None, previous_sql=None):
    """Ask Gemma for SQL. If a previous attempt failed, pass its error so
    Gemma can correct it."""
    prompt = RULES + "\nSCHEMA:\n" + schema + "\n"

    if previous_error and previous_sql:
        prompt += (
            "\nYour previous SQL failed.\n"
            "PREVIOUS SQL: " + previous_sql + "\n"
            "ERROR: " + previous_error + "\n"
            "Write a corrected Snowflake SQL query that fixes this error.\n"
        )

    prompt += "\nQUESTION: " + question + "\nSQL:"

    r = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )
    return clean_sql(r["message"]["content"])


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "How many customers are there?"
    print("QUESTION:", question)
    print("SQL:")
    print(question_to_sql(question, load_schema()))
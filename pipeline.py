import sys
from sql_gen import question_to_sql, load_schema
from safety import check_sql
from sf_runner import run_query


def answer(question):
    schema = load_schema()
    sql = question_to_sql(question, schema)
    sql = sql.rstrip().rstrip(";")  # remove trailing semicolon

    ok, reason = check_sql(sql)
    if not ok:
        return {"sql": sql, "error": "Blocked: " + reason}

    try:
        columns, rows, query_id = run_query(sql)
    except Exception as e:
        return {"sql": sql, "error": f"Snowflake error: {e}"}

    return {"sql": sql, "columns": columns, "rows": rows, "query_id": query_id}


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "How many customers are there?"
    result = answer(question)

    print("QUESTION:", question)
    print("SQL:", result["sql"])
    if "error" in result:
        print("ERROR:", result["error"])
    else:
        print("QUERY ID:", result["query_id"])
        print("COLUMNS:", result["columns"])
        for row in result["rows"]:
            print(row)
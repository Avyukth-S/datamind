import sqlglot
from sqlglot import exp


def check_sql(sql):
    """Return (True, "") if the SQL is one read-only SELECT, else (False, reason)."""
    try:
        statements = sqlglot.parse(sql, read="snowflake")
    except Exception as e:
        return False, f"Could not parse the SQL: {e}"

    statements = [s for s in statements if s is not None]
    if len(statements) != 1:
        return False, "Exactly one SQL statement is allowed."

    tree = statements[0]
    if not isinstance(tree, (exp.Select, exp.Union)):
        return False, "Only SELECT queries are allowed."

    banned = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create, exp.Alter, exp.Command)
    for node in tree.walk():
        if isinstance(node, banned):
            return False, "This query tries to change data, which is not allowed."

    return True, ""
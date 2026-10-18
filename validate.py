import sqlglot
from sqlglot import exp


def parse_schema(schema_text):
    """Read lines like 'Table CUSTOMER: C_CUSTKEY (id), C_NAME, ...'
    and return {table_name: {column names}}."""
    tables = {}
    for line in schema_text.splitlines():
        line = line.strip()
        if not line.startswith("Table "):
            continue
        name, _, rest = line[len("Table "):].partition(":")
        items, current, depth = [], "", 0
        for ch in rest:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if ch == "," and depth == 0:
                items.append(current)
                current = ""
            else:
                current += ch
        items.append(current)
        columns = {i.strip().split(" ")[0].upper() for i in items if i.strip()}
        tables[name.strip().upper()] = columns
    return tables


def validate_sql(sql, schema_text):
    """Return (True, "") if every table and column exists in the schema."""
    tables = parse_schema(schema_text)
    known_columns = set().union(*tables.values()) if tables else set()

    try:
        tree = sqlglot.parse_one(sql, read="snowflake")
    except Exception as e:
        return False, f"Could not parse the SQL: {e}"

    # Names the query defines itself (AS aliases and WITH names) are allowed
    own_names = {a.alias.upper() for a in tree.find_all(exp.Alias)}
    own_names |= {c.alias_or_name.upper() for c in tree.find_all(exp.CTE)}

    for t in tree.find_all(exp.Table):
        if t.name.upper() not in tables and t.name.upper() not in own_names:
            return False, f"Unknown table: {t.name}"

    for c in tree.find_all(exp.Column):
        if c.name.upper() not in known_columns and c.name.upper() not in own_names:
            return False, f"Unknown column: {c.name}"

    return True, ""
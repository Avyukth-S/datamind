import math
from decimal import Decimal
from pipeline import answer
from sf_runner import run_query

P = "SNOWFLAKE_SAMPLE_DATA.TPCH_SF1."

TESTS = [
    {"q": "How many customers are there?",
     "sql": f"SELECT COUNT(*) FROM {P}CUSTOMER"},
    {"q": "How many orders were placed in 1995?",
     "sql": f"SELECT COUNT(*) FROM {P}ORDERS WHERE YEAR(O_ORDERDATE) = 1995"},
    {"q": "How many orders were placed in March 1995?",
     "sql": f"SELECT COUNT(*) FROM {P}ORDERS WHERE YEAR(O_ORDERDATE) = 1995 AND MONTH(O_ORDERDATE) = 3"},
    {"q": "How many customers are in EUROPE?",
     "sql": f"SELECT COUNT(*) FROM {P}CUSTOMER C JOIN {P}NATION N ON C.C_NATIONKEY = N.N_NATIONKEY JOIN {P}REGION R ON N.N_REGIONKEY = R.R_REGIONKEY WHERE R.R_NAME = 'EUROPE'"},
    {"q": "How many orders were placed in India in March 1998?",
     "sql": f"SELECT COUNT(*) FROM {P}ORDERS O JOIN {P}CUSTOMER C ON O.O_CUSTKEY = C.C_CUSTKEY JOIN {P}NATION N ON C.C_NATIONKEY = N.N_NATIONKEY WHERE N.N_NAME = 'INDIA' AND YEAR(O.O_ORDERDATE) = 1998 AND MONTH(O.O_ORDERDATE) = 3"},
    {"q": "Which 3 nations have the highest total order value?",
     "sql": f"SELECT N.N_NAME, SUM(O.O_TOTALPRICE) FROM {P}ORDERS O JOIN {P}CUSTOMER C ON O.O_CUSTKEY = C.C_CUSTKEY JOIN {P}NATION N ON C.C_NATIONKEY = N.N_NATIONKEY GROUP BY N.N_NAME ORDER BY 2 DESC LIMIT 3"},
    {"q": "What is the average account balance per market segment?",
     "sql": f"SELECT C_MKTSEGMENT, AVG(C_ACCTBAL) FROM {P}CUSTOMER GROUP BY C_MKTSEGMENT"},
    {"q": "What is the total revenue after discount for items shipped in 1996?",
     "sql": f"SELECT SUM(L_EXTENDEDPRICE * (1 - L_DISCOUNT)) FROM {P}LINEITEM WHERE YEAR(L_SHIPDATE) = 1996"},
    {"q": "How many customers have never placed an order?",
     "sql": f"SELECT COUNT(*) FROM {P}CUSTOMER C WHERE NOT EXISTS (SELECT 1 FROM {P}ORDERS O WHERE O.O_CUSTKEY = C.C_CUSTKEY)"},
    {"q": "What percentage of all orders have status F?",
     "sql": f"SELECT 100.0 * COUNT_IF(O_ORDERSTATUS = 'F') / COUNT(*) FROM {P}ORDERS"},
    {"q": "Show me the best customers", "expect_status": "ambiguous"},
    {"q": "What is the weather in Delhi today?", "expect_status": "unsupported"},
    {"q": "Delete all customers", "expect_status": "unsupported"},
    {"q": "What is the average age of our customers?", "expect_status": "not_ok"},
]


def norm(v):
    if isinstance(v, (Decimal, float)):
        return float(v)
    return v


def norm_rows(rows):
    out = [tuple(norm(v) for v in r) for r in rows]
    return sorted(out, key=lambda r: str(r[0]) if r else "")


def same(a, b):
    if len(a) != len(b):
        return False
    for ra, rb in zip(a, b):
        if len(ra) != len(rb):
            return False
        for x, y in zip(ra, rb):
            if isinstance(x, float) or isinstance(y, float):
                try:
                    if not math.isclose(float(x), float(y), rel_tol=1e-3, abs_tol=0.01):
                        return False
                except (TypeError, ValueError):
                    return False
            elif x != y:
                return False
    return True


lines = [
    "| # | Question | Result | Note |",
    "|---|---|---|---|",
]
passed = 0

for i, t in enumerate(TESTS, 1):
    q = t["q"]
    print(f"[{i}/{len(TESTS)}] {q}")
    try:
        res = answer(q)
    except Exception as e:
        lines.append(f"| {i} | {q} | FAIL | Crashed: {str(e)[:60]} |")
        continue

    if "expect_status" in t:
        want = t["expect_status"]
        got = res["status"]
        ok = (got != "ok") if want == "not_ok" else (got == want)
        passed += ok
        lines.append(f"| {i} | {q} | {'PASS' if ok else 'FAIL'} | Expected {want}, got {got} |")
        continue

    if res["status"] != "ok":
        lines.append(f"| {i} | {q} | FAIL | Status {res['status']}: {res['message'][:60]} |")
        continue

    _, exp_rows, _ = run_query(t["sql"])
    ok = same(norm_rows(res["rows"]), norm_rows(exp_rows))
    passed += ok
    note = "Matches Snowflake ground truth" if ok else "Differs from ground truth, see SQL panel"
    lines.append(f"| {i} | {q} | {'PASS' if ok else 'FAIL'} | {note} |")

summary = f"\n**Score: {passed} of {len(TESTS)} passed**\n"
report = "\n".join(lines) + "\n" + summary

with open("eval_results.md", "w", encoding="utf-8") as f:
    f.write(report)

print()
print(report)
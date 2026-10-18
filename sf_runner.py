import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()


def run_query(sql):
    """Run SQL on Snowflake. Return (column_names, rows)."""
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database="SNOWFLAKE_SAMPLE_DATA",
        schema="TPCH_SF1",
        server_session_keep_alive_auto_detection=False,
    )
    try:
        cur = conn.cursor()
        cur.execute(sql)
        columns = [c[0] for c in cur.description]
        rows = cur.fetchmany(100)  # never pull more than 100 rows
        query_id = cur.sfqid
        return columns, rows, query_id
    finally:
        conn.close()
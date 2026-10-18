from sql_gen import load_schema
from validate import validate_sql

schema = load_schema()

good = "SELECT N.N_NAME, COUNT(*) AS CNT FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER C JOIN SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.NATION N ON C.C_NATIONKEY = N.N_NATIONKEY GROUP BY N.N_NAME ORDER BY CNT DESC LIMIT 5"
bad_column = "SELECT C_COUNTRY FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER"
bad_table = "SELECT * FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.EMPLOYEES"

print("good:      ", validate_sql(good, schema))
print("bad column:", validate_sql(bad_column, schema))
print("bad table: ", validate_sql(bad_table, schema))
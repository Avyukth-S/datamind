import os
import ollama
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    role=os.getenv("SNOWFLAKE_ROLE"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER")
print("Snowflake OK, customers:", cur.fetchone()[0])

model = os.getenv("OLLAMA_MODEL", "gemma3:4b")
r = ollama.chat(model=model, messages=[{"role": "user", "content": "Say hello in five words."}])
print("Gemma OK:", r["message"]["content"])
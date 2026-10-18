# DataMind: Talk to Your Data

Ask questions about data in plain English. Gemma writes the SQL, Snowflake runs it,
and every answer shows its evidence (SQL, query ID, result rows).

## How it works

Question -> Gemma gatekeeper -> Gemma writes SQL -> read-only check -> schema check
-> Snowflake runs it -> Gemma explains the rows -> Streamlit shows answer + evidence

- **Gemma (gemma3:4b via Ollama, runs locally):** gatekeeper, SQL writer, follow-up rewriter, explainer.
- **Snowflake:** stores the data and runs every query. Gemma never computes numbers.

## Setup

1. Install Python 3.11, Git and Ollama.
2. Download the model: `ollama pull gemma3:4b`
3. Create a Snowflake trial account at signup.snowflake.com, then run in a worksheet:

   CREATE WAREHOUSE IF NOT EXISTS DATAMIND_WH WAREHOUSE_SIZE='XSMALL' AUTO_SUSPEND=60 AUTO_RESUME=TRUE;
   CREATE ROLE IF NOT EXISTS DATAMIND_READER;
   GRANT USAGE ON WAREHOUSE DATAMIND_WH TO ROLE DATAMIND_READER;
   GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE_SAMPLE_DATA TO ROLE DATAMIND_READER;
   GRANT ROLE DATAMIND_READER TO USER AVYUKTH;

4. Clone and install:

   git clone https://github.com/Avyukth-S/datamind.git
   cd datamind
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt

5. Copy `.env.example` to `.env` and fill in your Snowflake account, user and password.
6. Run: `streamlit run app.py`

## Dataset

Snowflake sample data SNOWFLAKE_SAMPLE_DATA.TPCH_SF1 (TPC-H benchmark). It is not copied
into this repo; it is used inside the Snowflake account. No open licence is stated for it.

## Safeguards

- Gatekeeper asks for clarification on vague questions and refuses unsupported ones.
- sqlglot allows only a single read-only SELECT.
- Schema check rejects unknown tables and columns.
- Read-only Snowflake role, 100-row cap, XSMALL warehouse with 60 s auto-suspend.
- Empty results get a fixed message (Gemma is not asked to explain nothing).
- Follow-up questions are rewritten, and the rewrite is shown to the user.

## Known limitations

- A 4B model can write logically wrong SQL (for example a wrong join). The schema check
  only verifies that names exist, so the SQL and rows are shown for the user to verify.
- The gatekeeper is a small model's judgement and can wrongly accept or refuse.
- Questions are slow on a laptop (several Gemma calls each).
- Only one dataset is configured; the schema is in schema_tpch.txt but there is no
  config.yaml yet.
- No formal evaluation set yet; answers were checked by hand against Snowflake.

## Environment tested

Windows, Python 3.11, Ollama, gemma3:4b, Snowflake trial account.

## Main contribution

A layered pipeline that keeps language tasks (Gemma) separate from deterministic
execution (Snowflake), with validation at each step and evidence for every answer.

## Licence

See the LICENSE file.

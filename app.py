import pandas as pd
import streamlit as st
from pipeline import answer

st.set_page_config(page_title="DataMind", page_icon="🧠")

st.title("DataMind: talk to your data")
st.write("Ask a question about the TPC-H sample data (customers, orders, nations, regions).")

question = st.text_input("Your question", placeholder="Which 5 countries have the most customers?")

if st.button("Ask") and question.strip():
    with st.spinner("Thinking... (Gemma and Snowflake are working)"):
        result = answer(question)

    status = result["status"]

    if status == "ok":
        st.success(result["explanation"])

        df = pd.DataFrame(result["rows"], columns=result["columns"])

        st.subheader("Evidence")

        with st.expander("How this answer was obtained", expanded=True):
            st.markdown(
                "1. Gemma turned your question into a SQL query.\n"
                "2. A safety check confirmed it is a single read-only SELECT "
                "and uses only known tables and columns.\n"
                f"3. Snowflake ran the query and returned **{len(df)} row(s)**.\n"
                "4. Gemma explained those rows in plain language."
            )
            if len(df) == 100:
                st.caption("Note: results are capped at 100 rows.")

        with st.expander("SQL that ran in Snowflake"):
            st.code(result["sql"], language="sql")
            st.caption(f"Snowflake query ID: {result['query_id']}")

        with st.expander("Result rows", expanded=True):
            st.dataframe(df, use_container_width=True)

    elif status == "ambiguous":
        st.warning("I need a bit more detail: " + result["message"])
    elif status == "unsupported":
        st.info("I can't answer that: " + result["message"])
    else:
        st.error(result["message"])
        if "sql" in result:
            with st.expander("SQL that was blocked or failed"):
                st.code(result["sql"], language="sql")
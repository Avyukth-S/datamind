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
    elif status == "ambiguous":
        st.warning("I need a bit more detail: " + result["message"])
    elif status == "unsupported":
        st.info("I can't answer that: " + result["message"])
    else:
        st.error(result["message"])
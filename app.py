import streamlit as st
import pandas as pd
import os
from graph.agent import build_graph
from utils.profiler import profile_dataset, format_profile
from utils.report import generate_report

# Page config
st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Data Analyst Agent")
st.markdown("Upload a dataset and ask questions in plain English.")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Sidebar - API key input
with st.sidebar:
    st.header("🔑 Settings")
    api_key = st.text_input("Enter your Groq API Key", type="password")
    st.markdown("[Get your free API key here](https://console.groq.com)")

    if api_key:
        st.session_state["api_key"] = api_key
        st.success("API key saved!")

    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state["chat_history"] = []
        st.session_state["messages"] = []
        st.rerun()

    # Download report button
    if "df" in st.session_state and st.session_state["chat_history"]:
        st.markdown("---")
        if st.button("📥 Download Report (PDF)"):
            profile = profile_dataset(st.session_state["df"])
            formatted = format_profile(profile)

            pdf_path = generate_report(
                profile=profile,
                formatted_profile=formatted,
                chat_history=st.session_state["chat_history"],
            )

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="💾 Save Report",
                    data=f,
                    file_name="analysis_report.pdf",
                    mime="application/pdf",
                )

# File upload
uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Read the file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.session_state["df"] = df

    # Show preview
    st.subheader("📋 Data Preview")
    st.dataframe(df.head(10))

    # Auto-profiler
    profile = profile_dataset(df)
    formatted = format_profile(profile)

    st.subheader("🔍 Auto-Insights")
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", profile["rows"])
    col2.metric("Columns", profile["columns"])
    col3.metric("Missing Values", len(profile["missing"]))

    with st.expander("📊 Full Dataset Profile", expanded=True):
        st.markdown(formatted)

    # Chat section
    st.subheader("💬 Chat with Your Data")

    # Display previous messages
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "chart" in msg and msg["chart"] is not None:
                st.plotly_chart(msg["chart"], use_container_width=True)
            if "code" in msg:
                with st.expander("🔍 View Generated Code"):
                    st.code(msg["code"], language="python")
                    if msg.get("retries", 0) > 0:
                        st.info(f"🔧 Self-healed! Code was auto-fixed after {msg['retries']} retry(s).")

    # Chat input
    query = st.chat_input("Ask a question about your data...")

    if query and "api_key" in st.session_state:
        # Show user message
        st.session_state["messages"].append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        # Run agent
        with st.chat_message("assistant"):
            with st.spinner("🤖 Analyzing..."):
                agent = build_graph()

                initial_state = {
                    "query": query,
                    "api_key": st.session_state["api_key"],
                    "df": df,
                    "columns_info": str(list(df.columns)),
                    "sample_data": df.head(3).to_string(),
                    "route": "",
                    "generated_code": "",
                    "code_output": "",
                    "error": "",
                    "retry_count": 0,
                    "chart": None,
                    "summary": "",
                    "chat_history": st.session_state["chat_history"],
                }

                result = agent.invoke(initial_state)

            # Display results
            if result["summary"]:
                st.markdown(result["summary"])
            if result["chart"]:
                st.plotly_chart(result["chart"], use_container_width=True)
            with st.expander("🔍 View Generated Code"):
                st.code(result["generated_code"], language="python")
                if result["retry_count"] > 0:
                    st.info(f"🔧 Self-healed! Code was auto-fixed after {result['retry_count']} retry(s).")

            # Save assistant message
            st.session_state["messages"].append({
                "role": "assistant",
                "content": result["summary"],
                "chart": result["chart"],
                "code": result["generated_code"],
                "retries": result["retry_count"],
            })

            # Update chat history for context
            st.session_state["chat_history"].append({
                "query": query,
                "result": result["code_output"],
                "summary": result["summary"],
            })

    elif query and "api_key" not in st.session_state:
        st.warning("⚠️ Please enter your Groq API key in the sidebar first.")
else:
    st.info("👆 Upload a CSV or Excel file to get started.")

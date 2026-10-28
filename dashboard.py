import streamlit as st
import pandas as pd
import os

# Set up the page layout
st.set_page_config(page_title="AI Job Pipeline", page_icon="🤖", layout="wide")
st.title("🤖 Autonomous Job Application Dashboard")

# Define the path to your log file
LOG_FILE = "data/applications_log.csv"

if not os.path.exists(LOG_FILE):
    st.warning("No data found yet! Run your LangGraph pipeline to generate logs.")
else:
    # Load the data
    df = pd.read_csv(LOG_FILE)
    
    # --- Top Level Metrics ---
    st.subheader("Pipeline Overview")
    col1, col2, col3 = st.columns(3)
    
    total_jobs = len(df)
    successful_apps = len(df[df['Status'] == 'Success'])
    avg_ats = df['ATS Score'].mean() if not df['ATS Score'].isnull().all() else 0
    
    col1.metric("Total Jobs Evaluated", total_jobs)
    col2.metric("Successful Applications", successful_apps)
    col3.metric("Average ATS Score", f"{avg_ats:.1f} / 100")
    
    # --- Detailed Table ---
    st.markdown("---")
    st.subheader("Application History")
    
    # Add a search bar to filter jobs
    search = st.text_input("🔍 Search by Company or Title")
    if search:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
        
    # Display the dataframe as an interactive table
    st.dataframe(
        df,
        column_config={
            "ATS Score": st.column_config.ProgressColumn("ATS Score", format="%f", min_value=0, max_value=100),
            "Status": st.column_config.TextColumn("Status"),
        },
        use_container_width=True,
        hide_index=True
    )
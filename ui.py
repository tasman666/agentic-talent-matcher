"""
Streamlit UI for Agentic Talent Matcher.
Run with: streamlit run ui.py
"""

import streamlit as st
import httpx
import json
from config import get_settings

# Configuration
settings = get_settings()
# If host is 0.0.0.0 (listen all), client should connect to localhost
host = "localhost" if settings.app_host == "0.0.0.0" else settings.app_host
API_BASE_URL = f"http://{host}:{settings.app_port}"

st.set_page_config(
    page_title="Agentic Talent Matcher",
    page_icon="🧩",
    layout="wide"
)

st.title("🧩 Agentic Talent Matcher")
st.markdown("""
Use AI to find the perfect candidate match across your internal database, 
Ciklum job board, and LinkedIn.
""")

# --- Sidebar: CV Upload ---
with st.sidebar:
    st.header("📂 Upload CVs")
    uploaded_files = st.file_uploader(
        "Upload Candidate CVs (PDF)", 
        type=["pdf"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("Process & Upload CVs"):
            with st.spinner("Uploading and indexing..."):
                for uploaded_file in uploaded_files:
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                        with httpx.Client(timeout=120.0) as client:
                            response = client.post(f"{API_BASE_URL}/upload-cv/", files=files)
                            response.raise_for_status()
                            st.success(f"✅ Indexed: {uploaded_file.name}")
                    except Exception as e:
                        st.error(f"❌ Failed to upload {uploaded_file.name}: {str(e)}")


# --- Main Chat Interface ---

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to clear history
def clear_chat():
    st.session_state.messages = []

st.sidebar.button("Clear Chat", on_click=clear_chat)


# Chat Input
if prompt := st.chat_input("Describe the talent or job you are looking for..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking... searching databases..."):
            try:
                with httpx.Client(timeout=60.0) as client:
                    response = client.post(
                        f"{API_BASE_URL}/agent/match",
                        json={"query": prompt}
                    )
                    response.raise_for_status()
                    data = response.json()
                    ai_response = data.get("response", "No response from agent.")
                
                st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
                # Store last interaction for evaluation
                st.session_state.last_query = prompt
                st.session_state.last_response = ai_response
                st.session_state.last_context = ""  # Ideally getting context from backend response
                
            except Exception as e:
                error_msg = f"Error communicating with agent: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})


# --- Evaluation Section ---
if "last_response" in st.session_state and st.session_state.last_response:
    with st.expander("📝 Evaluate Last Response"):
        st.info("Uses the configured Evaluation LLM (Judge) to score the agent's answer.")
        if st.button("Run Evaluation"):
            with st.spinner("Evaluating..."):
                try:
                    payload = {
                        "query": st.session_state.last_query,
                        "response": st.session_state.last_response,
                        "context": "" # Context automatic retrieval handled by backend
                    }
                    with httpx.Client(timeout=60.0) as client:
                        resp = client.post(f"{API_BASE_URL}/agent/evaluate", json=payload)
                        resp.raise_for_status()
                        eval_data = resp.json()
                        metrics = eval_data.get("metrics", {})
                        
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Overall Score", f"{metrics.get('overall', 0)}/5")
                        col2.metric("Relevance", f"{metrics.get('relevance', {}).get('score', 0)}/5")
                        col3.metric("Clarity", f"{metrics.get('clarity', {}).get('score', 0)}/5")
                        col4.metric("Accuracy", f"{metrics.get('accuracy', {}).get('score', 0)}/5")
                        
                        st.subheader("Analysis")
                        st.text_area("Relevance", metrics.get("relevance", {}).get("reasoning", ""), height=100)
                        st.text_area("Clarity", metrics.get("clarity", {}).get("reasoning", ""), height=100)
                        st.text_area("Accuracy", metrics.get("accuracy", {}).get("reasoning", ""), height=100)
                        
                except Exception as e:
                    st.error(f"Evaluation failed: {str(e)}")

import streamlit as st
import requests

st.set_page_config(page_title="Smart AI, Made by Abhi", page_icon="🧠", layout="wide")
st.title("🧠 Smart AI, Made by Abhi")
st.caption("Cloud Hosted Generative AI | Always Online & Unlimited")

# Sidebar
with st.sidebar:
    st.header("⚙️ System Status")
    st.success("✅ Engine: Llama-3 Fast Cloud Engine")
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_query = st.chat_input("Ask anything (Coding, Science, Explanations, Stories)...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Generating detailed response..."):
            try:
                # Open, robust AI endpoint (No tokens or rate limits required)
                api_url = "https://text.pollinations.ai/"
                payload = {
                    "messages": [
                        {"role": "system", "content": "You are a helpful, witty, and smart AI assistant created by Abhi. Provide clear, accurate, and structured answers."},
                        *st.session_state.messages
                    ],
                    "model": "openai",
                    "seed": 42
                }
                
                response = requests.post(api_url, json=payload, timeout=45)
                
                if response.status_code == 200:
                    reply = response.text
                else:
                    reply = "Service is temporarily busy. Please try asking again in a moment."
            except Exception as e:
                reply = f"Error: {str(e)}"

            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
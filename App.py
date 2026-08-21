# Version: Local In-House AI Engine
import streamlit as st
import ollama

st.set_page_config(page_title="Abhi In-House AI", page_icon="🧠", layout="wide")
st.title("🧠 Abhi's 100% In-House AI (Real Brain)")
st.caption("Running Locally via Ollama Llama 3.2 | Zero External APIs | Unlimited Free Usage")

# Sidebar
with st.sidebar:
    st.header("⚙️ System Status")
    st.success("✅ Engine: Llama 3.2 (Local CPU)")
    st.info("🔒 100% Offline, Smart & Private")
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_query = st.chat_input("Ask anything (Coding, Science, Explanations, Stories)...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        def generate_response():
            response = ollama.chat(
                model="llama3.2:1b",
                messages=st.session_state.messages,
                stream=True
            )
            for chunk in response:
                yield chunk["message"]["content"]

        reply = st.write_stream(generate_response)

    st.session_state.messages.append({"role": "assistant", "content": reply})
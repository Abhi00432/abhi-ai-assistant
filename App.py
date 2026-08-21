import streamlit as st
import requests

st.set_page_config(page_title="Smart AI, Made by Abhi", page_icon="🧠", layout="wide")
st.title("🧠 Smart AI, Made by Abhi")
st.caption("Powered by Abhi's Local Ollama Hardware Engine | Globally Live")

# अपनी Cloudflare वाली लिंक यहाँ पेस्ट करें (लास्ट में / न लगाएं)
OLLAMA_SERVER_URL = "https://citizens-childrens-developing-ind.trycloudflare.com  "

with st.sidebar:
    st.header("⚙️ System Status")
    st.success("✅ Engine: Abhi's Local Llama 3.2 Hardware")
    st.info("🔒 100% In-House Hardware")
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_query = st.chat_input("Ask anything to Abhi's In-House AI...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Processing on Abhi's laptop processor..."):
            try:
                payload = {
                    "model": "llama3.2:1b",
                    "messages": st.session_state.messages,
                    "stream": False
                }
                
                res = requests.post(f"{OLLAMA_SERVER_URL}/api/chat", json=payload, timeout=60)
                
                if res.status_code == 200:
                    reply = res.json()["message"]["content"]
                else:
                    reply = f"Error: Status code {res.status_code}"
            except Exception as e:
                reply = "⚠️ Hardware tunnel is offline. Ensure Cloudflare tunnel is running on laptop."

            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
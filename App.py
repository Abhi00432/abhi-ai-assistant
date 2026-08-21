import streamlit as st
import requests
import json

st.set_page_config(page_title="Smart AI, Made by Abhi", page_icon="🧠", layout="wide")
st.title("🧠 Smart AI, Made by Abhi")
st.caption("Powered by Abhi's Local Ollama Hardware Engine | Streaming Live")

OLLAMA_SERVER_URL = "https://directive-asks-trance-subjects.trycloudflare.com"

with st.sidebar:
    st.header("⚙️ System Status")
    st.info("⚡ Live Streaming Active")
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
        payload = {
            "model": "llama3.2:1b",
            "messages": st.session_state.messages,
            "stream": True
        }
        
        def stream_response():
            try:
                with requests.post(f"{OLLAMA_SERVER_URL}/api/chat", json=payload, stream=True, timeout=120) as r:
                    if r.status_code == 200:
                        for line in r.iter_lines():
                            if line:
                                data = json.loads(line.decode("utf-8"))
                                yield data.get("message", {}).get("content", "")
                    else:
                        yield f"Error: Status code {r.status_code}"
            except Exception as e:
                yield f"⚠️ Tunnel connection issue: {str(e)}"

        full_reply = st.write_stream(stream_response)

    st.session_state.messages.append({"role": "assistant", "content": full_reply})
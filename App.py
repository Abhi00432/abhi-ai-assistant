import streamlit as st
import requests

st.set_page_config(page_title="Smart AI, Made by Abhi", page_icon="🧠", layout="wide")
st.title("🧠 Smart AI, Made by Abhi")
st.caption("Powered by Abhi's In-House Ollama Engine | Globally Live")

# आपकी एक्टिव टनल लिंक
OLLAMA_SERVER_URL = "https://directive-asks-trance-subjects.trycloudflare.com"

with st.sidebar:
    st.header("⚙️ System Status")
    st.success("✅ Engine: Abhi's Local Llama 3.2 Hardware")
    st.info("🔒 100% In-House Processing")
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
                
                # Timeout बढ़कर 180s कर दिया ताकि बड़ा जवाब भी कैंसिल न हो
                res = requests.post(
                    f"{OLLAMA_SERVER_URL}/api/chat", 
                    json=payload, 
                    timeout=180
                )
                
                if res.status_code == 200:
                    reply = res.json()["message"]["content"]
                else:
                    reply = f"Error: Status code {res.status_code}"
            except requests.exceptions.Timeout:
                reply = "⚠️ Processor is taking time to compute. Please try a shorter query."
            except Exception as e:
                reply = f"⚠️ Tunnel connection issue: {str(e)}"

            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
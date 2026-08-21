import streamlit as st
import os
import requests

st.set_page_config(page_title="Smart AI, Made by Abhi", page_icon="🧠", layout="wide")
st.title("🧠 Smart AI, Made by Abhi")
st.caption("Cloud Hosted Generative AI | Always Online")

# Sidebar
with st.sidebar:
    st.header("⚙️ System Status")
    st.success("✅ Engine: Qwen-2.5 Cloud Engine")
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
        with st.spinner("Generating answer..."):
            API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-1.5B-Instruct"
            payload = {
                "inputs": f"<|im_start|>user\n{user_query}<|im_end|>\n<|im_start|>assistant\n",
                "parameters": {"max_new_tokens": 512, "temperature": 0.7}
            }
            
            try:
                response = requests.post(API_URL, json=payload, timeout=30)
                result = response.json()
                
                if isinstance(result, list) and len(result) > 0:
                    raw_text = result[0].get("generated_text", "")
                    reply = raw_text.split("<|im_start|>assistant\n")[-1].replace("<|im_end|>", "").strip()
                else:
                    reply = "Server is warming up, please ask again in 10 seconds!"
            except Exception as e:
                reply = f"Connection error: {str(e)}"

            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
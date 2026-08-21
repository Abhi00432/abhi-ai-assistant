import streamlit as st
import requests
import json
import sqlite3
import hashlib
from datetime import datetime

st.set_page_config(page_title="Smart AI, Made by Abhi", page_icon="🧠", layout="wide")

# --- Database Setup ---
conn = sqlite3.connect("ai_assistant.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT,
    created_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    role TEXT,
    content TEXT,
    timestamp TEXT
)
""")
conn.commit()

# --- Helper Functions ---
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_chats(email):
    cursor.execute("SELECT role, content FROM chat_history WHERE user_email = ? ORDER BY id ASC", (email,))
    return [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]

def save_chat_message(email, role, content):
    cursor.execute("INSERT INTO chat_history (user_email, role, content, timestamp) VALUES (?, ?, ?, ?)",
                   (email, role, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

def clear_user_history(email):
    cursor.execute("DELETE FROM chat_history WHERE user_email = ?", (email,))
    conn.commit()

# --- Session Management ---
if "user_email" not in st.session_state:
    st.session_state.user_email = None

OLLAMA_SERVER_URL = "https://directive-asks-trance-subjects.trycloudflare.com"

# --- Authentication Screen ---
if not st.session_state.user_email:
    st.title("🧠 Smart AI - Login / Sign Up")
    st.caption("Sign in with your Gmail to save and access your chat history.")
    
    auth_choice = st.radio("Choose Action", ["Login with Gmail", "Create New Account"], horizontal=True)
    
    with st.form("auth_form"):
        email = st.text_input("Gmail Address", placeholder="yourname@gmail.com").strip().lower()
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Submit")
        
        if submit:
            if not email.endswith("@gmail.com"):
                st.error("Please enter a valid @gmail.com address.")
            elif not password:
                st.error("Password cannot be empty.")
            else:
                if auth_choice == "Create New Account":
                    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                    if cursor.fetchone():
                        st.error("Account with this Gmail already exists. Please login.")
                    else:
                        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", 
                                       (email, hash_pass(password), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()
                        st.success("Account created successfully! Please switch to Login.")
                else:
                    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hash_pass(password)))
                    if cursor.fetchone():
                        st.session_state.user_email = email
                        st.session_state.messages = get_user_chats(email)
                        st.rerun()
                    else:
                        st.error("Invalid Gmail or password.")

# --- Main App (Logged In) ---
else:
    st.title("🧠 Smart AI, Made by Abhi")
    st.caption(f"Logged in as: **{st.session_state.user_email}** | Hardware Engine Active")

    # Load messages
    if "messages" not in st.session_state:
        st.session_state.messages = get_user_chats(st.session_state.user_email)

    with st.sidebar:
        st.header("👤 User Profile")
        st.write(f"📧 **ID:** `{st.session_state.user_email}`")
        st.success("✅ Database Connected")
        
        if st.button("🗑️ Clear My Chat History", use_container_width=True):
            clear_user_history(st.session_state.user_email)
            st.session_state.messages = []
            st.rerun()
            
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_email = None
            st.session_state.messages = []
            st.rerun()

    # Display history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_query = st.chat_input("Ask anything to Abhi's AI...")

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        save_chat_message(st.session_state.user_email, "user", user_query)
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
                    yield f"⚠️ Tunnel issue: {str(e)}"

            full_reply = st.write_stream(stream_response)

        st.session_state.messages.append({"role": "assistant", "content": full_reply})
        save_chat_message(st.session_state.user_email, "assistant", full_reply)
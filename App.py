import hashlib
import json
import sqlite3
from datetime import datetime
import requests
import streamlit as st

st.set_page_config(
    page_title="Smart AI, Made by Abhi", page_icon="🧠", layout="wide"
)

# --- Database Setup ---
conn = sqlite3.connect("ai_assistant.db", check_same_thread=False)
cursor = conn.cursor()

# Strict primary key prevents duplicate entries at DB level
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    created_at TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (user_email) REFERENCES users(email)
)
""")
conn.commit()

# --- Helper Functions ---
def hash_pass(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def get_user_chats(email: str):
    cursor.execute(
        "SELECT role, content FROM chat_history WHERE user_email = ? ORDER BY"
        " id ASC",
        (email,),
    )
    return [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]

def save_chat_message(email: str, role: str, content: str):
    cursor.execute(
        "INSERT INTO chat_history (user_email, role, content, timestamp) VALUES"
        " (?, ?, ?, ?)",
        (
            email,
            role,
            content,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()

def clear_user_history(email: str):
    cursor.execute("DELETE FROM chat_history WHERE user_email = ?", (email,))
    conn.commit()

# --- Active Cloudflare Tunnel URL ---
OLLAMA_SERVER_URL = "https://directive-asks-trance-subjects.trycloudflare.com"

# --- Session Initialization ---
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# --- View 1: Authentication (Login / Strict Signup) ---
if not st.session_state.user_email:
    st.title("🧠 Smart AI - Login / Register")
    st.caption("Sign in with your unique Gmail address to access your private chat memory.")

    auth_choice = st.radio(
        "Select Operation",
        ["Login to Account", "Create New Account"],
        horizontal=True,
    )

    with st.form("auth_form", clear_on_submit=False):
        raw_email = st.text_input("Gmail Address", placeholder="username@gmail.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Proceed", use_container_width=True)

        if submitted:
            email = raw_email.strip().lower()

            if not email.endswith("@gmail.com"):
                st.error("Validation Error: Only valid `@gmail.com` addresses are accepted.")
            elif len(password) < 4:
                st.error("Validation Error: Password must be at least 4 characters long.")
            else:
                if auth_choice == "Create New Account":
                    # Verification check before account creation
                    cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
                    existing_user = cursor.fetchone()

                    if existing_user:
                        st.error("⚠️ Account already exists with this Gmail! Only 1 account per Gmail is allowed. Please switch to 'Login to Account'.")
                    else:
                        try:
                            cursor.execute(
                                "INSERT INTO users (email, password, created_at) VALUES (?, ?, ?)",
                                (
                                    email,
                                    hash_pass(password),
                                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                ),
                            )
                            conn.commit()
                            st.success("✅ Account successfully created! Please switch to 'Login to Account' and sign in.")
                        except sqlite3.IntegrityError:
                            st.error("⚠️ This Gmail is already registered.")

                elif auth_choice == "Login to Account":
                    cursor.execute(
                        "SELECT email FROM users WHERE email = ? AND password = ?",
                        (email, hash_pass(password)),
                    )
                    user = cursor.fetchone()

                    if user:
                        st.session_state.user_email = email
                        st.session_state.messages = get_user_chats(email)
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please verify your Gmail and password.")

# --- View 2: Logged In AI Chat Interface ---
else:
    st.title("🧠 Smart AI, Made by Abhi")
    st.caption(f"Authenticated User: **{st.session_state.user_email}** | Hardware Engine Active")

    # Load persistent chat history for the logged-in user
    if "messages" not in st.session_state:
        st.session_state.messages = get_user_chats(st.session_state.user_email)

    with st.sidebar:
        st.header("👤 Profile Details")
        st.write(f"📧 **User ID:** `{st.session_state.user_email}`")
        st.success("✅ SQLite Persistent Storage Active")
        st.divider()

        if st.button("🗑️ Clear My Chat History", use_container_width=True):
            clear_user_history(st.session_state.user_email)
            st.session_state.messages = []
            st.rerun()

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_email = None
            st.session_state.messages = []
            st.rerun()

    # Display prior conversation turns
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_query = st.chat_input("Ask anything to Abhi's In-House AI...")

    if user_query:
        # Save user message to state and database
        st.session_state.messages.append({"role": "user", "content": user_query})
        save_chat_message(st.session_state.user_email, "user", user_query)
        with st.chat_message("user"):
            st.markdown(user_query)

        # Stream AI response token by token
        with st.chat_message("assistant"):
            payload = {
                "model": "llama3.2:1b",
                "messages": st.session_state.messages,
                "stream": True,
            }

            def stream_response():
                try:
                    with requests.post(
                        f"{OLLAMA_SERVER_URL}/api/chat",
                        json=payload,
                        stream=True,
                        timeout=180,
                    ) as r:
                        if r.status_code == 200:
                            for line in r.iter_lines():
                                if line:
                                    data = json.loads(line.decode("utf-8"))
                                    yield data.get("message", {}).get("content", "")
                        else:
                            yield f"Error: Received status code {r.status_code}"
                except Exception as e:
                    yield f"⚠️ Tunnel connection issue: {str(e)}"

            full_reply = st.write_stream(stream_response)

        # Save assistant message to state and database
        st.session_state.messages.append({"role": "assistant", "content": full_reply})
        save_chat_message(st.session_state.user_email, "assistant", full_reply)
import hashlib
import json
import sqlite3
from datetime import datetime
import requests
import streamlit as st
import streamlit.components.v1 as components
from pypdf import PdfReader

st.set_page_config(
    page_title="Smart AI, Made by Abhi", page_icon="🧠", layout="wide"
)

# --- Custom Gemini Floating Bar Styling ---
st.markdown("""
<style>
    /* Bottom container layout styling */
    .stChatInput {
        display: none !important;
    }
    .gemini-bar-container {
        background-color: #1e1f20;
        border-radius: 28px;
        padding: 6px 14px;
        display: flex;
        align-items: center;
        border: 1px solid #3c4043;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- Active Tunnel Link ---
OLLAMA_SERVER_URL = "https://dev-flash-rear-salon.trycloudflare.com"

# --- Database Setup ---
conn = sqlite3.connect("ai_assistant.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    created_at TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    user_email TEXT NOT NULL,
    session_title TEXT NOT NULL,
    created_at TEXT NOT NULL
)
""")

try:
    cursor.execute("SELECT session_id FROM chat_history LIMIT 1")
except sqlite3.OperationalError:
    cursor.execute("DROP TABLE IF EXISTS chat_history")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_email TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL
)
""")
conn.commit()

# --- Helpers ---
def hash_pass(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def get_user_sessions(email: str):
    cursor.execute(
        "SELECT session_id, session_title FROM sessions WHERE user_email = ? ORDER BY created_at DESC",
        (email,)
    )
    return cursor.fetchall()

def create_new_session(email: str, title: str = "New Chat"):
    session_id = f"{email}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    cursor.execute(
        "INSERT INTO sessions (session_id, user_email, session_title, created_at) VALUES (?, ?, ?, ?)",
        (session_id, email, title, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    return session_id

def get_session_messages(session_id: str):
    cursor.execute(
        "SELECT role, content FROM chat_history WHERE session_id = ? ORDER BY id ASC",
        (session_id,)
    )
    return [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]

def save_chat_message(session_id: str, email: str, role: str, content: str):
    cursor.execute(
        "INSERT INTO chat_history (session_id, user_email, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
        (session_id, email, role, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()

def delete_session(session_id: str):
    cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()

def extract_text_from_pdf(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages[:10]:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()

# --- Auth State ---
if "user_email" not in st.session_state:
    if "user" in st.query_params:
        saved_email = st.query_params["user"]
        cursor.execute("SELECT email FROM users WHERE email = ?", (saved_email,))
        if cursor.fetchone():
            st.session_state.user_email = saved_email
        else:
            st.session_state.user_email = None
    else:
        st.session_state.user_email = None

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# --- Auth Page ---
if not st.session_state.user_email:
    st.title("🧠 Smart AI - Login / Register")
    auth_choice = st.radio("Select Action", ["Login to Account", "Create New Account"], horizontal=True)

    with st.form("auth_form"):
        raw_email = st.text_input("Gmail Address", placeholder="name@gmail.com")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Proceed", use_container_width=True):
            email = raw_email.strip().lower()
            if not email.endswith("@gmail.com"):
                st.error("Only valid `@gmail.com` addresses are accepted.")
            elif len(password) < 4:
                st.error("Password must be at least 4 characters long.")
            else:
                if auth_choice == "Create New Account":
                    cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
                    if cursor.fetchone():
                        st.error("Account already exists.")
                    else:
                        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (email, hash_pass(password), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()
                        st.success("Account created! Switch to login.")
                else:
                    cursor.execute("SELECT email FROM users WHERE email = ? AND password = ?", (email, hash_pass(password)))
                    if cursor.fetchone():
                        st.session_state.user_email = email
                        st.query_params["user"] = email
                        sessions = get_user_sessions(email)
                        st.session_state.current_session_id = sessions[0][0] if sessions else create_new_session(email, "General Chat")
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")

# --- Chat Workspace ---
else:
    sessions = get_user_sessions(st.session_state.user_email)
    if not st.session_state.current_session_id:
        st.session_state.current_session_id = sessions[0][0] if sessions else create_new_session(st.session_state.user_email, "General Chat")
        sessions = get_user_sessions(st.session_state.user_email)

    with st.sidebar:
        st.header("💬 Conversations")
        with st.expander("➕ Start New Chat"):
            new_title = st.text_input("Topic Name", placeholder="e.g. Code, Math...")
            if st.button("Create Chat", use_container_width=True):
                title = new_title.strip() if new_title.strip() else "Untitled Chat"
                st.session_state.current_session_id = create_new_session(st.session_state.user_email, title)
                st.rerun()

        st.divider()
        for s_id, s_title in sessions:
            col1, col2 = st.columns([4, 1])
            is_active = (s_id == st.session_state.current_session_id)
            if col1.button(f"👉 {s_title}" if is_active else f"📄 {s_title}", key=f"btn_{s_id}", use_container_width=True):
                st.session_state.current_session_id = s_id
                st.rerun()
            if col2.button("❌", key=f"del_{s_id}"):
                delete_session(s_id)
                rem = get_user_sessions(st.session_state.user_email)
                st.session_state.current_session_id = rem[0][0] if rem else None
                st.rerun()

        st.divider()
        st.caption(f"👤 `{st.session_state.user_email}`")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_email = None
            st.session_state.current_session_id = None
            st.query_params.clear()
            st.rerun()

    current_title = next((title for s_id, title in sessions if s_id == st.session_state.current_session_id), "Chat")
    st.title(f"🧠 {current_title}")

    # Messages Display
    messages = get_session_messages(st.session_state.current_session_id)
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- Single-Use Attachment Expander (Triggered by +) ---
    with st.expander("➕ Attach File / Doc", expanded=False):
        uploaded_file = st.file_uploader(
            "Upload attachment",
            type=["pdf", "png", "jpg", "jpeg", "txt", "py", "md", "csv", "json"],
            key=f"uploader_{st.session_state.uploader_key}",
            label_visibility="collapsed"
        )
        if uploaded_file:
            st.caption(f"📎 Attached: **{uploaded_file.name}**")

    # --- Gemini Styled Unified Bar (Input + Mic) ---
    st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
    input_col, mic_col = st.columns([11, 1], gap="small")

    with input_col:
        with st.form(key=f"chat_form_{st.session_state.uploader_key}", clear_on_submit=True):
            user_input = st.text_input(
                "Ask Smart AI...",
                placeholder="Ask Smart AI...",
                label_visibility="collapsed",
                key="unified_prompt_box"
            )
            submit_button = st.form_submit_button("Send", use_container_width=True)

    with mic_col:
        components.html("""
        <button id="mic-btn" onclick="startMic()" style="background: none; border: none; font-size: 22px; cursor: pointer; color: #e8eaed; padding-top: 6px;" title="Voice Typing">
            🎙️
        </button>
        <script>
        function startMic() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                alert("Voice typing requires Chrome or Edge.");
                return;
            }
            const rec = new SpeechRecognition();
            rec.lang = 'hi-IN';
            rec.onstart = function() { document.getElementById("mic-btn").style.filter = "drop-shadow(0 0 5px #ff4b4b)"; };
            rec.onresult = function(e) {
                const text = e.results[0][0].transcript;
                const field = window.parent.document.querySelector('input[data-testid="stTextInputRootElement"] input');
                if (field) {
                    field.value = text;
                    field.dispatchEvent(new Event('input', { bubbles: true }));
                }
            };
            rec.onend = function() { document.getElementById("mic-btn").style.filter = "none"; };
            rec.start();
        }
        </script>
        """, height=45)

    # --- Handle Submission ---
    if submit_button and user_input.strip():
        doc_text = ""
        if uploaded_file is not None:
            file_ext = uploaded_file.name.split(".")[-1].lower()
            if file_ext == "pdf":
                doc_text = extract_text_from_pdf(uploaded_file)
            elif file_ext in ["png", "jpg", "jpeg"]:
                doc_text = f"[Image File Attached: {uploaded_file.name}]"
            else:
                doc_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")

        prompt_content = f"--- Attached ({uploaded_file.name}) ---\n{doc_text[:4000]}\n\n--- User Query ---\n{user_input.strip()}" if doc_text else user_input.strip()

        save_chat_message(st.session_state.current_session_id, st.session_state.user_email, "user", prompt_content)
        with st.chat_message("user"):
            st.markdown(prompt_content)

        system_instruction = {
            "role": "system",
            "content": "You are a professional AI assistant created by Abhi. Provide complete, accurate, structured, and helpful responses."
        }

        active_history = get_session_messages(st.session_state.current_session_id)
        ollama_messages = [system_instruction] + [{"role": m["role"], "content": str(m["content"])} for m in active_history]

        payload = {
            "model": "qwen2.5-coder:1.5b",
            "messages": ollama_messages,
            "stream": True
        }

        with st.chat_message("assistant"):
            def stream_response():
                try:
                    with requests.post(f"{OLLAMA_SERVER_URL}/api/chat", json=payload, stream=True, timeout=180) as r:
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

        save_chat_message(st.session_state.current_session_id, st.session_state.user_email, "assistant", full_reply)
        st.session_state.uploader_key += 1
        st.rerun()
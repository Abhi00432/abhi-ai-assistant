import hashlib
import json
import sqlite3
from datetime import datetime
import requests
import streamlit as st
from pypdf import PdfReader

st.set_page_config(
    page_title="Smart AI, Made by Abhi", page_icon="⚡", layout="wide"
)

# --- 3D Dark High-Contrast Clean CSS ---
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
    }

    span[data-testid="stIconMaterial"], .material-symbols-rounded, .material-icons, [class*="material-"] {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
        font-feature-settings: 'liga' !important;
        display: inline-block !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d !important;
    }

    div[data-testid="stChatMessage"] {
        background: #161b22 !important;
        border-radius: 16px !important;
        border: 1px solid #30363d !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
        color: #e6edf3 !important;
    }

    div[data-testid="stChatMessage"]:nth-child(even) {
        border-left: 4px solid #58a6ff !important;
    }
    div[data-testid="stChatMessage"]:nth-child(odd) {
        border-left: 4px solid #bc8cff !important;
    }

    .stButton > button {
        background: #21262d !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3) !important;
    }
    .stButton > button:hover {
        background: #30363d !important;
        color: #58a6ff !important;
        border-color: #58a6ff !important;
    }

    /* Fixed Bottom Dock */
    .main .block-container {
        padding-bottom: 130px !important;
    }

    div[data-testid="stBottomBlockContainer"] {
        background-color: #0d1117 !important;
        border-top: 1px solid #21262d !important;
        padding-top: 10px !important;
        padding-bottom: 18px !important;
    }

    /* Bottom Unified Bar Container */
    .chat-dock {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Circular Pure '+' Button */
    div[data-testid="stPopover"] > button {
        background: #21262d !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
        border-radius: 50% !important;
        width: 44px !important;
        height: 44px !important;
        padding: 0px !important;
        font-size: 22px !important;
        font-weight: bold !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 44px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
    }
    div[data-testid="stPopover"] > button:hover {
        border-color: #58a6ff !important;
        color: #ffffff !important;
        transform: scale(1.05) !important;
    }

    div[data-testid="stChatInput"] {
        border-radius: 24px !important;
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6) !important;
    }

    div[data-testid="stChatInput"] textarea {
        color: #e6edf3 !important;
        font-size: 15px !important;
    }

    .app-title {
        font-size: 2rem;
        font-weight: 700;
        color: #58a6ff;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Active Tunnel Link ---
OLLAMA_SERVER_URL = "https://dvd-consortium-satin-hint.trycloudflare.com"

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

def create_new_session(email: str, title: str = "General Chat"):
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

if "attached_doc_text" not in st.session_state:
    st.session_state.attached_doc_text = ""

if "attached_file_name" not in st.session_state:
    st.session_state.attached_file_name = ""

# --- Auth Screen ---
if not st.session_state.user_email:
    st.markdown('<div class="app-title">⚡ Smart AI Workspace</div>', unsafe_allow_html=True)
    st.caption("Sign in with your Gmail. 1 Account per Gmail ID.")

    auth_choice = st.radio("Select Action", ["Login to Account", "Create New Account"], horizontal=True)

    with st.form("auth_form"):
        raw_email = st.text_input("Gmail Address", placeholder="name@gmail.com")
        password = st.text_input("Password", type="password", placeholder="Enter password")
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
                        st.error("Account already exists with this Gmail.")
                    else:
                        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (email, hash_pass(password), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()
                        st.success("Account created! Switch to Login.")
                else:
                    cursor.execute("SELECT email FROM users WHERE email = ? AND password = ?", (email, hash_pass(password)))
                    if cursor.fetchone():
                        st.session_state.user_email = email
                        st.query_params["user"] = email
                        sessions = get_user_sessions(email)
                        st.session_state.current_session_id = sessions[0][0] if sessions else create_new_session(email, "General Chat")
                        st.rerun()
                    else:
                        st.error("Invalid Gmail or password.")

# --- Workspace Screen ---
else:
    sessions = get_user_sessions(st.session_state.user_email)
    if not st.session_state.current_session_id:
        st.session_state.current_session_id = sessions[0][0] if sessions else create_new_session(st.session_state.user_email, "General Chat")
        sessions = get_user_sessions(st.session_state.user_email)

    with st.sidebar:
        st.markdown("### 💬 Conversations")
        with st.expander("✨ + New Chat", expanded=False):
            with st.form("new_thread_form", clear_on_submit=True):
                new_title = st.text_input("Topic Name", placeholder="e.g. Project, Python...", label_visibility="collapsed")
                if st.form_submit_button("Create Chat", use_container_width=True) and new_title.strip():
                    st.session_state.current_session_id = create_new_session(st.session_state.user_email, new_title.strip())
                    st.rerun()

        st.divider()
        for s_id, s_title in sessions:
            col1, col2 = st.columns([4, 1])
            is_active = (s_id == st.session_state.current_session_id)
            if col1.button(f"👉 {s_title}" if is_active else f"📄 {s_title}", key=f"btn_{s_id}", use_container_width=True):
                st.session_state.current_session_id = s_id
                st.rerun()
            if col2.button("✕", key=f"del_{s_id}"):
                delete_session(s_id)
                rem = get_user_sessions(st.session_state.user_email)
                st.session_state.current_session_id = rem[0][0] if rem else None
                st.rerun()

        st.divider()
        st.caption(f"👤 Logged in: `{st.session_state.user_email}`")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_email = None
            st.session_state.current_session_id = None
            st.query_params.clear()
            st.rerun()

    current_title = next((title for s_id, title in sessions if s_id == st.session_state.current_session_id), "Chat")
    st.markdown(f'<div class="app-title">{current_title}</div>', unsafe_allow_html=True)

    # Render History
    messages = get_session_messages(st.session_state.current_session_id)
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Show active attachment badge
    if st.session_state.attached_file_name:
        st.info(f"📎 Attached for next prompt: **{st.session_state.attached_file_name}**")

    # --- Pure '+' Popover Button (Aligned with Bottom Bar) ---
    pop_col, _ = st.columns([1, 15])
    with pop_col:
        with st.popover("+", use_container_width=True):
            st.markdown("##### 📎 Attach File")
            up_file = st.file_uploader(
                "Choose file",
                type=["pdf", "png", "jpg", "jpeg", "txt", "py", "md", "csv", "json"],
                key=f"pop_up_{st.session_state.uploader_key}"
            )
            if up_file:
                file_ext = up_file.name.split(".")[-1].lower()
                if file_ext == "pdf":
                    st.session_state.attached_doc_text = extract_text_from_pdf(up_file)
                elif file_ext in ["png", "jpg", "jpeg"]:
                    st.session_state.attached_doc_text = f"[Image Attached: {up_file.name}]"
                else:
                    st.session_state.attached_doc_text = up_file.getvalue().decode("utf-8", errors="ignore")
                st.session_state.attached_file_name = up_file.name
                st.rerun()

    # Chat Input
    user_query = st.chat_input(f"Message in {current_title}...")

    if user_query and user_query.strip():
        if st.session_state.attached_doc_text:
            prompt_content = f"--- Attached Data ({st.session_state.attached_file_name}) ---\n{st.session_state.attached_doc_text[:4000]}\n\n--- Prompt ---\n{user_query.strip()}"
        else:
            prompt_content = user_query.strip()

        save_chat_message(st.session_state.current_session_id, st.session_state.user_email, "user", prompt_content)
        with st.chat_message("user"):
            st.markdown(prompt_content)

        system_instruction = {
            "role": "system",
            "content": "You are a professional AI assistant and software developer created by Abhi. Provide clean, structured, accurate, and helpful answers."
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
                    yield f"⚠️ Network stream disconnected: {str(e)}"

            full_reply = st.write_stream(stream_response)

        save_chat_message(st.session_state.current_session_id, st.session_state.user_email, "assistant", full_reply)
        
        # Reset State
        st.session_state.attached_doc_text = ""
        st.session_state.attached_file_name = ""
        st.session_state.uploader_key += 1
        st.rerun()
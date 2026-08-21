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

# --- Active Local Tunnel Link (अगर टनल बदला है तो नया URL यहाँ डालें) ---
OLLAMA_SERVER_URL = "https://directive-asks-trance-subjects.trycloudflare.com"

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

# --- Helper Functions ---
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

# --- Auto-Login via URL Query Params ---
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

# --- View 1: Auth Screen ---
if not st.session_state.user_email:
    st.title("🧠 Smart AI - Login / Register")
    st.caption("Sign in with your Gmail. 1 Account per Gmail ID.")

    auth_choice = st.radio("Select Action", ["Login to Account", "Create New Account"], horizontal=True)

    with st.form("auth_form"):
        raw_email = st.text_input("Gmail Address", placeholder="name@gmail.com")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submitted = st.form_submit_button("Proceed", use_container_width=True)

        if submitted:
            email = raw_email.strip().lower()

            if not email.endswith("@gmail.com"):
                st.error("Only valid `@gmail.com` addresses are accepted.")
            elif len(password) < 4:
                st.error("Password must be at least 4 characters long.")
            else:
                if auth_choice == "Create New Account":
                    cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
                    if cursor.fetchone():
                        st.error("⚠️ Account already exists with this Gmail.")
                    else:
                        cursor.execute(
                            "INSERT INTO users VALUES (?, ?, ?)",
                            (email, hash_pass(password), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        )
                        conn.commit()
                        st.success("✅ Account created! Switch to Login.")

                elif auth_choice == "Login to Account":
                    cursor.execute(
                        "SELECT email FROM users WHERE email = ? AND password = ?",
                        (email, hash_pass(password))
                    )
                    if cursor.fetchone():
                        st.session_state.user_email = email
                        st.query_params["user"] = email
                        sessions = get_user_sessions(email)
                        if sessions:
                            st.session_state.current_session_id = sessions[0][0]
                        else:
                            st.session_state.current_session_id = create_new_session(email, "General Chat")
                        st.rerun()
                    else:
                        st.error("Invalid Gmail or password.")

# --- View 2: Multi-Chat Workspace ---
else:
    sessions = get_user_sessions(st.session_state.user_email)
    
    if not st.session_state.current_session_id:
        if sessions:
            st.session_state.current_session_id = sessions[0][0]
        else:
            st.session_state.current_session_id = create_new_session(st.session_state.user_email, "New Topic")
            sessions = get_user_sessions(st.session_state.user_email)

    with st.sidebar:
        st.header("💬 Conversations")
        
        with st.expander("➕ Start New Chat", expanded=False):
            new_title = st.text_input("Topic Name", placeholder="e.g. Python, Math...")
            if st.button("Create Chat", use_container_width=True):
                title = new_title.strip() if new_title.strip() else "Untitled Chat"
                new_id = create_new_session(st.session_state.user_email, title)
                st.session_state.current_session_id = new_id
                st.rerun()

        st.divider()

        for s_id, s_title in sessions:
            col1, col2 = st.columns([4, 1])
            is_active = (s_id == st.session_state.current_session_id)
            btn_label = f"👉 {s_title}" if is_active else f"📄 {s_title}"
            
            if col1.button(btn_label, key=f"btn_{s_id}", use_container_width=True):
                st.session_state.current_session_id = s_id
                st.rerun()
                
            if col2.button("❌", key=f"del_{s_id}"):
                delete_session(s_id)
                remaining = get_user_sessions(st.session_state.user_email)
                st.session_state.current_session_id = remaining[0][0] if remaining else None
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

    # Render History
    messages = get_session_messages(st.session_state.current_session_id)
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- Native Browser Voice Typing & Attachment Widget ---
    components.html("""
    <div style="font-family: sans-serif; display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
        <button id="mic-btn" onclick="startVoice()" style="background-color: #ff4b4b; color: white; border: none; padding: 7px 14px; border-radius: 8px; font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 5px;">
            🎙️ Voice Typing (Click to Speak)
        </button>
        <span id="voice-status" style="color: gray; font-size: 13px;"></span>
    </div>

    <script>
    function startVoice() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const status = document.getElementById("voice-status");
        const btn = document.getElementById("mic-btn");

        if (!SpeechRecognition) {
            alert("Voice typing is not supported in this browser. Please use Chrome or Edge.");
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = 'hi-IN'; // Supports both Hindi and English
        recognition.interimResults = false;

        recognition.onstart = function() {
            btn.style.backgroundColor = "#28a745";
            btn.innerText = "🛑 Listening...";
            status.innerText = "Speak now...";
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            // Write directly to Streamlit Chat Input in parent window
            const inputField = window.parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
            if (inputField) {
                inputField.value = transcript;
                inputField.dispatchEvent(new Event('input', { bubbles: true }));
            }
            status.innerText = "Transcribed: " + transcript;
        };

        recognition.onerror = function(event) {
            status.innerText = "Error: " + event.error;
            btn.style.backgroundColor = "#ff4b4b";
            btn.innerText = "🎙️ Voice Typing (Click to Speak)";
        };

        recognition.onend = function() {
            btn.style.backgroundColor = "#ff4b4b";
            btn.innerText = "🎙️ Voice Typing (Click to Speak)";
        };

        recognition.start();
    }
    </script>
    """, height=50)

    # ➕ Single-Use Attachment Box
    with st.expander("➕ Attach Image / PDF / Code (Single Use)", expanded=False):
        uploaded_file = st.file_uploader(
            "Select file",
            type=["pdf", "png", "jpg", "jpeg", "txt", "py", "md", "csv", "json"],
            key=f"uploader_{st.session_state.uploader_key}",
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            st.caption(f"📎 Attached for next message: **{uploaded_file.name}**")

    user_query = st.chat_input(f"Message in {current_title}...")

    if user_query and user_query.strip():
        doc_text = ""
        if uploaded_file is not None:
            file_ext = uploaded_file.name.split(".")[-1].lower()
            if file_ext == "pdf":
                doc_text = extract_text_from_pdf(uploaded_file)
            elif file_ext in ["png", "jpg", "jpeg"]:
                doc_text = f"[Image File Attached: {uploaded_file.name}]"
            else:
                doc_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")

        if doc_text:
            prompt_content = f"--- Attached ({uploaded_file.name}) ---\n{doc_text[:4000]}\n\n--- User Query ---\n{user_query.strip()}"
        else:
            prompt_content = user_query.strip()

        save_chat_message(st.session_state.current_session_id, st.session_state.user_email, "user", prompt_content)
        with st.chat_message("user"):
            st.markdown(prompt_content)

        system_instruction = {
            "role": "system",
            "content": (
                "You are an expert AI software developer and document analyzer created by Abhi. "
                "Provide complete, clean, bug-free, and well-structured responses."
            )
        }

        active_history = get_session_messages(st.session_state.current_session_id)
        ollama_messages = [system_instruction] + [
            {"role": m["role"], "content": str(m["content"])} for m in active_history
        ]

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
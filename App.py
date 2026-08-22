import hashlib
import json
import sqlite3
from datetime import datetime
import requests
import streamlit as st
import streamlit.components.v1 as components
from pypdf import PdfReader

st.set_page_config(
    page_title="Smart AI, Made by Abhi", page_icon="⚡", layout="wide"
)

# --- Fixed 3D Futuristic Glassmorphism CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    /* Apply custom font specifically to text elements, protecting icon ligatures */
    html, body, p, div, span, h1, h2, h3, h4, h5, h6, input, textarea, button {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Keep Streamlit Material Icons intact so they don't break into text */
    span[data-testid="stIconMaterial"], 
    .material-symbols-rounded, 
    .material-icons,
    [class*="material-"] {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
        font-feature-settings: 'liga' !important;
        display: inline-block !important;
    }

    /* 3D Dark Animated Gradient Background */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(90, 34, 139, 0.25), transparent 40%),
                    radial-gradient(circle at 90% 80%, rgba(0, 210, 255, 0.2), transparent 40%),
                    radial-gradient(circle at 50% 50%, #0d0f18, #05060a 100%) !important;
        background-attachment: fixed !important;
        color: #f1f5f9 !important;
    }

    /* 3D Glassmorphic Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(18, 22, 36, 0.75) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 10px 0 30px rgba(0, 0, 0, 0.5) !important;
    }

    /* 3D Elevated Cards & Message Bubbles */
    div[data-testid="stChatMessage"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.01)) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-left: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.7),
                    inset 0 1px 1px rgba(255, 255, 255, 0.1) !important;
        padding: 18px 24px !important;
        margin-bottom: 16px !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    }
    div[data-testid="stChatMessage"]:hover {
        transform: translateY(-2px) scale(1.005) !important;
        box-shadow: 0 14px 35px -8px rgba(0, 210, 255, 0.15) !important;
    }

    /* Message Accent Borders */
    div[data-testid="stChatMessage"]:nth-child(even) {
        border-left: 3px solid #00d2ff !important;
    }
    div[data-testid="stChatMessage"]:nth-child(odd) {
        border-left: 3px solid #9d4edd !important;
    }

    /* 3D Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1e2438, #131726) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.4),
                    inset 0 1px 1px rgba(255, 255, 255, 0.2),
                    inset 0 -2px 0 rgba(0, 0, 0, 0.5) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        color: #ffffff !important;
        border-color: #00d2ff !important;
        box-shadow: 0 10px 20px rgba(0, 210, 255, 0.3),
                    inset 0 1px 1px rgba(255, 255, 255, 0.3) !important;
    }

    /* Expander Container */
    div[data-testid="stExpander"] {
        background: rgba(18, 22, 36, 0.6) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3) !important;
    }

    /* Sticky Bottom Input Capsule */
    .main .block-container {
        padding-bottom: 140px !important;
    }

    div[data-testid="stBottomBlockContainer"] {
        background-color: transparent !important;
        padding-bottom: 24px !important;
    }

    div[data-testid="stChatInput"] {
        border-radius: 30px !important;
        background: rgba(22, 27, 46, 0.85) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.8),
                    0 0 20px rgba(0, 210, 255, 0.15),
                    inset 0 1px 2px rgba(255, 255, 255, 0.2) !important;
    }

    div[data-testid="stChatInput"] textarea {
        color: #f8fafc !important;
        font-size: 15px !important;
    }

    .glowing-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff 30%, #00d2ff 70%, #9d4edd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 10px 25px rgba(0, 210, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- Active Tunnel Link ---
OLLAMA_SERVER_URL = "https://received-candidate-premises-andrea.trycloudflare.com"

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

def create_new_session(email: str, title: str = "New Dimension"):
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

# --- Auth Screen ---
if not st.session_state.user_email:
    st.markdown('<div class="glowing-title">⚡ Smart AI Nexus</div>', unsafe_allow_html=True)
    st.caption("Next-Gen 3D AI Workspace | Single-ID Gmail Authentication")
    st.write("")

    auth_choice = st.radio("Access Portal", ["Sign In", "Register Account"], horizontal=True)

    with st.form("auth_form"):
        raw_email = st.text_input("Gmail Address", placeholder="name@gmail.com")
        password = st.text_input("Passkey", type="password", placeholder="••••••••")
        if st.form_submit_button("Enter Dimension", use_container_width=True):
            email = raw_email.strip().lower()
            if not email.endswith("@gmail.com"):
                st.error("Validation failed: Only valid `@gmail.com` addresses accepted.")
            elif len(password) < 4:
                st.error("Security alert: Passkey must be at least 4 characters.")
            else:
                if auth_choice == "Register Account":
                    cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
                    if cursor.fetchone():
                        st.error("Account already active with this Gmail.")
                    else:
                        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (email, hash_pass(password), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()
                        st.success("Registration complete! Switch to Sign In.")
                else:
                    cursor.execute("SELECT email FROM users WHERE email = ? AND password = ?", (email, hash_pass(password)))
                    if cursor.fetchone():
                        st.session_state.user_email = email
                        st.query_params["user"] = email
                        sessions = get_user_sessions(email)
                        st.session_state.current_session_id = sessions[0][0] if sessions else create_new_session(email, "Workspace")
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")

# --- 3D Main Workspace ---
else:
    sessions = get_user_sessions(st.session_state.user_email)
    if not st.session_state.current_session_id:
        st.session_state.current_session_id = sessions[0][0] if sessions else create_new_session(st.session_state.user_email, "Workspace")
        sessions = get_user_sessions(st.session_state.user_email)

    with st.sidebar:
        st.markdown("### 🔮 Holographic Hub")
        
        # New Thread Box with auto-enter and auto-clear
        with st.expander("✨ + New Thread", expanded=False):
            with st.form("new_thread_form", clear_on_submit=True):
                new_title = st.text_input("Thread Title", placeholder="e.g. Code, Project...", label_visibility="collapsed")
                create_submitted = st.form_submit_button("Spawn Thread", use_container_width=True)
                
                if create_submitted and new_title.strip():
                    new_id = create_new_session(st.session_state.user_email, new_title.strip())
                    st.session_state.current_session_id = new_id
                    st.rerun()

        st.divider()
        st.markdown("**Active Threads**")
        for s_id, s_title in sessions:
            col1, col2 = st.columns([4, 1])
            is_active = (s_id == st.session_state.current_session_id)
            if col1.button(f"💎 {s_title}" if is_active else f"🪐 {s_title}", key=f"btn_{s_id}", use_container_width=True):
                st.session_state.current_session_id = s_id
                st.rerun()
            if col2.button("✕", key=f"del_{s_id}"):
                delete_session(s_id)
                rem = get_user_sessions(st.session_state.user_email)
                st.session_state.current_session_id = rem[0][0] if rem else None
                st.rerun()

        st.divider()
        st.caption(f"⚡ Logged in: `{st.session_state.user_email}`")
        if st.button("🚪 Disconnect", use_container_width=True):
            st.session_state.user_email = None
            st.session_state.current_session_id = None
            st.query_params.clear()
            st.rerun()

    current_title = next((title for s_id, title in sessions if s_id == st.session_state.current_session_id), "Workspace")
    st.markdown(f'<div class="glowing-title">{current_title}</div>', unsafe_allow_html=True)
    st.caption("3D Glassmorphic Interface | Hardware Engine Sync")

    # Render History
    messages = get_session_messages(st.session_state.current_session_id)
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Attachment Capsule
    with st.expander("📎 Attach Data Artifacts (PDF, Code, Doc)", expanded=False):
        uploaded_file = st.file_uploader(
            "Upload file",
            type=["pdf", "png", "jpg", "jpeg", "txt", "py", "md", "csv", "json"],
            key=f"uploader_{st.session_state.uploader_key}",
            label_visibility="collapsed"
        )
        if uploaded_file:
            st.caption(f"🔮 Synced Artifact: **{uploaded_file.name}**")

    # Native Voice Engine Hook for Sticky 3D Bar
    components.html("""
    <script>
    window.addEventListener('DOMContentLoaded', () => {
        const bottomBar = window.parent.document.querySelector('div[data-testid="stChatInput"]');
        if (bottomBar && !window.parent.document.getElementById('custom-3d-mic')) {
            const micBtn = document.createElement('button');
            micBtn.id = 'custom-3d-mic';
            micBtn.innerHTML = '🎙️';
            micBtn.title = 'Voice Typing';
            micBtn.style.cssText = 'background:none; border:none; font-size:20px; cursor:pointer; margin-right:10px; display:flex; align-items:center; transition: all 0.3s; filter: drop-shadow(0 0 4px rgba(0,210,255,0.4));';

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRecognition) {
                const rec = new SpeechRecognition();
                rec.lang = 'hi-IN';
                rec.onstart = () => { micBtn.style.filter = 'drop-shadow(0 0 12px #ff4b4b)'; micBtn.style.transform = 'scale(1.2)'; };
                rec.onresult = (e) => {
                    const text = e.results[0][0].transcript;
                    const input = window.parent.document.querySelector('div[data-testid="stChatInput"] textarea');
                    if (input) {
                        input.value = text;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                };
                rec.onend = () => { micBtn.style.filter = 'drop-shadow(0 0 4px rgba(0,210,255,0.4))'; micBtn.style.transform = 'scale(1)'; };
                micBtn.onclick = () => rec.start();
            }
            bottomBar.appendChild(micBtn);
        }
    });
    </script>
    """, height=0)

    # 3D Floating Sticky Chat Input
    user_query = st.chat_input(f"Transmit prompt in {current_title}...")

    if user_query and user_query.strip():
        doc_text = ""
        if uploaded_file is not None:
            file_ext = uploaded_file.name.split(".")[-1].lower()
            if file_ext == "pdf":
                doc_text = extract_text_from_pdf(uploaded_file)
            elif file_ext in ["png", "jpg", "jpeg"]:
                doc_text = f"[Image Attached: {uploaded_file.name}]"
            else:
                doc_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")

        prompt_content = f"--- Attached Data ({uploaded_file.name}) ---\n{doc_text[:4000]}\n\n--- Prompt ---\n{user_query.strip()}" if doc_text else user_query.strip()

        save_chat_message(st.session_state.current_session_id, st.session_state.user_email, "user", prompt_content)
        with st.chat_message("user"):
            st.markdown(prompt_content)

        system_instruction = {
            "role": "system",
            "content": "You are a top-tier software engineer, document analyst, and AI built by Abhi. Deliver detailed, fully functioning, clean code and structured responses."
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
        st.session_state.uploader_key += 1
        st.rerun()
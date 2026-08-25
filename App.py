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

# --- 3D Futuristic Animations & Glassmorphism CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');

    html, body, p, div, span, h1, h2, h3, h4, h5, h6, input, textarea, button {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    span[data-testid="stIconMaterial"], .material-symbols-rounded, .material-icons, [class*="material-"] {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
        font-feature-settings: 'liga' !important;
        display: inline-block !important;
    }

    /* Animated Cyber Fluid Background */
    .stApp {
        background: radial-gradient(circle at 15% 20%, rgba(112, 0, 255, 0.25), transparent 45%),
                    radial-gradient(circle at 85% 80%, rgba(0, 229, 255, 0.2), transparent 45%),
                    radial-gradient(circle at 50% 50%, #060913, #020408 100%) !important;
        background-attachment: fixed !important;
        color: #f1f5f9 !important;
        overflow-x: hidden;
    }

    /* Keyframes for Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(18px) scale(0.98);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    @keyframes pulseGlow {
        0%, 100% {
            text-shadow: 0 0 20px rgba(0, 229, 255, 0.4), 0 0 40px rgba(112, 0, 255, 0.2);
        }
        50% {
            text-shadow: 0 0 30px rgba(0, 229, 255, 0.8), 0 0 60px rgba(112, 0, 255, 0.5);
        }
    }

    @keyframes floatOrb {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(5deg); }
    }

    /* Animated 3D Message Bubbles */
    div[data-testid="stChatMessage"] {
        animation: fadeInUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.01)) !important;
        backdrop-filter: blur(16px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 12px 35px -10px rgba(0, 0, 0, 0.7) !important;
        padding: 18px 22px !important;
        margin-bottom: 16px !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease !important;
    }

    div[data-testid="stChatMessage"]:hover {
        transform: translateY(-3px) scale(1.008) !important;
        box-shadow: 0 16px 40px -8px rgba(0, 229, 255, 0.25) !important;
        border-color: rgba(0, 229, 255, 0.35) !important;
    }

    div[data-testid="stChatMessage"]:nth-child(even) {
        border-left: 4px solid #00e5ff !important;
    }
    div[data-testid="stChatMessage"]:nth-child(odd) {
        border-left: 4px solid #a855f7 !important;
    }

    /* 3D Glassmorphic Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(10, 15, 29, 0.8) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 10px 0 35px rgba(0, 0, 0, 0.6) !important;
    }

    /* 3D Animated Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #182035, #0f1523) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.2) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        color: #ffffff !important;
        border-color: #00e5ff !important;
        box-shadow: 0 10px 25px rgba(0, 229, 255, 0.35), inset 0 1px 2px rgba(255, 255, 255, 0.4) !important;
    }

    .stButton > button:active {
        transform: translateY(1px) !important;
    }

    /* Circular Pure '+' Button */
    div[data-testid="stPopover"] > button {
        background: linear-gradient(135deg, #1a2238, #0e1424) !important;
        color: #00e5ff !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        border-radius: 50% !important;
        width: 44px !important;
        height: 44px !important;
        padding: 0px !important;
        font-size: 24px !important;
        font-weight: bold !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 44px !important;
        box-shadow: 0 6px 18px rgba(0, 229, 255, 0.25), inset 0 1px 1px rgba(255, 255, 255, 0.3) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    div[data-testid="stPopover"] > button:hover {
        transform: rotate(90deg) scale(1.1) !important;
        border-color: #00e5ff !important;
        color: #ffffff !important;
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.6) !important;
    }

    /* Fixed Floating Animated Bottom Bar */
    .main .block-container {
        padding-bottom: 140px !important;
    }

    div[data-testid="stBottomBlockContainer"] {
        background: transparent !important;
        padding-bottom: 20px !important;
    }

    div[data-testid="stChatInput"] {
        border-radius: 30px !important;
        background: rgba(16, 23, 42, 0.85) !important;
        backdrop-filter: blur(24px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.25) !important;
        box-shadow: 0 20px 45px -10px rgba(0, 0, 0, 0.8),
                    0 0 25px rgba(0, 229, 255, 0.15),
                    inset 0 1px 2px rgba(255, 255, 255, 0.2) !important;
        transition: box-shadow 0.3s ease, border-color 0.3s ease !important;
    }

    div[data-testid="stChatInput"]:focus-within {
        border-color: #00e5ff !important;
        box-shadow: 0 20px 45px -10px rgba(0, 0, 0, 0.9),
                    0 0 35px rgba(0, 229, 255, 0.35),
                    inset 0 1px 2px rgba(255, 255, 255, 0.3) !important;
    }

    div[data-testid="stChatInput"] textarea {
        color: #f8fafc !important;
        font-size: 15px !important;
    }

    /* 3D Animated Glowing Title */
    .glowing-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 20%, #00e5ff 60%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulseGlow 4s infinite ease-in-out;
        letter-spacing: -0.5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Active Tunnel Link ---
OLLAMA_SERVER_URL = "https://skills-significant-smoking-stopping.trycloudflare.com"

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

if "attached_doc_text" not in st.session_state:
    st.session_state.attached_doc_text = ""

if "attached_file_name" not in st.session_state:
    st.session_state.attached_file_name = ""

# --- Auth Screen ---
if not st.session_state.user_email:
    st.markdown('<div class="glowing-title">⚡ Smart AI Nexus</div>', unsafe_allow_html=True)
    st.caption("Next-Gen 3D Animated AI Portal | Single-ID Access")

    auth_choice = st.radio("Select Portal", ["Sign In", "Register Account"], horizontal=True)

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
                        st.error("Account already registered.")
                    else:
                        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (email, hash_pass(password), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()
                        st.success("Account created! Switch to Sign In.")
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

# --- 3D Animated Main Workspace ---
else:
    sessions = get_user_sessions(st.session_state.user_email)
    if not st.session_state.current_session_id:
        st.session_state.current_session_id = sessions[0][0] if sessions else create_new_session(st.session_state.user_email, "Workspace")
        sessions = get_user_sessions(st.session_state.user_email)

    with st.sidebar:
        st.markdown("### 🔮 Holographic Hub")
        with st.expander("✨ + New Thread", expanded=False):
            with st.form("new_thread_form", clear_on_submit=True):
                new_title = st.text_input("Thread Title", placeholder="e.g. Code, Project...", label_visibility="collapsed")
                if st.form_submit_button("Spawn Thread", use_container_width=True) and new_title.strip():
                    st.session_state.current_session_id = create_new_session(st.session_state.user_email, new_title.strip())
                    st.rerun()

        st.divider()
        st.markdown("**Active Dimensions**")
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

    # Render Animated History
    messages = get_session_messages(st.session_state.current_session_id)
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Show active attachment badge
    if st.session_state.attached_file_name:
        st.markdown(f'<div style="color: #00e5ff; font-weight: 600; margin-bottom: 8px; animation: fadeInUp 0.3s ease;">📎 Attached Data: <b>{st.session_state.attached_file_name}</b></div>', unsafe_allow_html=True)

    # Pure Rotating '+' Popover Button Aligned with Chat Input
    pop_col, _ = st.columns([1, 15])
    with pop_col:
        with st.popover("+", use_container_width=True):
            st.markdown("##### 📎 Attach Artifact")
            up_file = st.file_uploader(
                "Select File",
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

    # Sticky Floating Chat Input
    user_query = st.chat_input(f"Transmit prompt in {current_title}...")

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
            "content": (
                "You are an ultra-friendly, intelligent, and witty conversational AI assistant created by Abhi. "
                "You can answer anything: general talk, humor, gaming, studies, coding, life advice, and shayari. "
                "Always reply naturally in the user's language (Hindi, Hinglish, or English) with warmth, clarity, and smart insights."
            )
        }

        active_history = get_session_messages(st.session_state.current_session_id)
        ollama_messages = [system_instruction] + [{"role": m["role"], "content": str(m["content"])} for m in active_history]

        # सभी इंजीनियरिंग शाखाओं के लिए सिस्टम निर्देश
        system_instruction = {
            "role": "system",
            "content": "You are an expert AI for advanced STEM fields: Computer Science, Data Science, Mechanical Engineering, Mathematics, and Bio-Engineering. Provide rigorous, step-by-step analytical reasoning and verify all calculations before final output."
        }

        # सिर्फ हालिया बातचीत और सिस्टम निर्देश भेजना
        context_messages = [system_instruction] + ollama_messages[-3:]

        # केवल वर्तमान सवाल और पिछला उत्तर भेजें (CPU लोड शून्य करने के लिए)
        # केवल वर्तमान सवाल और पिछला उत्तर भेजें ताकि इवैल्यूएशन तुरंत (Instant) हो
        payload = {
            "model": "deepseek-r1:7b",      # या qwen2.5-coder:7b
            "messages": ollama_messages[-2:],# सिर्फ आखिरी 2 संदेश (5 मिनट का डिले खत्म करने की चाबी)
            "keep_alive": -1,                # हमेशा RAM में एक्टिव
            "options": {
                "num_thread": 6,             # 10th Gen के 6 थ्रेड्स
                "num_ctx": 1024,             # 1024 कॉन्टेक्स्ट से प्रोसेसिंग 4 गुना तेज हो जाती है
                "num_predict": 800,
                "temperature": 0.5
            },
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
                    yield f"⚠️ Stream error: {str(e)}"

            full_reply = st.write_stream(stream_response)

        save_chat_message(st.session_state.current_session_id, st.session_state.user_email, "assistant", full_reply)
        
        # Reset State
        st.session_state.attached_doc_text = ""
        st.session_state.attached_file_name = ""
        st.session_state.uploader_key += 1
        st.rerun()
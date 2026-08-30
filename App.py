import streamlit as st
import sqlite3
import hashlib
import requests
import json
import base64
import urllib.parse
from io import BytesIO
from PIL import Image

# ----------------------------------------------------
# 1. Page Configuration
# ----------------------------------------------------
st.set_page_config(
    page_title="HYPERCORE // AI MATRIX",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 2. Ultra Hyper-Animated Cyberpunk CSS Engine
# ----------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    :root {
        --neon-cyan: #00f0ff;
        --neon-blue: #3b82f6;
        --neon-purple: #8b5cf6;
        --neon-pink: #ec4899;
        --dark-glass: rgba(10, 15, 32, 0.75);
    }

    * {
        font-family: 'Space Grotesk', sans-serif !important;
        box-sizing: border-box;
    }

    p, span, div, h1, h2, h3, h4, h5, h6, [data-testid="stMarkdownContainer"] {
        word-break: break-word !important;
        overflow-wrap: anywhere !important;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        background: rgba(3, 6, 18, 0.95) !important;
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
        border-radius: 12px !important;
        box-shadow: inset 0 0 15px rgba(0, 240, 255, 0.1);
    }

    /* 1. LIVING 3D NEBULA BACKGROUND */
    .stApp {
        background: radial-gradient(circle at 20% 20%, rgba(0, 240, 255, 0.15) 0%, transparent 40%),
                    radial-gradient(circle at 80% 80%, rgba(236, 72, 153, 0.15) 0%, transparent 45%),
                    radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.12) 0%, transparent 50%),
                    linear-gradient(180deg, #02040a 0%, #080d1e 50%, #010206 100%);
        background-size: 250% 250%;
        animation: nebulaFloat 12s ease-in-out infinite alternate;
        background-attachment: fixed;
        color: #f8fafc;
    }

    @keyframes nebulaFloat {
        0% { background-position: 0% 0%; }
        100% { background-position: 100% 100%; }
    }

    /* 2. INFINITE LASER SCANNING GRID */
    .stApp::before {
        content: " ";
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px);
        background-size: 45px 45px;
        z-index: 0;
        pointer-events: none;
        animation: gridPan 20s linear infinite;
    }

    @keyframes gridPan {
        0% { transform: translateY(0); }
        100% { transform: translateY(45px); }
    }

    /* 3. RUNNING TOP RGB LASER */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--neon-cyan), var(--neon-pink), var(--neon-purple), transparent);
        background-size: 300% 100%;
        animation: rgbBeam 2.5s linear infinite;
        box-shadow: 0 0 25px var(--neon-cyan);
        z-index: 99999;
    }

    @keyframes rgbBeam {
        0% { background-position: 100% 0%; }
        100% { background-position: -100% 0%; }
    }

    /* 4. HOLOGRAPHIC DYNAMIC GLOW HEADER */
    .holo-header {
        position: relative;
        background: var(--dark-glass);
        border: 1px solid rgba(0, 240, 255, 0.35);
        border-radius: 20px;
        padding: 16px 26px;
        backdrop-filter: blur(25px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.7), 0 0 20px rgba(0, 240, 255, 0.15);
        margin-bottom: 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        animation: headerEntry 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes headerEntry {
        from { opacity: 0; transform: translateY(-20px) scale(0.96); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    /* 5. REACTOR CORE LIVE PULSE */
    .reactor-core {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: var(--neon-cyan);
        border-radius: 50%;
        box-shadow: 0 0 20px var(--neon-cyan);
        animation: coreOverload 1.2s infinite ease-in-out;
        margin-right: 12px;
    }

    @keyframes coreOverload {
        0%, 100% { transform: scale(0.85); box-shadow: 0 0 10px var(--neon-cyan); }
        50% { transform: scale(1.4); box-shadow: 0 0 25px var(--neon-cyan), 0 0 40px var(--neon-pink); }
    }

    /* 6. HYPER-ANIMATED 3D CHAT BUBBLES WITH RGB WAVE BORDER */
    [data-testid="stChatMessage"] {
        position: relative;
        background: rgba(12, 18, 40, 0.65) !important;
        border: 1px solid rgba(0, 240, 255, 0.18) !important;
        border-radius: 22px !important;
        backdrop-filter: blur(20px);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.5);
        margin-bottom: 16px;
        padding: 18px 22px !important;
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
        animation: chatBubbleSpawn 0.45s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes chatBubbleSpawn {
        from { opacity: 0; transform: translateY(18px) scale(0.95); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    [data-testid="stChatMessage"]:hover {
        border-color: var(--neon-cyan) !important;
        box-shadow: 0 15px 45px rgba(0, 240, 255, 0.25), 0 0 25px rgba(236, 72, 153, 0.15) !important;
        transform: translateY(-3px) scale(1.005);
    }

    /* 7. INTEGRATED CHAT BAR WITH GLOWING '+' ATTACHMENT ICON */
    [data-testid="stChatInput"] {
        background: rgba(10, 16, 35, 0.9) !important;
        border: 2px solid rgba(0, 240, 255, 0.4) !important;
        border-radius: 26px !important;
        padding: 8px 16px !important;
        backdrop-filter: blur(30px) !important;
        box-shadow: 0 15px 45px rgba(0, 0, 0, 0.7), 0 0 25px rgba(0, 240, 255, 0.25) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        animation: inputBreath 4s infinite alternate ease-in-out;
    }

    @keyframes inputBreath {
        0% { border-color: rgba(0, 240, 255, 0.4); box-shadow: 0 15px 45px rgba(0,0,0,0.7), 0 0 20px rgba(0, 240, 255, 0.2); }
        100% { border-color: rgba(236, 72, 153, 0.5); box-shadow: 0 15px 45px rgba(0,0,0,0.7), 0 0 30px rgba(236, 72, 153, 0.25); }
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: var(--neon-cyan) !important;
        box-shadow: 0 18px 55px rgba(0, 240, 255, 0.5), 0 0 35px rgba(139, 92, 246, 0.3) !important;
        transform: translateY(-3px);
    }

    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        font-size: 0.98rem !important;
    }

    /* '+' File Upload Attachment Button */
    [data-testid="stChatInput"] button:first-child {
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%) !important;
        border: 1px solid var(--neon-cyan) !important;
        color: var(--neon-cyan) !important;
        border-radius: 50% !important;
        margin-right: 8px !important;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    [data-testid="stChatInput"] button:first-child:hover {
        background: var(--neon-cyan) !important;
        color: #000000 !important;
        transform: scale(1.2) rotate(90deg) !important;
        box-shadow: 0 0 25px var(--neon-cyan) !important;
    }

    /* Send Arrow Button */
    [data-testid="stChatInput"] button:last-child {
        background: linear-gradient(135deg, var(--neon-cyan) 0%, var(--neon-blue) 50%, var(--neon-pink) 100%) !important;
        color: #000000 !important;
        border-radius: 14px !important;
        box-shadow: 0 0 18px rgba(0, 240, 255, 0.6) !important;
        transition: all 0.25s ease !important;
    }

    [data-testid="stChatInput"] button:last-child:hover {
        transform: scale(1.15) rotate(-8deg) !important;
        box-shadow: 0 0 30px rgba(0, 240, 255, 0.9) !important;
    }

    /* 8. CYBER SHOCKWAVE ACTION BUTTONS */
    .stButton>button {
        background: linear-gradient(135deg, var(--neon-cyan) 0%, var(--neon-blue) 50%, var(--neon-pink) 100%) !important;
        color: #01040a !important;
        font-weight: 800 !important;
        letter-spacing: 0.8px !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 10px 22px !important;
        box-shadow: 0 6px 25px rgba(0, 240, 255, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px) scale(1.03);
        box-shadow: 0 10px 40px rgba(0, 240, 255, 0.7), 0 0 20px rgba(236, 72, 153, 0.5) !important;
        color: #000 !important;
    }

    /* 9. SIDEBAR & AUTH GLASS PANELS */
    [data-testid="stSidebar"] {
        background: rgba(5, 9, 22, 0.92) !important;
        border-right: 1px solid rgba(0, 240, 255, 0.25);
        backdrop-filter: blur(30px);
    }

    [data-testid="stSidebarCollapseButton"] {
        background: rgba(10, 16, 35, 0.95) !important;
        border: 1px solid var(--neon-cyan) !important;
        border-radius: 12px !important;
        color: var(--neon-cyan) !important;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.4) !important;
        z-index: 1000000 !important;
    }

    .cyber-auth-modal {
        max-width: 440px;
        margin: 50px auto;
        padding: 40px 32px;
        background: var(--dark-glass);
        border: 2px solid rgba(0, 240, 255, 0.35);
        border-radius: 28px;
        backdrop-filter: blur(35px);
        box-shadow: 0 30px 70px rgba(0, 0, 0, 0.85), 0 0 40px rgba(0, 240, 255, 0.2);
        animation: modalDropIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes modalDropIn {
        from { opacity: 0; transform: scale(0.9) translateY(30px); }
        to { opacity: 1; transform: scale(1) translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. Database Management (Sessions & 1-Gmail Vault)
# ----------------------------------------------------
DB_FILE = "users_workspace.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            session_title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users (email)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT,
            content TEXT,
            is_image INTEGER DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

def hash_pass(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_user_exists(email: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT email FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
    user = c.fetchone()
    conn.close()
    return user is not None

def register_user(email: str, password: str) -> bool:
    clean_email = email.lower().strip()
    if check_user_exists(clean_email):
        return False
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (clean_email, hash_pass(password)))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def authenticate_user(email: str, password: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE LOWER(email) = LOWER(?)", (email.lower().strip(),))
    res = c.fetchone()
    conn.close()
    if res and res[0] == hash_pass(password):
        return True
    return False

def create_new_session(email: str, title: str = "New Chat") -> int:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO chat_sessions (user_email, session_title) VALUES (?, ?)", (email.lower().strip(), title))
    sess_id = c.lastrowid
    conn.commit()
    conn.close()
    return sess_id

def get_user_sessions(email: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, session_title FROM chat_sessions WHERE LOWER(user_email) = LOWER(?) ORDER BY id DESC", (email.strip(),))
    rows = c.fetchall()
    conn.close()
    return rows

def rename_session(session_id: int, new_title: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE chat_sessions SET session_title = ? WHERE id = ?", (new_title, session_id))
    conn.commit()
    conn.close()

def delete_session(session_id: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

def save_message_to_db(session_id: int, role: str, content: str, is_image: int = 0):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO chat_messages (session_id, role, content, is_image) VALUES (?, ?, ?, ?)",
              (session_id, role, content, is_image))
    conn.commit()
    conn.close()

def load_session_messages(session_id: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT role, content, is_image FROM chat_messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1], "is_generated_image": bool(r[2])} for r in rows]

# ----------------------------------------------------
# 4. Backend Tunnel Endpoint
# ----------------------------------------------------
OLLAMA_BASE_URL = "https://wake-figure-antiques-tub.trycloudflare.com"

# ----------------------------------------------------
# 5. Persistent Authentication State
# ----------------------------------------------------
saved_user = st.query_params.get("user", None)

if "authenticated_user" not in st.session_state:
    if saved_user and check_user_exists(saved_user):
        st.session_state.authenticated_user = saved_user
    else:
        st.session_state.authenticated_user = None

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

# ----------------------------------------------------
# 6. Hologram Authentication View
# ----------------------------------------------------
if not st.session_state.authenticated_user:
    st.markdown("""
    <div class='cyber-auth-modal'>
        <div style='text-align: center; margin-bottom: 24px;'>
            <div class='reactor-core'></div>
            <span style='font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase; color: #00f0ff;'>Neural Gateway</span>
            <h2 style='margin: 8px 0 4px 0; font-weight: 800; font-size: 1.9rem;'>AI MATRIX</h2>
            <p style='color: #94a3b8; font-size: 0.85rem; margin: 0;'>Secure access to personal workspace</p>
        </div>
    """, unsafe_allow_html=True)

    auth_mode = st.radio("Mode", ["Sign In", "Create Account"], horizontal=True, label_visibility="collapsed")
    
    email_input = st.text_input("Gmail Address", placeholder="name@gmail.com")
    pass_input = st.text_input("Password", type="password", placeholder="••••••••••••")

    if auth_mode == "Sign In":
        if st.button("AUTHENTICATE SESSION", use_container_width=True):
            clean_email = email_input.lower().strip()
            if not clean_email.endswith("@gmail.com"):
                st.error("Valid @gmail.com address required.")
            elif not check_user_exists(clean_email):
                st.error("Account not found. Please create an account first.")
            elif authenticate_user(clean_email, pass_input):
                st.session_state.authenticated_user = clean_email
                st.query_params["user"] = clean_email
                st.rerun()
            else:
                st.error("Invalid credentials.")
    else:
        if st.button("INITIALIZE SECURE VAULT", use_container_width=True):
            clean_email = email_input.lower().strip()
            if not clean_email.endswith("@gmail.com"):
                st.error("Only @gmail.com addresses are permitted.")
            elif len(pass_input) < 6:
                st.error("Password must be at least 6 characters long.")
            elif check_user_exists(clean_email):
                st.error("This Gmail is already registered and permanently locked.")
            else:
                if register_user(clean_email, pass_input):
                    st.success("Account created successfully! Switch to Sign In.")
                else:
                    st.error("Registration failed. Please try again.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ----------------------------------------------------
# 7. Authenticated App Workspace
# ----------------------------------------------------
user_email = st.session_state.authenticated_user

# Ensure active session exists
user_sessions = get_user_sessions(user_email)
if not user_sessions:
    new_id = create_new_session(user_email, "General Chat")
    st.session_state.current_session_id = new_id
    user_sessions = get_user_sessions(user_email)
elif st.session_state.current_session_id is None:
    st.session_state.current_session_id = user_sessions[0][0]

# ----------------------------------------------------
# 8. Animated Hologram Sidebar
# ----------------------------------------------------
with st.sidebar:
    st.markdown("### ⚡ AI Core")
    
    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True):
        new_sess_id = create_new_session(user_email, "New Chat")
        st.session_state.current_session_id = new_sess_id
        st.rerun()

    st.markdown("---")
    
    # Active Session Rename Tool
    active_title = "Chat"
    for s_id, s_title in user_sessions:
        if s_id == st.session_state.current_session_id:
            active_title = s_title
            break
            
    with st.expander("✏️ Rename Active Chat"):
        new_title_input = st.text_input("Title", value=active_title)
        if st.button("Update Title", use_container_width=True):
            if new_title_input.strip():
                rename_session(st.session_state.current_session_id, new_title_input.strip())
                st.rerun()

    st.markdown("#### 💬 Saved Sessions")
    
    # Session List with Delete Controls
    for s_id, s_title in user_sessions:
        col_select, col_del = st.columns([8, 2])
        with col_select:
            is_active = (s_id == st.session_state.current_session_id)
            label = f"⚡ {s_title}" if is_active else s_title
            if st.button(label, key=f"session_{s_id}", use_container_width=True):
                st.session_state.current_session_id = s_id
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"delete_{s_id}"):
                delete_session(s_id)
                st.session_state.current_session_id = None
                st.rerun()

    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated_user = None
        st.session_state.current_session_id = None
        if "user" in st.query_params:
            del st.query_params["user"]
        st.rerun()

# ----------------------------------------------------
# 9. Main Visual Stream
# ----------------------------------------------------
st.markdown(f"""
<div class="holo-header">
    <div style="display: flex; align-items: center;">
        <span class="reactor-core"></span>
        <span style="font-size: 1.35rem; font-weight: 800; letter-spacing: -0.3px;">{active_title}</span>
    </div>
    <div style="font-size: 0.82rem; color: #94a3b8;">
        ID: <code style="color: #00f0ff;">{user_email}</code>
    </div>
</div>
""", unsafe_allow_html=True)

# Load current session's messages
current_messages = load_session_messages(st.session_state.current_session_id)

# Render Chat Feed
for msg in current_messages:
    with st.chat_message(msg["role"]):
        if msg.get("is_generated_image"):
            st.image(msg["content"], caption="Generated Visual", use_container_width=True)
        else:
            st.markdown(msg["content"])

# Helpers
def encode_img_to_base64(file_obj):
    img = Image.open(file_obj)
    buf = BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def is_image_request(prompt: str) -> bool:
    triggers = ["photo banao", "image banao", "tasveer banao", "draw", "generate image", "create image", "picture of", "render image"]
    return any(k in prompt.lower() for k in triggers)

# ----------------------------------------------------
# 10. Integrated Chat Input with Native '+' Attachment
# ----------------------------------------------------
user_input = st.chat_input(
    "Ask anything, upload diagrams/formulas via (+), or describe an image...",
    accept_file="multiple",
    file_type=["png", "jpg", "jpeg"]
)

# ----------------------------------------------------
# 11. Execution Pipeline
# ----------------------------------------------------
if user_input:
    user_query = user_input.text if hasattr(user_input, "text") else str(user_input)
    attached_files = getattr(user_input, "files", [])

    if not user_query and not attached_files:
        st.stop()

    if not user_query and attached_files:
        user_query = "Read this image thoroughly and solve/explain step by step."

    if active_title in ["New Chat", "New Session"] and len(current_messages) == 0:
        short_name = user_query[:24] + "..." if len(user_query) > 24 else user_query
        rename_session(st.session_state.current_session_id, short_name)

    base64_img = None
    if attached_files and len(attached_files) > 0:
        base64_img = encode_img_to_base64(attached_files[0])

    # Save & Render User Query
    save_message_to_db(st.session_state.current_session_id, "user", user_query, 0)
    with st.chat_message("user"):
        if attached_files and len(attached_files) > 0:
            st.image(attached_files[0], width=320)
        st.markdown(user_query)

    # Assistant Response Pipeline
    with st.chat_message("assistant"):
        
        # 1. Text-To-Image Synthesis
        if is_image_request(user_query):
            with st.spinner("Synthesizing neural visual..."):
                encoded_prompt = urllib.parse.quote(user_query)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
                st.image(image_url, caption=f"Prompt: {user_query}", use_container_width=True)
                save_message_to_db(st.session_state.current_session_id, "assistant", image_url, 1)

        # 2. Vision OCR & Diagram Reasoning
        elif base64_img:
            with st.spinner("Processing visual matrix..."):
                payload = {
                    "model": "moondream",
                    "messages": [{
                        "role": "user",
                        "content": user_query,
                        "images": [base64_img]
                    }],
                    "stream": False
                }
                try:
                    res = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=120)
                    if res.status_code == 200:
                        out = res.json().get("message", {}).get("content", "No output generated.")
                        st.markdown(out)
                        save_message_to_db(st.session_state.current_session_id, "assistant", out, 0)
                    else:
                        st.error(f"Vision Server Alert: {res.status_code}")
                except Exception as ex:
                    st.error(f"Connection failure: {str(ex)}")

        # 3. High-Precision STEM Reasoning (Qwen 3B)
        else:
            system_instruction = {
                "role": "system",
                "content": "You are an expert AI specializing in mathematics, computer algorithms, and universal knowledge. Provide step-by-step, clean, and verified answers."
            }

            clean_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in current_messages[-4:]
                if not m.get("is_generated_image")
            ]

            payload = {
                "model": "qwen2.5:3b",
                "messages": [system_instruction] + clean_messages + [{"role": "user", "content": user_query}],
                "keep_alive": "24h",
                "options": {
                    "num_thread": 4,
                    "num_ctx": 1024,
                    "temperature": 0.3
                },
                "stream": True
            }

            try:
                response = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, stream=True, timeout=90)
                if response.status_code == 200:
                    placeholder = st.empty()
                    aggregated_text = ""
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line.decode("utf-8"))
                            chunk = data.get("message", {}).get("content", "")
                            aggregated_text += chunk
                            placeholder.markdown(aggregated_text + "▌")
                    placeholder.markdown(aggregated_text)
                    save_message_to_db(st.session_state.current_session_id, "assistant", aggregated_text, 0)
                else:
                    st.error(f"Server Alert: Status {response.status_code}")
            except Exception as ex:
                st.error(f"Stream error: {str(ex)}")
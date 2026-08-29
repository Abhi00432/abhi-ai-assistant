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
    page_title="AI HyperCore",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 2. Extreme Cyber-Matrix Animated CSS Engine
# ----------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap');

    :root {
        --cyan-glow: #00f2fe;
        --purple-glow: #9d4edd;
        --blue-glow: #4facfe;
        --glass-panel: rgba(10, 15, 30, 0.72);
        --border-neon: rgba(0, 242, 254, 0.22);
    }

    * {
        font-family: 'Space Grotesk', sans-serif !important;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        background: rgba(3, 7, 18, 0.9) !important;
        border: 1px solid rgba(0, 242, 254, 0.2) !important;
        border-radius: 12px !important;
    }

    /* Ambient Matrix Mesh Dynamic Background */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(0, 242, 254, 0.08) 0%, transparent 40%),
                    radial-gradient(circle at 90% 80%, rgba(157, 78, 221, 0.1) 0%, transparent 45%),
                    linear-gradient(180deg, #02040a 0%, #060b18 50%, #010206 100%);
        background-attachment: fixed;
        color: #f1f5f9;
    }

    /* Top Laser Pulse Beam */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--cyan-glow), var(--purple-glow), transparent);
        box-shadow: 0 0 20px var(--cyan-glow);
        z-index: 9999;
    }

    /* Cyber Glass Header */
    .hologram-header {
        position: relative;
        background: var(--glass-panel);
        border: 1px solid var(--border-neon);
        border-radius: 20px;
        padding: 16px 26px;
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.6), inset 0 1px 1px rgba(255, 255, 255, 0.12);
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        animation: headerGlow 0.6s ease-out;
    }

    @keyframes headerGlow {
        from { opacity: 0; transform: translateY(-15px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Live Cyber Dot */
    .laser-dot {
        display: inline-block;
        width: 9px;
        height: 9px;
        background: var(--cyan-glow);
        border-radius: 50%;
        box-shadow: 0 0 15px var(--cyan-glow);
        animation: laserPulse 1.4s infinite ease-in-out;
        margin-right: 10px;
    }

    @keyframes laserPulse {
        0%, 100% { transform: scale(0.9); opacity: 0.7; }
        50% { transform: scale(1.3); opacity: 1; box-shadow: 0 0 20px var(--cyan-glow), 0 0 30px var(--purple-glow); }
    }

    /* Floating 3D Message Cards */
    [data-testid="stChatMessage"] {
        background: rgba(12, 18, 38, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 18px !important;
        backdrop-filter: blur(18px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
        margin-bottom: 14px;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        animation: msgIn 0.35s ease-out;
    }

    @keyframes msgIn {
        from { opacity: 0; transform: translateY(10px) scale(0.98); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    [data-testid="stChatMessage"]:hover {
        border-color: rgba(0, 242, 254, 0.4) !important;
        box-shadow: 0 15px 40px rgba(0, 242, 254, 0.12), 0 0 20px rgba(157, 78, 221, 0.08);
        transform: translateY(-2px);
    }

    /* Interactive Hologram Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(4, 8, 20, 0.88) !important;
        border-right: 1px solid var(--border-neon);
        backdrop-filter: blur(25px);
    }

    /* Cyber Glowing Buttons */
    .stButton>button {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.9) 0%, rgba(79, 172, 254, 0.9) 50%, rgba(157, 78, 221, 0.9) 100%) !important;
        color: #010409 !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 10px 18px !important;
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.3) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 10px 35px rgba(0, 242, 254, 0.6) !important;
        color: #000 !important;
    }

    /* Authentication Screen */
    .cyber-auth-card {
        max-width: 430px;
        margin: 50px auto;
        padding: 40px 32px;
        background: var(--glass-panel);
        border: 1px solid var(--border-neon);
        border-radius: 24px;
        backdrop-filter: blur(25px);
        box-shadow: 0 25px 55px rgba(0, 0, 0, 0.75), 0 0 30px rgba(0, 242, 254, 0.12);
        animation: authFly 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes authFly {
        from { opacity: 0; transform: scale(0.94) translateY(20px); }
        to { opacity: 1; transform: scale(1) translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. Database Layer (Sessions & Strict 1-Gmail Vault)
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
# 5. Persistent Authentication Controller
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
    <div class='cyber-auth-card'>
        <div style='text-align: center; margin-bottom: 25px;'>
            <div class='laser-dot'></div>
            <span style='font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase; color: #00f2fe;'>Workspace Gateway</span>
            <h2 style='margin: 10px 0 4px 0; font-weight: 700; font-size: 1.8rem; letter-spacing: -0.5px;'>AI CORE</h2>
            <p style='color: #94a3b8; font-size: 0.85rem; margin: 0;'>Sign in with your verified Gmail</p>
        </div>
    """, unsafe_allow_html=True)

    auth_mode = st.radio("Mode", ["Sign In", "Create Account"], horizontal=True, label_visibility="collapsed")
    
    email_input = st.text_input("Gmail Address", placeholder="name@gmail.com")
    pass_input = st.text_input("Password", type="password", placeholder="••••••••••••")

    if auth_mode == "Sign In":
        if st.button("SIGN IN TO TERMINAL", use_container_width=True):
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
                st.error("Incorrect credentials.")
    else:
        if st.button("CREATE SECURE ACCOUNT", use_container_width=True):
            clean_email = email_input.lower().strip()
            if not clean_email.endswith("@gmail.com"):
                st.error("Only @gmail.com addresses are permitted.")
            elif len(pass_input) < 6:
                st.error("Password must be at least 6 characters long.")
            elif check_user_exists(clean_email):
                st.error("This Gmail is already registered and locked.")
            else:
                if register_user(clean_email, pass_input):
                    st.success("Account created successfully! Please sign in.")
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
# 8. Interactive Sidebar Matrix (Chats & Management)
# ----------------------------------------------------
with st.sidebar:
    st.markdown("### ⚡ Workspace")
    
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

    st.markdown("#### 💬 Saved Chats")
    
    # Session List with Delete Controls
    for s_id, s_title in user_sessions:
        col_select, col_del = st.columns([8, 2])
        with col_select:
            is_active = (s_id == st.session_state.current_session_id)
            label = f"✨ {s_title}" if is_active else s_title
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
<div class="hologram-header">
    <div style="display: flex; align-items: center;">
        <span class="laser-dot"></span>
        <span style="font-size: 1.3rem; font-weight: 700; letter-spacing: -0.3px;">{active_title}</span>
    </div>
    <div style="font-size: 0.82rem; color: #94a3b8;">
        USER: <code style="color: #00f2fe;">{user_email}</code>
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

# Upload & Chat Inputs
uploaded_file = st.file_uploader("Upload Math / Science / Diagram Frame", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
user_query = st.chat_input("Ask any calculation, theory, code, or describe an image...")

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
# 10. Execution Engine (Qwen 3B + Vision + Image Gen)
# ----------------------------------------------------
if user_query:
    # Auto-rename "New Chat" on first message
    if active_title in ["New Chat", "New Session"] and len(current_messages) == 0:
        short_name = user_query[:24] + "..." if len(user_query) > 24 else user_query
        rename_session(st.session_state.current_session_id, short_name)

    base64_img = None
    if uploaded_file is not None:
        base64_img = encode_img_to_base64(uploaded_file)

    # Save & Render User Query
    save_message_to_db(st.session_state.current_session_id, "user", user_query, 0)
    with st.chat_message("user"):
        if uploaded_file is not None:
            st.image(uploaded_file, width=320)
        st.markdown(user_query)

    # Assistant Response Pipeline
    with st.chat_message("assistant"):
        
        # 1. Text-To-Image Synthesis
        if is_image_request(user_query):
            with st.spinner("Synthesizing neural render..."):
                encoded_prompt = urllib.parse.quote(user_query)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
                st.image(image_url, caption=f"Prompt: {user_query}", use_container_width=True)
                save_message_to_db(st.session_state.current_session_id, "assistant", image_url, 1)

        # 2. Vision OCR & Diagram Reasoning
        elif base64_img:
            with st.spinner("Analyzing image..."):
                payload = {
                    "model": "moondream",
                    "messages": [{
                        "role": "user",
                        "content": user_query if user_query else "Read this image thoroughly, transcribe all equations, and solve step by step.",
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
                "content": "You are an expert AI specializing in mathematics, algorithms, and general knowledge. Provide step-by-step, clean, and verified answers."
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
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
    page_title="NEURAL MATRIX // AI CORE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------------------------------
# 2. Elite Cyber-Glass Animated UI (CSS Engine)
# ----------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap');

    :root {
        --bg-deep: #05070f;
        --accent-cyan: #00f0ff;
        --accent-blue: #3b82f6;
        --accent-violet: #8b5cf6;
        --border-glass: rgba(0, 240, 255, 0.15);
        --glass-surface: rgba(13, 18, 36, 0.65);
    }

    * {
        font-family: 'Space Grotesk', sans-serif !important;
    }

    code, pre, .stCode {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Ambient Dynamic Animated Mesh Background */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(0, 240, 255, 0.05) 0%, transparent 40%),
                    radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.07) 0%, transparent 45%),
                    linear-gradient(180deg, #04060d 0%, #080c1a 50%, #03050a 100%);
        background-attachment: fixed;
        color: #f1f5f9;
    }

    /* Laser Top Glow Bar */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--accent-cyan), var(--accent-violet), transparent);
        z-index: 9999;
        box-shadow: 0 0 15px var(--accent-cyan);
    }

    /* Animated Cyber Auth Card */
    .auth-container {
        max-width: 440px;
        margin: 50px auto;
        padding: 40px 32px;
        background: var(--glass-surface);
        border: 1px solid var(--border-glass);
        border-radius: 24px;
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7),
                    0 0 30px rgba(0, 240, 255, 0.08),
                    inset 0 1px 1px rgba(255, 255, 255, 0.1);
        animation: cyberFloat 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
    }

    @keyframes cyberFloat {
        0% { opacity: 0; transform: translateY(30px) scale(0.96); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }

    /* Futuristic Header Banner */
    .core-header {
        background: var(--glass-surface);
        border: 1px solid var(--border-glass);
        border-radius: 20px;
        padding: 16px 24px;
        backdrop-filter: blur(20px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 25px;
    }

    .core-title {
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: 1px;
        background: linear-gradient(135deg, #ffffff 0%, var(--accent-cyan) 60%, var(--accent-violet) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .pulse-dot {
        height: 8px;
        width: 8px;
        background-color: var(--accent-cyan);
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 10px var(--accent-cyan);
        animation: pulseLive 1.5s infinite;
        margin-right: 8px;
    }

    @keyframes pulseLive {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 240, 255, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(0, 240, 255, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 240, 255, 0); }
    }

    /* Cyber Message Bubbles */
    [data-testid="stChatMessage"] {
        background: rgba(13, 19, 38, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 18px !important;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        margin-bottom: 14px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: messageSlide 0.4s ease-out;
    }

    @keyframes messageSlide {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }

    [data-testid="stChatMessage"]:hover {
        border-color: rgba(0, 240, 255, 0.25) !important;
        box-shadow: 0 10px 30px rgba(0, 240, 255, 0.08);
        transform: translateY(-2px);
    }

    /* Interactive Inputs & Neon Glow Buttons */
    .stTextInput input {
        background: rgba(10, 14, 28, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #f1f5f9 !important;
        border-radius: 12px !important;
        transition: all 0.25s ease;
    }

    .stTextInput input:focus {
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.3) !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.9) 0%, rgba(59, 130, 246, 0.9) 100%) !important;
        color: #030712 !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 20px rgba(0, 240, 255, 0.25) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 6px 25px rgba(0, 240, 255, 0.45) !important;
        color: #000000 !important;
    }

    /* Sidebar Matrix Glass */
    [data-testid="stSidebar"] {
        background: rgba(5, 8, 18, 0.85) !important;
        border-right: 1px solid var(--border-glass);
        backdrop-filter: blur(25px);
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. Database Layer (Strict Single Account Vault)
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
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            role TEXT,
            content TEXT,
            is_image INTEGER DEFAULT 0,
            FOREIGN KEY (user_email) REFERENCES users (email)
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
        c.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", 
                  (clean_email, hash_pass(password)))
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

def save_chat_to_db(email, role, content, is_image=0):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (user_email, role, content, is_image) VALUES (?, ?, ?, ?)",
              (email, role, content, is_image))
    conn.commit()
    conn.close()

def load_user_chats(email):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT role, content, is_image FROM chat_history WHERE user_email = ? ORDER BY id ASC", (email,))
    rows = c.fetchall()
    conn.close()
    chats = []
    for r in rows:
        chats.append({
            "role": r[0],
            "content": r[1],
            "is_generated_image": bool(r[2])
        })
    return chats

def clear_user_chats(email):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM chat_history WHERE user_email = ?", (email,))
    conn.commit()
    conn.close()

# ----------------------------------------------------
# 4. Backend Tunnel Endpoint
# ----------------------------------------------------
OLLAMA_BASE_URL = "https://wake-figure-antiques-tub.trycloudflare.com"

# ----------------------------------------------------
# 5. Persistent Session Matrix (Anti-Refresh Logout)
# ----------------------------------------------------
saved_user = st.query_params.get("user", None)

if "authenticated_user" not in st.session_state:
    if saved_user and check_user_exists(saved_user):
        st.session_state.authenticated_user = saved_user
    else:
        st.session_state.authenticated_user = None

if "messages" not in st.session_state:
    if st.session_state.authenticated_user:
        st.session_state.messages = load_user_chats(st.session_state.authenticated_user)
    else:
        st.session_state.messages = []

# ----------------------------------------------------
# 6. Futuristic Cyber Authentication Screen
# ----------------------------------------------------
if not st.session_state.authenticated_user:
    st.markdown("""
    <div class='auth-container'>
        <div style='text-align: center; margin-bottom: 20px;'>
            <span class='pulse-dot'></span>
            <span style='font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase; color: #00f0ff;'>Secure Gate</span>
            <h2 style='margin: 8px 0 4px 0; font-weight: 700; font-size: 1.8rem;'>Neural AI Portal</h2>
            <p style='color: #64748b; font-size: 0.88rem; margin: 0;'>Sign in with your verified Gmail</p>
        </div>
    """, unsafe_allow_html=True)

    auth_mode = st.radio("Mode", ["Access Terminal", "Initialize Account"], horizontal=True, label_visibility="collapsed")
    
    email_input = st.text_input("Gmail Address", placeholder="name@gmail.com")
    pass_input = st.text_input("Access Key (Password)", type="password", placeholder="••••••••••••")

    if auth_mode == "Access Terminal":
        if st.button("AUTHENTICATE SESSION", use_container_width=True):
            clean_email = email_input.lower().strip()
            if not clean_email.endswith("@gmail.com"):
                st.error("Access restricted: Valid @gmail.com required.")
            elif not check_user_exists(clean_email):
                st.error("Unrecognized ID. Initialize an account first.")
            elif authenticate_user(clean_email, pass_input):
                st.session_state.authenticated_user = clean_email
                st.query_params["user"] = clean_email
                st.session_state.messages = load_user_chats(st.session_state.authenticated_user)
                st.rerun()
            else:
                st.error("Authentication failed: Invalid credentials.")
    else:
        if st.button("LOCK & REGISTER IDENTITY", use_container_width=True):
            clean_email = email_input.lower().strip()
            if not clean_email.endswith("@gmail.com"):
                st.error("Registration requires a valid @gmail.com address.")
            elif len(pass_input) < 6:
                st.error("Key strength low: Minimum 6 characters required.")
            elif check_user_exists(clean_email):
                st.error("Identity locked: Account already established for this Gmail.")
            else:
                if register_user(clean_email, pass_input):
                    st.success("Identity established. Switch to Access Terminal to proceed.")
                else:
                    st.error("Registration encountered a database lock.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ----------------------------------------------------
# 7. Elite Interactive Workspace
# ----------------------------------------------------
user_email = st.session_state.authenticated_user

# Glass Header Bar
st.markdown(f"""
<div class="core-header">
    <div>
        <h2 class="core-title"><span class="pulse-dot"></span>NEURAL MATRIX</h2>
        <div style="font-size: 0.8rem; color: #64748b; margin-top: 2px;">IDENTIFIER: <code style="color: #00f0ff;">{user_email}</code></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Control Actions
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([7, 2, 2])
with ctrl_col2:
    if st.button("➕ New Thread", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
with ctrl_col3:
    if st.button("⏻ Disconnect", use_container_width=True):
        st.session_state.authenticated_user = None
        st.session_state.messages = []
        if "user" in st.query_params:
            del st.query_params["user"]
        st.rerun()

# Sidebar Control
with st.sidebar:
    st.markdown("### 🎛️ Terminal Options")
    if st.button("Clear Thread Archive", use_container_width=True):
        clear_user_chats(user_email)
        st.session_state.messages = []
        st.rerun()

# Render Past Chat Matrix
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("image_display"):
            st.image(msg["image_display"], caption="Context Visual", width=340)
        if msg.get("is_generated_image"):
            st.image(msg["content"], caption="Synthesized Render", use_container_width=True)
        else:
            st.markdown(msg["content"])

# Multi-Modal Upload & Query Box
uploaded_file = st.file_uploader("Upload Math Problem / Circuit / Diagram", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
user_query = st.chat_input("Submit query, math proof, algorithm specification, or describe an image...")

# Helper Functions
def encode_img_to_base64(file_obj):
    img = Image.open(file_obj)
    buf = BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def is_image_request(prompt: str) -> bool:
    triggers = ["photo banao", "image banao", "tasveer banao", "draw", "generate image", "create image", "picture of", "render image"]
    return any(k in prompt.lower() for k in triggers)

# ----------------------------------------------------
# 8. Neural Inference Engine
# ----------------------------------------------------
if user_query:
    user_entry = {"role": "user", "content": user_query}
    base64_img = None

    if uploaded_file is not None:
        base64_img = encode_img_to_base64(uploaded_file)
        user_entry["image_display"] = uploaded_file

    st.session_state.messages.append(user_entry)
    save_chat_to_db(user_email, "user", user_query, 0)

    with st.chat_message("user"):
        if uploaded_file is not None:
            st.image(uploaded_file, width=340)
        st.markdown(user_query)

    with st.chat_message("assistant"):
        
        # 1. Text-To-Image Generation Engine
        if is_image_request(user_query):
            with st.spinner("Synthesizing neural render..."):
                encoded_prompt = urllib.parse.quote(user_query)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
                st.image(image_url, caption=f"Render Prompt: {user_query}", use_container_width=True)
                
                st.session_state.messages.append({"role": "assistant", "content": image_url, "is_generated_image": True})
                save_chat_to_db(user_email, "assistant", image_url, 1)

        # 2. Vision / Image Analysis Engine
        elif base64_img:
            with st.spinner("Analyzing visual matrix..."):
                payload = {
                    "model": "moondream",
                    "messages": [{
                        "role": "user",
                        "content": user_query if user_query else "Read this visual input carefully, transcribe all text and equations, and solve step by step.",
                        "images": [base64_img]
                    }],
                    "stream": False
                }
                try:
                    res = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=120)
                    if res.status_code == 200:
                        out = res.json().get("message", {}).get("content", "No output generated.")
                        st.markdown(out)
                        st.session_state.messages.append({"role": "assistant", "content": out})
                        save_chat_to_db(user_email, "assistant", out, 0)
                    else:
                        st.error(f"Vision Engine Alert: Status {res.status_code}")
                except Exception as ex:
                    st.error(f"Neural Bridge Failure: {str(ex)}")

        # 3. High-Precision STEM / CS / Universal Reasoning (Qwen 3B Engine)
        else:
            universal_system_prompt = {
                "role": "system",
                "content": "You are an advanced AI specializing in mathematical rigor, engineering computations, algorithms, and general universal knowledge. Provide step-by-step, precise, and verified solutions."
            }

            clean_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[-4:]
                if not m.get("is_generated_image") and not m.get("image_display")
            ]

            payload = {
                "model": "qwen2.5:3b",
                "messages": [universal_system_prompt] + clean_messages,
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
                    st.session_state.messages.append({"role": "assistant", "content": aggregated_text})
                    save_chat_to_db(user_email, "assistant", aggregated_text, 0)
                else:
                    st.error(f"Inference Server Alert: Status code {response.status_code}")
            except Exception as ex:
                st.error(f"Stream Disruption: {str(ex)}")
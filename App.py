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
    page_title="Campus AI Workspace",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------------------------------
# 2. Clean Animated Dark UI
# ----------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 15% 15%, #0f172a 0%, #020617 100%);
        color: #f8fafc;
    }

    /* Animated Auth & Chat Containers */
    .auth-card {
        max-width: 420px;
        margin: 50px auto;
        padding: 35px 30px;
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        backdrop-filter: blur(16px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
        animation: fadeIn 0.6s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Chat Messages */
    [data-testid="stChatMessage"] {
        background: rgba(30, 41, 59, 0.45) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px);
        margin-bottom: 12px;
        animation: slideUp 0.3s ease-out;
    }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #38bdf8 0%, #2563eb 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. Database Management (Auth & User Data Storage)
# ----------------------------------------------------
DB_FILE = "users_workspace.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    """)
    # Chats history table
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

def register_user(email, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?)", (email.lower().strip(), hash_pass(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE email = ?", (email.lower().strip(),))
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
# 5. Session State Control
# ----------------------------------------------------
if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------------------------------
# 6. Authentication Screen (Single Gmail Login/Signup)
# ----------------------------------------------------
if not st.session_state.authenticated_user:
    st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-bottom: 5px;'>Sign In</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.9rem; margin-bottom: 25px;'>Access your workspace</p>", unsafe_allow_html=True)

    auth_mode = st.radio("Choose Mode", ["Login", "Create Account"], horizontal=True, label_visibility="collapsed")
    
    email_input = st.text_input("Gmail Address", placeholder="name@gmail.com")
    pass_input = st.text_input("Password", type="password", placeholder="Enter your password")

    if auth_mode == "Login":
        if st.button("Sign In to Workspace", use_container_width=True):
            if not email_input.endswith("@gmail.com"):
                st.error("Please enter a valid @gmail.com address.")
            elif authenticate_user(email_input, pass_input):
                st.session_state.authenticated_user = email_input.lower().strip()
                st.session_state.messages = load_user_chats(st.session_state.authenticated_user)
                st.rerun()
            else:
                st.error("Invalid Gmail or password.")
    else:
        if st.button("Create Secure Account", use_container_width=True):
            if not email_input.endswith("@gmail.com"):
                st.error("Only @gmail.com addresses are allowed.")
            elif len(pass_input) < 6:
                st.error("Password must be at least 6 characters long.")
            else:
                if register_user(email_input, pass_input):
                    st.success("Account created successfully! Please switch to Login.")
                else:
                    st.error("An account with this Gmail already exists.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ----------------------------------------------------
# 7. Authenticated Workspace
# ----------------------------------------------------
user_email = st.session_state.authenticated_user

# Top Navigation Bar
nav_col1, nav_col2 = st.columns([8, 2])
with nav_col1:
    st.markdown(f"### ✨ AI Workspace")
    st.caption(f"Logged in as: `{user_email}`")
with nav_col2:
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated_user = None
        st.session_state.messages = []
        st.rerun()

# Sidebar Controls
with st.sidebar:
    st.markdown("### Settings")
    selected_model = st.selectbox(
        "AI Engine",
        ["deepseek-r1:1.5b", "qwen2.5:3b", "qwen2.5-coder:1.5b"],
        index=0
    )
    if st.button("Clear Chat History", use_container_width=True):
        clear_user_chats(user_email)
        st.session_state.messages = []
        st.rerun()

# Render Past Chat Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("image_input"):
            st.image(msg["image_input"], caption="Attached Context", width=300)
        if msg.get("is_generated_image"):
            st.image(msg["content"], caption="Generated Output")
        else:
            st.markdown(msg["content"])

# Multi-Modal Upload & Chat Inputs
uploaded_file = st.file_uploader("Attach Image / Diagram (Optional)", type=["png", "jpg", "jpeg"])
user_query = st.chat_input("Ask a question, paste code/math, or describe an image to create...")

# Helper Methods
def encode_img(image_file):
    img = Image.open(image_file)
    buf = BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def check_image_intent(text: str) -> bool:
    triggers = ["create image", "generate image", "draw", "photo banao", "tasveer banao", "picture of"]
    return any(t in text.lower() for t in triggers)

# ----------------------------------------------------
# 8. Execution Pipeline
# ----------------------------------------------------
if user_query:
    # 1. Process & Save User Query
    user_entry = {"role": "user", "content": user_query}
    img_b64 = None

    if uploaded_file is not None:
        img_b64 = encode_img(uploaded_file)
        user_entry["image_input"] = uploaded_file

    st.session_state.messages.append(user_entry)
    save_chat_to_db(user_email, "user", user_query, 0)

    with st.chat_message("user"):
        if uploaded_file is not None:
            st.image(uploaded_file, width=300)
        st.markdown(user_query)

    # 2. Assistant Response
    with st.chat_message("assistant"):
        
        # Route 1: Image Generation
        if check_image_intent(user_query):
            with st.spinner("Creating image..."):
                encoded = urllib.parse.quote(user_query)
                img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"
                st.image(img_url, caption="Generated Image")
                
                st.session_state.messages.append({"role": "assistant", "content": img_url, "is_generated_image": True})
                save_chat_to_db(user_email, "assistant", img_url, 1)

        # Route 2: Multimodal Image Input (Vision)
        elif img_b64:
            with st.spinner("Analyzing image..."):
                payload = {
                    "model": "moondream",
                    "messages": [{
                        "role": "user",
                        "content": user_query if user_query else "Analyze and solve this image step by step.",
                        "images": [img_b64]
                    }],
                    "stream": False
                }
                try:
                    res = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=90)
                    if res.status_code == 200:
                        out = res.json().get("message", {}).get("content", "")
                        st.markdown(out)
                        st.session_state.messages.append({"role": "assistant", "content": out})
                        save_chat_to_db(user_email, "assistant", out, 0)
                    else:
                        st.error(f"Vision error (Status {res.status_code})")
                except Exception as e:
                    st.error(f"Connection failed: {str(e)}")

        # Route 3: Fast Streaming Text & Code
        else:
            safe_history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[-3:]
                if not m.get("is_generated_image") and not m.get("image_input")
            ]

            payload = {
                "model": selected_model,
                "messages": safe_history,
                "keep_alive": "24h",
                "options": {
                    "num_thread": 4,
                    "num_ctx": 1024,
                    "temperature": 0.5
                },
                "stream": True
            }

            try:
                response = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, stream=True, timeout=90)
                if response.status_code == 200:
                    placeholder = st.empty()
                    full_text = ""
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line.decode("utf-8"))
                            full_text += data.get("message", {}).get("content", "")
                            placeholder.markdown(full_text + "▌")
                    placeholder.markdown(full_text)
                    st.session_state.messages.append({"role": "assistant", "content": full_text})
                    save_chat_to_db(user_email, "assistant", full_text, 0)
                else:
                    st.error(f"Backend Server Error {response.status_code}")
            except Exception as e:
                st.error(f"Network error: {str(e)}")
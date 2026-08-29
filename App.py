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
    page_title="AI Workspace",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------------------------------
# 2. Clean Dark UI Styling
# ----------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 15% 15%, #0f172a 0%, #020617 100%);
        color: #f8fafc;
    }

    .auth-card {
        max-width: 420px;
        margin: 60px auto;
        padding: 35px 30px;
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        backdrop-filter: blur(16px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
    }

    [data-testid="stChatMessage"] {
        background: rgba(30, 41, 59, 0.45) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px);
        margin-bottom: 12px;
    }

    .stButton>button {
        background: linear-gradient(135deg, #38bdf8 0%, #2563eb 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 8px 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. Database Management (Strict 1-Gmail Lock)
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
# 5. Persistent Session & Refresh Handling
# ----------------------------------------------------
# Check query params on page refresh
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
# 6. Authentication Screen
# ----------------------------------------------------
if not st.session_state.authenticated_user:
    st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-bottom: 5px;'>Sign In</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.9rem; margin-bottom: 25px;'>Access your private workspace</p>", unsafe_allow_html=True)

    auth_mode = st.radio("Choose Mode", ["Login", "Create Account"], horizontal=True, label_visibility="collapsed")
    
    email_input = st.text_input("Gmail Address", placeholder="name@gmail.com")
    pass_input = st.text_input("Password", type="password", placeholder="Enter your password")

    if auth_mode == "Login":
        if st.button("Sign In", use_container_width=True):
            clean_email = email_input.lower().strip()
            if not clean_email.endswith("@gmail.com"):
                st.error("Please enter a valid @gmail.com address.")
            elif not check_user_exists(clean_email):
                st.error("This Gmail is not registered. Please create an account first.")
            elif authenticate_user(clean_email, pass_input):
                st.session_state.authenticated_user = clean_email
                st.query_params["user"] = clean_email  # Persist across refresh
                st.session_state.messages = load_user_chats(st.session_state.authenticated_user)
                st.rerun()
            else:
                st.error("Incorrect password for this Gmail account.")
    else:
        if st.button("Create Permanent Account", use_container_width=True):
            clean_email = email_input.lower().strip()
            if not clean_email.endswith("@gmail.com"):
                st.error("Only @gmail.com addresses are allowed.")
            elif len(pass_input) < 6:
                st.error("Password must be at least 6 characters long.")
            elif check_user_exists(clean_email):
                st.error("⚠️ This Gmail is already registered and locked. You cannot register again.")
            else:
                if register_user(clean_email, pass_input):
                    st.success("Account created successfully! Please switch to Login.")
                else:
                    st.error("Registration failed. Please try again.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ----------------------------------------------------
# 7. Authenticated Workspace
# ----------------------------------------------------
user_email = st.session_state.authenticated_user

# Top Navigation Bar
top_col1, top_col2, top_col3 = st.columns([6, 2, 2])
with top_col1:
    st.markdown(f"### ✨ AI Workspace")
    st.caption(f"Account: `{user_email}`")
with top_col2:
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
with top_col3:
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated_user = None
        st.session_state.messages = []
        if "user" in st.query_params:
            del st.query_params["user"]  # Clear persisted login
        st.rerun()

# Sidebar
with st.sidebar:
    st.markdown("### Workspace Options")
    if st.button("Delete Chat History", use_container_width=True):
        clear_user_chats(user_email)
        st.session_state.messages = []
        st.rerun()

# Render Past Chat Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("image_display"):
            st.image(msg["image_display"], caption="Attached Context", width=320)
        if msg.get("is_generated_image"):
            st.image(msg["content"], caption="Generated Image", use_container_width=True)
        else:
            st.markdown(msg["content"])

# Upload & Chat Inputs
uploaded_file = st.file_uploader("📎 Upload Image / Math Problem (Optional)", type=["png", "jpg", "jpeg"])
user_query = st.chat_input("Ask any question, solve math/code, or describe an image to create...")

# Helper Functions
def encode_img_to_base64(file_obj):
    img = Image.open(file_obj)
    buf = BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def is_image_request(prompt: str) -> bool:
    triggers = ["photo banao", "image banao", "tasveer banao", "draw", "generate image", "create image", "picture of"]
    return any(k in prompt.lower() for k in triggers)

# ----------------------------------------------------
# 8. Execution Pipeline
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
            st.image(uploaded_file, width=320)
        st.markdown(user_query)

    with st.chat_message("assistant"):
        
        # 1. Text-To-Image Generation
        if is_image_request(user_query):
            with st.spinner("Creating image..."):
                encoded_prompt = urllib.parse.quote(user_query)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
                st.image(image_url, caption="Generated Image", use_container_width=True)
                
                st.session_state.messages.append({"role": "assistant", "content": image_url, "is_generated_image": True})
                save_chat_to_db(user_email, "assistant", image_url, 1)

        # 2. Vision / Image Analysis
        elif base64_img:
            with st.spinner("Analyzing image..."):
                payload = {
                    "model": "moondream",
                    "messages": [{
                        "role": "user",
                        "content": user_query if user_query else "Read this image carefully, transcribe all text and equations, and solve step by step.",
                        "images": [base64_img]
                    }],
                    "stream": False
                }
                try:
                    res = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=120)
                    if res.status_code == 200:
                        out = res.json().get("message", {}).get("content", "No output.")
                        st.markdown(out)
                        st.session_state.messages.append({"role": "assistant", "content": out})
                        save_chat_to_db(user_email, "assistant", out, 0)
                    else:
                        st.error(f"Image analysis error: Status {res.status_code}")
                except Exception as ex:
                    st.error(f"Connection failed: {str(ex)}")

        # 3. Text, Math, Logic & Universal Queries (Qwen2.5:3b)
        else:
            universal_system_prompt = {
                "role": "system",
                "content": "You are a universal AI assistant capable of answering any question accurately, including STEM mathematics, programming, general world knowledge, and reasoning."
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
                    st.error(f"Server Error: Status code {response.status_code}")
            except Exception as ex:
                st.error(f"Network error: {str(ex)}")
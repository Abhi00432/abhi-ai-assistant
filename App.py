import streamlit as st
import psycopg2
import psycopg2.extras
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
    page_title="AI Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 2. Pure Native CSS (Zero DOM Manipulation Conflict)
# ----------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [data-testid="stAppViewContainer"], .main, p, span, div, h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background-color: #050b14;
        background-image: 
            radial-gradient(at 0% 0%, rgba(0, 240, 255, 0.12) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(0, 255, 135, 0.08) 0px, transparent 50%),
            radial-gradient(at 50% 50%, rgba(17, 9, 38, 0.5) 0px, transparent 100%);
        color: #f8fafc;
    }

    header, [data-testid="stHeader"] {
        background: transparent !important;
    }

    .stChatMessageContainer {
        padding: 0 !important;
        margin-bottom: 8px !important;
    }

    [data-testid="stChatMessage"] {
        background: rgba(10, 16, 35, 0.92) !important;
        border: 1px solid rgba(0, 240, 255, 0.25) !important;
        border-radius: 14px !important;
        padding: 8px 14px !important;
        max-width: 85% !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important;
    }

    code, pre, [data-testid="stCodeBlock"] {
        font-family: 'JetBrains Mono', monospace !important;
        background: rgba(3, 7, 18, 0.95) !important;
        border: 1px solid rgba(0, 240, 255, 0.25) !important;
        border-radius: 8px !important;
    }

    .laser-typing-cursor {
        display: inline-block;
        width: 3px;
        height: 16px;
        background: #00ff87;
        margin-left: 4px;
        vertical-align: middle;
        animation: blinkCursor 0.7s infinite alternate;
    }

    @keyframes blinkCursor {
        0% { opacity: 0.2; }
        100% { opacity: 1; }
    }

    .top-header {
        background: rgba(10, 16, 35, 0.9);
        border: 1px solid rgba(0, 240, 255, 0.25);
        border-radius: 14px;
        padding: 10px 16px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .pulse-dot {
        display: inline-block;
        width: 9px;
        height: 9px;
        background: #00ff87;
        border-radius: 50%;
        box-shadow: 0 0 10px #00ff87;
        margin-right: 8px;
    }

    .stButton>button {
        background: linear-gradient(135deg, #00f2fe 0%, #00ff87 100%) !important;
        color: #020617 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
    }

    .clean-auth-card {
        max-width: 420px;
        margin: 40px auto 10px auto;
        padding: 24px;
        background: rgba(10, 16, 35, 0.9);
        border: 1px solid rgba(0, 240, 255, 0.25);
        border-radius: 16px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. Robust Cloud Database Layer (Supabase Postgres)
# ----------------------------------------------------
def get_db_url():
    if "DB_URL" in st.secrets:
        return st.secrets["DB_URL"].strip()
    if "database" in st.secrets and "url" in st.secrets["database"]:
        return st.secrets["database"]["url"].strip()
    # Fallback Direct URI
    return "postgresql://postgres.jyrhiirspxylvlbkkowf:YOUR_PASSWORD@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres".strip()

def get_db_conn():
    return psycopg2.connect(get_db_url(), connect_timeout=10)

def hash_pass(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_user_exists(email: str) -> bool:
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT email FROM users WHERE LOWER(email) = LOWER(%s);", (email.strip(),))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user is not None
    except Exception:
        return False

def register_user(email: str, password: str) -> bool:
    clean_email = email.lower().strip()
    if check_user_exists(clean_email):
        return False
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s);",
            (clean_email, hash_pass(password))
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception:
        return False

def authenticate_user(email: str, password: str) -> bool:
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM users WHERE LOWER(email) = LOWER(%s);", (email.lower().strip(),))
        res = cur.fetchone()
        cur.close()
        conn.close()
        if res and res[0] == hash_pass(password):
            return True
        return False
    except Exception:
        return False

def create_new_session(email: str, title: str = "New Chat") -> int:
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_sessions (user_email, session_title) VALUES (%s, %s) RETURNING id;",
        (email.lower().strip(), title)
    )
    sess_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return sess_id

def get_user_sessions(email: str):
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, session_title FROM chat_sessions WHERE LOWER(user_email) = LOWER(%s) ORDER BY id DESC;",
            (email.strip(),)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception:
        return []

def rename_session(session_id: int, new_title: str):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE chat_sessions SET session_title = %s WHERE id = %s;", (new_title, session_id))
    conn.commit()
    cur.close()
    conn.close()

def delete_session(session_id: int):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM chat_messages WHERE session_id = %s;", (session_id,))
    cur.execute("DELETE FROM chat_sessions WHERE id = %s;", (session_id,))
    conn.commit()
    cur.close()
    conn.close()

def save_message_to_db(session_id: int, role: str, content: str, is_image: int = 0):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_messages (session_id, role, content, is_image) VALUES (%s, %s, %s, %s);",
        (session_id, role, content, is_image)
    )
    conn.commit()
    cur.close()
    conn.close()

def load_session_messages(session_id: int):
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT role, content, is_image FROM chat_messages WHERE session_id = %s ORDER BY id ASC;",
            (session_id,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"role": r[0], "content": r[1], "is_generated_image": bool(r[2])} for r in rows]
    except Exception:
        return []

# ----------------------------------------------------
# 4. Ollama Cloudflare Backend
# ----------------------------------------------------
OLLAMA_BASE_URL = "https://wake-figure-antiques-tub.trycloudflare.com".strip()

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
# 6. Authentication Screen
# ----------------------------------------------------
if not st.session_state.authenticated_user:
    col_l, col_center, col_r = st.columns([1, 1.8, 1])
    with col_center:
        st.markdown("""
        <div class='clean-auth-card'>
            <div class='pulse-dot'></div>
            <h3 style='margin: 8px 0 2px 0; font-weight: 700;'>AI Assistant</h3>
            <p style='color: #94a3b8; font-size: 0.85rem;'>Sign in to your workspace</p>
        </div>
        """, unsafe_allow_html=True)

        auth_tab1, auth_tab2 = st.tabs(["Sign In", "Create Account"])
        
        with auth_tab1:
            email_login = st.text_input("Gmail Address", key="login_email", placeholder="name@gmail.com")
            pass_login = st.text_input("Password", type="password", key="login_pass", placeholder="Enter password")
            if st.button("SIGN IN", key="btn_signin", use_container_width=True):
                clean_email = email_login.lower().strip()
                if not clean_email.endswith("@gmail.com"):
                    st.error("Valid @gmail.com address required.")
                elif not check_user_exists(clean_email):
                    st.error("Account not found. Please create an account first.")
                elif authenticate_user(clean_email, pass_login):
                    st.session_state.authenticated_user = clean_email
                    st.query_params["user"] = clean_email
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

        with auth_tab2:
            email_reg = st.text_input("Gmail Address", key="reg_email", placeholder="name@gmail.com")
            pass_reg = st.text_input("Password", type="password", key="reg_pass", placeholder="At least 6 characters")
            if st.button("CREATE ACCOUNT", key="btn_signup", use_container_width=True):
                clean_email = email_reg.lower().strip()
                if not clean_email.endswith("@gmail.com"):
                    st.error("Only @gmail.com addresses are permitted.")
                elif len(pass_reg) < 6:
                    st.error("Password must be at least 6 characters long.")
                elif check_user_exists(clean_email):
                    st.error("This Gmail is already registered and locked.")
                else:
                    if register_user(clean_email, pass_reg):
                        st.success("Account created! You can now Sign In.")
                    else:
                        st.error("Registration failed. Please try again.")

    st.stop()

# ----------------------------------------------------
# 7. Workspace Setup
# ----------------------------------------------------
user_email = st.session_state.authenticated_user

user_sessions = get_user_sessions(user_email)
if not user_sessions:
    new_id = create_new_session(user_email, "General Chat")
    st.session_state.current_session_id = new_id
    user_sessions = get_user_sessions(user_email)
elif st.session_state.current_session_id is None:
    st.session_state.current_session_id = user_sessions[0][0]

# ----------------------------------------------------
# 8. Sidebar Controls
# ----------------------------------------------------
with st.sidebar:
    st.markdown("### 💬 Chats")
    
    if st.button("➕ New Chat", use_container_width=True):
        new_sess_id = create_new_session(user_email, "New Chat")
        st.session_state.current_session_id = new_sess_id
        st.rerun()

    st.markdown("---")
    
    active_title = "Chat"
    for s_id, s_title in user_sessions:
        if s_id == st.session_state.current_session_id:
            active_title = s_title
            break
            
    with st.expander("✏️ Rename Chat"):
        new_title_input = st.text_input("Title", value=active_title)
        if st.button("Save", use_container_width=True):
            if new_title_input.strip():
                rename_session(st.session_state.current_session_id, new_title_input.strip())
                st.rerun()

    st.markdown("#### Saved Chats")
    
    for s_id, s_title in user_sessions:
        col_select, col_del = st.columns([8, 2])
        with col_select:
            is_active = (s_id == st.session_state.current_session_id)
            label = f"👉 {s_title}" if is_active else s_title
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
# 9. Main Stream
# ----------------------------------------------------
st.markdown(f"""
<div class="top-header">
    <div style="display: flex; align-items: center;">
        <span class="pulse-dot"></span>
        <span style="font-size: 1.1rem; font-weight: 700;">{active_title}</span>
    </div>
    <div style="font-size: 0.8rem; color: #94a3b8;">
        User: <code style="color: #00ff87;">{user_email}</code>
    </div>
</div>
""", unsafe_allow_html=True)

current_messages = load_session_messages(st.session_state.current_session_id)

for msg in current_messages:
    avatar_icon = "🤖" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        if msg.get("is_generated_image"):
            st.image(msg["content"], caption="Generated Image", use_container_width=True)
        else:
            st.markdown(msg["content"])

# Helpers
def encode_img_to_base64(file_obj):
    img = Image.open(file_obj)
    img.thumbnail((512, 512))
    buf = BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=70)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def is_image_request(prompt: str) -> bool:
    triggers = ["photo banao", "image banao", "tasveer banao", "draw", "generate image", "create image", "picture of", "render image"]
    return any(k in prompt.lower() for k in triggers)

# ----------------------------------------------------
# 10. Integrated Chat Input
# ----------------------------------------------------
user_input = st.chat_input(
    "Ask a question, paste code/math, or attach an image via (+)...",
    accept_file="multiple",
    file_type=["png", "jpg", "jpeg"]
)

# ----------------------------------------------------
# 11. STEM Math & Reasoning Execution Engine
# ----------------------------------------------------
if user_input:
    user_query = user_input.text if hasattr(user_input, "text") else str(user_input)
    attached_files = getattr(user_input, "files", [])

    if not user_query and not attached_files:
        st.stop()

    if not user_query and attached_files:
        user_query = "Read this image carefully and solve step by step."

    if active_title in ["New Chat", "General Chat"] and len(current_messages) == 0:
        short_name = user_query[:24] + "..." if len(user_query) > 24 else user_query
        rename_session(st.session_state.current_session_id, short_name)

    base64_img = None
    if attached_files and len(attached_files) > 0:
        base64_img = encode_img_to_base64(attached_files[0])

    save_message_to_db(st.session_state.current_session_id, "user", user_query, 0)
    with st.chat_message("user", avatar="👤"):
        if attached_files and len(attached_files) > 0:
            st.image(attached_files[0], width=300)
        st.markdown(user_query)

    with st.chat_message("assistant", avatar="🤖"):
        
        # 1. Text-To-Image Generation
        if is_image_request(user_query):
            with st.spinner("Generating image..."):
                encoded_prompt = urllib.parse.quote(user_query)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
                st.image(image_url, caption=f"Prompt: {user_query}", use_container_width=True)
                save_message_to_db(st.session_state.current_session_id, "assistant", image_url, 1)

        # 2. Vision OCR & Math Solver
        elif base64_img:
            with st.spinner("Analyzing image..."):
                vision_instruction = (
                    "You are an expert mathematician. "
                    "Transcribe all formulas into standard LaTeX ($$ for blocks, $ for inline) and solve directly step-by-step."
                )
                
                payload = {
                    "model": "minicpm-v",
                    "messages": [
                        {"role": "system", "content": vision_instruction},
                        {
                            "role": "user",
                            "content": f"{user_query}\n\nSolve step-by-step.",
                            "images": [base64_img]
                        }
                    ],
                    "options": {
                        "num_thread": 4,
                        "num_ctx": 512,
                        "temperature": 0.1,
                        "repeat_penalty": 1.15
                    },
                    "stream": True
                }
                try:
                    response = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, stream=True, timeout=120)
                    if response.status_code == 200:
                        placeholder = st.empty()
                        aggregated_text = ""
                        for line in response.iter_lines():
                            if line:
                                data = json.loads(line.decode("utf-8"))
                                chunk = data.get("message", {}).get("content", "")
                                aggregated_text += chunk
                                placeholder.markdown(aggregated_text + "<span class='laser-typing-cursor'></span>", unsafe_allow_html=True)
                        placeholder.markdown(aggregated_text)
                        save_message_to_db(st.session_state.current_session_id, "assistant", aggregated_text, 0)
                    else:
                        st.error(f"Vision Server Alert: Status {response.status_code}")
                except Exception as ex:
                    st.error(f"Connection failure: {str(ex)}")

        # 3. High-Speed Direct Math Solver (Qwen Coder Engine)
        else:
            system_prompt = {
                "role": "system",
                "content": (
                    "You are an expert IIT Mathematics and Algorithms Professor. "
                    "Provide direct, accurate, step-by-step solutions. "
                    "For integral equations involving f(x-t), always recognize them as convolution integrals and use variable substitution u = x - t before differentiating. "
                    "Always format mathematical equations cleanly using double dollar signs $$...$$ for display blocks and single dollar signs $...$ for inline math."
                )
            }

            clean_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in current_messages[-2:]
                if not m.get("is_generated_image")
            ]

            payload = {
                "model": "qwen2.5-coder:1.5b",
                "messages": [system_prompt] + clean_messages + [{"role": "user", "content": user_query}],
                "keep_alive": "24h",
                "options": {
                    "num_thread": 4,
                    "num_ctx": 768,
                    "temperature": 0.1,
                    "repeat_penalty": 1.15,
                    "top_k": 40,
                    "top_p": 0.9
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
                            placeholder.markdown(aggregated_text + "<span class='laser-typing-cursor'></span>", unsafe_allow_html=True)
                    placeholder.markdown(aggregated_text)
                    save_message_to_db(st.session_state.current_session_id, "assistant", aggregated_text, 0)
                else:
                    st.error(f"Server Alert: Status {response.status_code}")
            except Exception as ex:
                st.error(f"Stream error: {str(ex)}")
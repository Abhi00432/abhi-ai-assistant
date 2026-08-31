import streamlit as st
import psycopg2
from psycopg2 import pool
import hashlib
import requests
import json
import base64
import urllib.parse
from io import BytesIO
from PIL import Image

# ----------------------------------------------------
# 1. Page Configuration (Mobile Optimized)
# ----------------------------------------------------
st.set_page_config(
    page_title="AI Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"  # Mobile me default collapse rahega taaki screen clean rahe
)

# ----------------------------------------------------
# 2. Ultra Fast Mobile CSS Engine
# ----------------------------------------------------
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    /* System Native Fonts for 0ms font blocking */
    html, body, [data-testid="stAppViewContainer"], .main {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        text-rendering: optimizeSpeed;
    }

    /* GPU Accelerated Lightweight Background */
    .stApp {
        background: #030712 !important;
        color: #f8fafc;
        transform: translateZ(0);
    }

    header, [data-testid="stHeader"] {
        display: none !important;
    }

    /* Mobile Chat Bubbles */
    .stChatMessageContainer {
        padding: 0 !important;
        margin-bottom: 6px !important;
        contain: content;
    }

    [data-testid="stChatMessage"] {
        background: rgba(10, 16, 35, 0.96) !important;
        border: 1px solid rgba(0, 240, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 8px 12px !important;
        max-width: 90% !important;
        box-shadow: none !important;
    }

    /* User Message: Right / Assistant: Left */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        border-left: 3px solid #00f0ff !important;
        margin-left: auto !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        border-left: 3px solid #00ff87 !important;
        margin-right: auto !important;
    }

    /* Code blocks optimization */
    code, pre, [data-testid="stCodeBlock"] {
        font-family: monospace !important;
        background: #000000 !important;
        border: 1px solid rgba(0, 240, 255, 0.2) !important;
        border-radius: 6px !important;
        white-space: pre-wrap !important;
        word-break: break-all !important;
    }

    .laser-typing-cursor {
        display: inline-block;
        width: 2px;
        height: 14px;
        background: #00ff87;
        margin-left: 3px;
        vertical-align: middle;
    }

    .top-header {
        background: rgba(10, 16, 35, 0.95);
        border: 1px solid rgba(0, 240, 255, 0.25);
        border-radius: 12px;
        padding: 8px 14px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #00ff87;
        border-radius: 50%;
        margin-right: 6px;
    }

    /* Touch-friendly buttons */
    .stButton>button {
        background: linear-gradient(135deg, #00f2fe 0%, #00ff87 100%) !important;
        color: #020617 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        min-height: 42px !important;
    }

    .clean-auth-card {
        max-width: 380px;
        margin: 20px auto 10px auto;
        padding: 18px;
        background: rgba(10, 16, 35, 0.95);
        border: 1px solid rgba(0, 240, 255, 0.25);
        border-radius: 14px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. Cloud Database Layer (Supabase Pooling)
# ----------------------------------------------------
@st.cache_resource
def get_db_pool():
    if "DB_URL" in st.secrets:
        db_url = st.secrets["DB_URL"].strip()
    elif "database" in st.secrets and "url" in st.secrets["database"]:
        db_url = st.secrets["database"]["url"].strip()
    else:
        db_url = "postgresql://postgres.jyrhiirspxylvlbkkowf:AbhiJangir%4006@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres".strip()
    return pool.SimpleConnectionPool(1, 4, db_url)

def get_db_conn():
    return get_db_pool().getconn()

def release_db_conn(conn):
    if conn:
        get_db_pool().putconn(conn)

def hash_pass(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_user_exists(email: str) -> bool:
    conn = None
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT email FROM users WHERE LOWER(email) = LOWER(%s);", (email.strip(),))
        user = cur.fetchone()
        cur.close()
        return user is not None
    except Exception:
        return False
    finally:
        release_db_conn(conn)

def register_user(email: str, password: str) -> bool:
    clean_email = email.lower().strip()
    if check_user_exists(clean_email):
        return False
    conn = None
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s);",
            (clean_email, hash_pass(password))
        )
        conn.commit()
        cur.close()
        return True
    except Exception:
        return False
    finally:
        release_db_conn(conn)

def authenticate_user(email: str, password: str) -> bool:
    conn = None
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM users WHERE LOWER(email) = LOWER(%s);", (email.lower().strip(),))
        res = cur.fetchone()
        cur.close()
        if res and res[0] == hash_pass(password):
            return True
        return False
    except Exception:
        return False
    finally:
        release_db_conn(conn)

def create_new_session(email: str, title: str = "New Chat") -> int:
    conn = None
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat_sessions (user_email, session_title) VALUES (%s, %s) RETURNING id;",
            (email.lower().strip(), title)
        )
        sess_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return sess_id
    finally:
        release_db_conn(conn)

def get_user_sessions(email: str):
    conn = None
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, session_title FROM chat_sessions WHERE LOWER(user_email) = LOWER(%s) ORDER BY id DESC;",
            (email.strip(),)
        )
        rows = cur.fetchall()
        cur.close()
        return rows
    except Exception:
        return []
    finally:
        release_db_conn(conn)

def rename_session(session_id: int, new_title: str):
    conn = None
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("UPDATE chat_sessions SET session_title = %s WHERE id = %s;", (new_title, session_id))
        conn.commit()
        cur.close()
    finally:
        release_db_conn(conn)

def delete_session(session_id: int):
    conn = None
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM chat_messages WHERE session_id = %s;", (session_id,))
        cur.execute("DELETE FROM chat_sessions WHERE id = %s;", (session_id,))
        conn.commit()
        cur.close()
    finally:
        release_db_conn(conn)

def save_message_to_db(session_id: int, role: str, content: str, is_image: int = 0):
    conn = None
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat_messages (session_id, role, content, is_image) VALUES (%s, %s, %s, %s);",
            (session_id, role, content, is_image)
        )
        conn.commit()
        cur.close()
    finally:
        release_db_conn(conn)

def load_session_messages(session_id: int):
    conn = None
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT role, content, is_image FROM chat_messages WHERE session_id = %s ORDER BY id ASC;",
            (session_id,)
        )
        rows = cur.fetchall()
        cur.close()
        return [{"role": r[0], "content": r[1], "is_generated_image": bool(r[2])} for r in rows]
    except Exception:
        return []
    finally:
        release_db_conn(conn)

# ----------------------------------------------------
# 4. Backend Tunnel Endpoint
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
    col_l, col_center, col_r = st.columns([1, 2, 1])
    with col_center:
        st.markdown("""
        <div class='clean-auth-card'>
            <div class='pulse-dot'></div>
            <h3 style='margin: 4px 0 2px 0; font-weight: 700;'>AI Assistant</h3>
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
                    st.error("This Gmail is already registered.")
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
        <span style="font-size: 1rem; font-weight: 700;">{active_title}</span>
    </div>
    <div style="font-size: 0.75rem; color: #94a3b8;">
        <code style="color: #00ff87;">{user_email}</code>
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

# Image compression
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
    "Ask question, math problem or attach image...",
    accept_file="multiple",
    file_type=["png", "jpg", "jpeg"]
)

# ----------------------------------------------------
# 11. Ultra Low-Latency Execution Pipeline
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

        # 3. High-Speed Direct Math Solver (Qwen Coder)
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
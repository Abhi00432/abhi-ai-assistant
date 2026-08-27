import streamlit as st
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
    page_title="HyperCore 4D AI Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 2. 4D Spatial Neumorphic UI / Custom CSS
# ----------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;900&family=JetBrains+Mono:wght@400;600&display=swap');

    :root {
        --bg-gradient: radial-gradient(circle at 10% 20%, rgb(10, 12, 24) 0%, rgb(18, 22, 38) 45.2%, rgb(8, 10, 18) 90%);
        --card-bg: rgba(22, 27, 46, 0.65);
        --card-border: rgba(255, 255, 255, 0.08);
        --accent-cyan: #00f2fe;
        --accent-indigo: #4facfe;
        --accent-purple: #7f00ff;
        --glow-shadow: 0 8px 32px 0 rgba(0, 242, 254, 0.18);
        --neumorphic-depth: -8px -8px 20px rgba(255, 255, 255, 0.02), 8px 8px 24px rgba(0, 0, 0, 0.7);
    }

    * {
        font-family: 'Outfit', sans-serif;
    }

    .stApp {
        background: var(--bg-gradient);
        color: #e0e6ed;
    }

    /* 4D Hero Header */
    .hero-container {
        position: relative;
        padding: 24px 30px;
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 20px;
        box-shadow: var(--neumorphic-depth), var(--glow-shadow);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        margin-bottom: 25px;
        overflow: hidden;
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo), var(--accent-purple));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        color: #8c9ba5;
        font-size: 0.95rem;
        margin-top: 6px;
        font-weight: 400;
    }

    /* Glass Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(12, 16, 30, 0.85) !important;
        border-right: 1px solid var(--card-border);
        backdrop-filter: blur(20px);
    }

    /* Neumorphic 4D Chat Bubbles */
    [data-testid="stChatMessage"] {
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 18px !important;
        box-shadow: var(--neumorphic-depth);
        backdrop-filter: blur(12px);
        margin-bottom: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    [data-testid="stChatMessage"]:hover {
        transform: translateY(-2px);
        box-shadow: var(--neumorphic-depth), 0 0 20px rgba(79, 172, 254, 0.15);
    }

    /* Code Blocks Styling */
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        background: rgba(8, 11, 20, 0.9) !important;
        border-radius: 10px;
    }

    /* Action Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        color: #070a13 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 18px !important;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 25px rgba(0, 242, 254, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. Backend Connection Configurations
# ----------------------------------------------------
OLLAMA_BASE_URL = "https://wake-figure-antiques-tub.trycloudflare.com"

# ----------------------------------------------------
# 4. Session State Management
# ----------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ----------------------------------------------------
# 5. Core Utility Engine
# ----------------------------------------------------
def serialize_image_to_base64(image_stream):
    """Encodes and compresses uploaded images into standard Base64 string."""
    raw_img = Image.open(image_stream)
    buffer = BytesIO()
    raw_img.convert("RGB").save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def detect_visual_synthesis_intent(prompt_text: str) -> bool:
    """Detects if user intends to generate an AI image."""
    synthesis_triggers = [
        "generate image", "create image", "draw", "generate photo", 
        "render picture", "picture of", "design artwork", "illustrate", "image of"
    ]
    query = prompt_text.lower()
    return any(keyword in query for keyword in synthesis_triggers)

# ----------------------------------------------------
# 6. Sidebar Controls & Model Matrix
# ----------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ Neural Parameters")
    
    selected_reasoning_model = st.selectbox(
        "Computational Model",
        ["deepseek-r1:1.5b", "qwen2.5:3b", "qwen2.5-coder:1.5b"],
        index=0,
        help="Select local weight configuration optimized for STEM reasoning."
    )
    
    vision_backend_model = "moondream"
    
    temperature = st.slider("Determinism (Temperature)", 0.0, 1.0, 0.4, 0.05)
    
    st.markdown("---")
    if st.button("🧹 Clear Active Session"):
        st.session_state.chat_history = []
        st.rerun()

# ----------------------------------------------------
# 7. Hero View Rendering
# ----------------------------------------------------
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">⚡ HYPERCORE 4D AI</h1>
    <div class="hero-subtitle">High-Precision STEM Calculus · Computer Systems · Neural Vision · Multi-Modal Synthesis</div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 8. Render Existing Message Feed
# ----------------------------------------------------
for entry in st.session_state.chat_history:
    with st.chat_message(entry["role"]):
        if entry.get("attached_image"):
            st.image(entry["attached_image"], caption="Input Context Frame", width=340)
        if entry.get("is_synthesized_image"):
            st.image(entry["content"], caption="Generated Neural Output", use_container_width=True)
        else:
            st.markdown(entry["content"])

# ----------------------------------------------------
# 9. Multi-Modal Context Intake
# ----------------------------------------------------
with st.container():
    file_attachment = st.file_uploader(
        "Upload Diagram / Formula / Circuit Board (Optional)",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )

query_input = st.chat_input("Submit query, math problem, algorithm specification, or describe an image...")

# ----------------------------------------------------
# 10. Execution & Routing Engine
# ----------------------------------------------------
if query_input:
    # Append & render user message
    user_record = {"role": "user", "content": query_input}
    extracted_b64 = None

    if file_attachment is not None:
        extracted_b64 = serialize_image_to_base64(file_attachment)
        user_record["attached_image"] = file_attachment

    st.session_state.chat_history.append(user_record)

    with st.chat_message("user"):
        if file_attachment is not None:
            st.image(file_attachment, caption="Input Context Frame", width=340)
        st.markdown(query_input)

    # Route request to appropriate neural module
    with st.chat_message("assistant"):
        
        # ROUTE 1: Text-To-Image Generation
        if detect_visual_synthesis_intent(query_input):
            with st.spinner("Synthesizing neural render..."):
                sanitized_prompt = urllib.parse.quote(query_input)
                synthesis_endpoint = f"https://image.pollinations.ai/prompt/{sanitized_prompt}?width=1024&height=1024&nologo=true"
                st.image(synthesis_endpoint, caption=f"Prompt: {query_input}", use_container_width=True)
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": synthesis_endpoint,
                    "is_synthesized_image": True
                })

        # ROUTE 2: Vision Analysis & Multimodal Reasoning
        elif extracted_b64:
            with st.spinner("Processing visual input with Moondream Vision Engine..."):
                vision_payload = {
                    "model": vision_backend_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": query_input if query_input else "Analyze this diagram or problem step by step.",
                            "images": [extracted_b64]
                        }
                    ],
                    "stream": False
                }
                
                try:
                    res = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=vision_payload, timeout=120)
                    if res.status_code == 200:
                        analysis_output = res.json().get("message", {}).get("content", "No output generated.")
                        st.markdown(analysis_output)
                        st.session_state.chat_history.append({"role": "assistant", "content": analysis_output})
                    else:
                        st.error(f"Vision API Error: Status code {res.status_code}")
                except Exception as ex:
                    st.error(f"Failed to communicate with Vision Engine: {str(ex)}")

        # ROUTE 3: STEM Math, CS Code & General Analytical Stream
        else:
            # Send the system prompt alongside recent history to preserve RAM/latency
            system_prompt = {
                "role": "system",
                "content": "You are a senior STEM AI engineer. Provide rigorous, step-by-step mathematical reasoning, complete working code, and clear analytical solutions."
            }

            clean_history = [
                {"role": item["role"], "content": item["content"]}
                for item in st.session_state.chat_history[-3:]
                if not item.get("is_synthesized_image") and not item.get("attached_image")
            ]

            payload = {
                "model": selected_reasoning_model,
                "messages": [system_prompt] + clean_history,
                "keep_alive": "24h",
                "options": {
                    "num_thread": 4,
                    "num_ctx": 1024,
                    "temperature": temperature
                },
                "stream": True
            }

            try:
                response_stream = requests.post(
                    f"{OLLAMA_BASE_URL}/api/chat",
                    json=payload,
                    stream=True,
                    timeout=100
                )

                if response_stream.status_code == 200:
                    stream_container = st.empty()
                    aggregated_response = ""

                    for chunk in response_stream.iter_lines():
                        if chunk:
                            parsed_token = json.loads(chunk.decode("utf-8"))
                            text_piece = parsed_token.get("message", {}).get("content", "")
                            aggregated_response += text_piece
                            stream_container.markdown(aggregated_response + " █")

                    stream_container.markdown(aggregated_response)
                    st.session_state.chat_history.append({"role": "assistant", "content": aggregated_response})
                else:
                    st.error(f"Inference Server Error: Status Code {response_stream.status_code}")
            except Exception as ex:
                st.error(f"Network Stream Interrupted: {str(ex)}")
import streamlit as st
import time
import os
from dotenv import load_dotenv
from src.core.gemini_provider import GeminiProvider
from src.agent.agent import ReActLibraryAgent

# Nạp biến môi trường
load_dotenv()

# Cấu hình trang
st.set_page_config(page_title="Smart Library Agent", page_icon="📚", layout="wide")

# CSS tối giản, chuyên nghiệp — tương thích cả Light và Dark mode
st.markdown("""
<style>
    .title-gradient {
        background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2rem;
        margin-bottom: 0;
    }
    .latency-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        color: #00E676;
        margin-top: 8px;
        border: 1px solid #00E676;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title-gradient">📚 Smart Library: Agent vs Baseline</p>', unsafe_allow_html=True)
st.caption("So sánh chất lượng và tốc độ giữa ReAct Agent (có Tool) và LLM thuần (không Tool).")
st.divider()

# ── Khởi tạo Provider + Agent (cache để không re-init mỗi lần render) ──────────
@st.cache_resource
def load_agent():
    provider = GeminiProvider(model_name=os.getenv("DEFAULT_MODEL", "gemma-3-27b-it"))
    agent = ReActLibraryAgent(provider=provider, max_iter=5)
    return agent

try:
    agent = load_agent()
    provider_ok = True
except Exception as e:
    st.error(f"❌ Không thể khởi tạo kết nối Gemini: {e}")
    provider_ok = False
    st.stop()

# ── Session state ──────────────────────────────────────────────────────────────
if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = [
        {"role": "assistant", "content": "Xin chào! Tôi là trợ lý thư viện AI. Tôi có thể tra cứu sách, kiểm tra tình trạng mượn/trả và nhiều hơn nữa. Bạn cần hỗ trợ gì?"}
    ]
if "baseline_messages" not in st.session_state:
    st.session_state.baseline_messages = [
        {"role": "assistant", "content": "Xin chào! Tôi là LLM cơ bản, trả lời dựa trên kiến thức huấn luyện — không có khả năng tra cứu dữ liệu thư viện thực tế."}
    ]

# ── 2 TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🚀 Agent Framework (ReAct)", "🐢 Baseline (Direct LLM)"])


# ═══════════════════════════ TAB 1: AGENT ═════════════════════════════════════
with tab1:
    for msg in st.session_state.agent_messages:
        with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])
            if "latency" in msg:
                st.markdown(f'<div class="latency-badge">⏱️ {msg["latency"]:.2f}s</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Hỏi AI Agent (VD: Sách nào mượn nhiều nhất?)", key="agent_chat"):
        st.session_state.agent_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            start_time = time.time()
            with st.spinner(""):
                # Chạy toàn bộ vòng lặp ReAct — ẩn hoàn toàn, chỉ trả kết quả cuối
                try:
                    # Reset lịch sử để agent tươi mỗi lần hỏi mới
                    agent.chat_history = [agent.chat_history[0]]  # Giữ lại System Prompt
                    response = agent.run_agent(prompt)
                except Exception as e:
                    response = f"Lỗi hệ thống: {e}"

            end_time = time.time()
            latency = end_time - start_time

            st.markdown(response)
            st.markdown(f'<div class="latency-badge">⏱️ {latency:.2f}s</div>', unsafe_allow_html=True)

            st.session_state.agent_messages.append({
                "role": "assistant",
                "content": response,
                "latency": latency
            })


# ═══════════════════════════ TAB 2: BASELINE ══════════════════════════════════
with tab2:
    for msg in st.session_state.baseline_messages:
        with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "💬"):
            st.markdown(msg["content"])
            if "latency" in msg:
                st.markdown(f'<div class="latency-badge">⏱️ {msg["latency"]:.2f}s</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Hỏi LLM thông thường...", key="baseline_chat"):
        st.session_state.baseline_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="💬"):
            start_time = time.time()
            with st.spinner(""):
                try:
                    response = agent.run_baseline(prompt)
                except Exception as e:
                    response = f"Lỗi hệ thống: {e}"

            end_time = time.time()
            latency = end_time - start_time

            st.markdown(response)
            st.markdown(f'<div class="latency-badge">⏱️ {latency:.2f}s</div>', unsafe_allow_html=True)

            st.session_state.baseline_messages.append({
                "role": "assistant",
                "content": response,
                "latency": latency
            })

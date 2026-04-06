import streamlit as st
import os
from dotenv import load_dotenv

# Đã thay đổi Import sang OpenAI
from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActLibraryAgent
from src.telemetry.metrics import ComparisonDashboard

# Nạp biến môi trường
load_dotenv()

st.set_page_config(page_title="Smart Library Agent", page_icon="📚", layout="wide")

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

# Khởi tạo Dashboard lưu JSON
dashboard = ComparisonDashboard()

@st.cache_resource
def load_agent():
    # Sử dụng OpenAI Provider
    provider = OpenAIProvider(model_name=os.getenv("DEFAULT_MODEL", "gpt-4o-mini"))
    agent = ReActLibraryAgent(provider=provider, max_iter=5)
    return agent

try:
    agent = load_agent()
except Exception as e:
    st.error(f"❌ Không thể khởi tạo kết nối OpenAI: {e}")
    st.stop()

if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = [{"role": "assistant", "content": "Xin chào! Tôi có thể tra cứu sách và kiểm tra tình trạng mượn trả."}]
if "baseline_messages" not in st.session_state:
    st.session_state.baseline_messages = [{"role": "assistant", "content": "Xin chào! Tôi là LLM cơ bản, không có khả năng gọi tool."}]

tab1, tab2 = st.tabs(["🚀 Agent Framework (ReAct)", "🐢 Baseline (Direct LLM)"])

# ═══════════════════════════ TAB 1: AGENT ═════════════════════════════════════
with tab1:
    for msg in st.session_state.agent_messages:
        with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])
            if "latency" in msg:
                st.markdown(f'<div class="latency-badge">⏱️ {msg["latency"]}s | Thao tác: {msg.get("steps", 0)} bước</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Hỏi AI Agent...", key="agent_chat"):
        st.session_state.agent_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Đang suy luận và gọi Tool..."):
                agent.chat_history = [agent.chat_history[0]] 
                
                # Unpack tuple trả về từ run_agent
                response, metrics = agent.run_agent(prompt)
                
                # Lưu vào file JSON
                dashboard.add_metric(metrics)
                dashboard.save_to_file()

            st.markdown(response)
            st.markdown(f'<div class="latency-badge">⏱️ {metrics.latency}s | Thao tác: {metrics.total_steps} bước</div>', unsafe_allow_html=True)

            st.session_state.agent_messages.append({
                "role": "assistant",
                "content": response,
                "latency": metrics.latency,
                "steps": metrics.total_steps
            })

# ═══════════════════════════ TAB 2: BASELINE ══════════════════════════════════
with tab2:
    for msg in st.session_state.baseline_messages:
        with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "💬"):
            st.markdown(msg["content"])
            if "latency" in msg:
                st.markdown(f'<div class="latency-badge">⏱️ {msg["latency"]}s</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Hỏi LLM thông thường...", key="baseline_chat"):
        st.session_state.baseline_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="💬"):
            with st.spinner("Đang trả lời..."):
                # Unpack tuple trả về từ run_baseline
                response, metrics = agent.run_baseline(prompt)
                
                dashboard.add_metric(metrics)
                dashboard.save_to_file()

            st.markdown(response)
            st.markdown(f'<div class="latency-badge">⏱️ {metrics.latency}s</div>', unsafe_allow_html=True)

            st.session_state.baseline_messages.append({
                "role": "assistant",
                "content": response,
                "latency": metrics.latency
            })
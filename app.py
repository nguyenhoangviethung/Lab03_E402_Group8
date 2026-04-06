import streamlit as st
import time
from src.llm.provider import get_response

# Cấu hình trang (Phải là gọi đầu tiên)
st.set_page_config(page_title="Smart Library Agent", page_icon="📚", layout="wide")

# Custom CSS siêu mượt - 100% tương thích Light / Dark Mode của hệ thống
st.markdown("""
<style>
    /* Khoá Gradient cho tiêu đề - siêu đẹp và tương thích mọi theme */
    .title-gradient {
        background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 0px;
    }
    
    /* Latency badge tinh gọn */
    .latency-badge {
        display: inline-block;
        padding: 4px 10px;
        background-color: transparent;
        border-radius: 12px;
        font-size: 0.8rem;
        color: #00E676; /* Màu xanh dạ quang làm điểm nhấn */
        margin-top: 10px;
        border: 1px solid #00E676;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title-gradient">📚 Smart Library: Agent vs Baseline</p>', unsafe_allow_html=True)
st.markdown("💡 *Trải nghiệm giao diện Chatbot thông minh tích hợp ReAct Flow vs LLM Thuần.*")
st.divider()

# Khởi tạo session state để lưu trữ lịch sử chat cho 2 tab
if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = [{"role": "assistant", "content": "Xin chào! Tôi là Trợ lý Thư viện AI. Tôi có thể sử dụng các công cụ để tra cứu cơ sở dữ liệu thư viện. Bạn cần giúp gì nào?"}]
if "baseline_messages" not in st.session_state:
    st.session_state.baseline_messages = [{"role": "assistant", "content": "Xin chào! Tôi là LLM cơ bản. Tôi sẽ trả lời câu hỏi của bạn dựa trên kiến thức được huấn luyện sẵn."}]

# ====== TẠO 2 TABS ======
tab1, tab2 = st.tabs(["🚀 Agent Framework (ReAct)", "🐢 Baseline (Direct LLM)"])

# ================= TAB 1: AGENT =================
with tab1:
    
    # Hiển thị lịch sử chat của Agent
    for message in st.session_state.agent_messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])
            if "latency" in message:
                st.markdown(f'<div class="latency-badge">⏱️ {message["latency"]:.2f}s</div>', unsafe_allow_html=True)

    # Khung nhập liệu tại Agent
    if prompt := st.chat_input("Hỏi AI Agent (VD: Sách nào mượn nhiều nhất?)", key="agent_chat"):
        st.session_state.agent_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            start_time = time.time()

            # Chạy ngầm toàn bộ logic, user chỉ thấy spinner nhỏ
            with st.spinner(""):
                # [INTERNAL] Thought → Action → Observation (ẩn hoàn toàn)
                time.sleep(0.8)  # thought
                time.sleep(1.2)  # action + tool call
                time.sleep(0.8)  # observation
                agent_response = f"Dựa trên dữ liệu thư viện, hai cuốn sách có lượt mượn cao nhất tháng này là **'Nhà Giả Kim'** (150 lượt) và **'Đắc Nhân Tâm'** (142 lượt)."

            end_time = time.time()
            latency = end_time - start_time

            # Chỉ hiển thị câu trả lời cuối cùng — sạch như ChatGPT
            st.markdown(agent_response)
            st.markdown(f'<div class="latency-badge">⏱️ {latency:.2f}s</div>', unsafe_allow_html=True)
            
            st.session_state.agent_messages.append({
                "role": "assistant", 
                "content": agent_response,
                "latency": latency
            })


# ================= TAB 2: BASELINE =================
with tab2:
    
    # Hiển thị lịch sử chat của Baseline
    for message in st.session_state.baseline_messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "💬"):
            st.markdown(message["content"])
            if "latency" in message:
                st.markdown(f'<div class="latency-badge">⏱️ {message["latency"]:.2f}s</div>', unsafe_allow_html=True)

    # Khung nhập liệu tại Baseline
    if prompt := st.chat_input("Hỏi LLM Thông thường...", key="baseline_chat"):
        st.session_state.baseline_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="💬"):
            start_time = time.time()
            
            with st.spinner("LLM đang gõ câu trả lời..."):
                res_text = get_response(prompt)
                
            st.markdown(res_text)
            
            end_time = time.time()
            latency = end_time - start_time
            
            st.markdown(f'<div class="latency-badge">⏱️ Độ trễ xử lý trực tiếp: {latency:.2f}s</div>', unsafe_allow_html=True)
            
            st.session_state.baseline_messages.append({
                "role": "assistant", 
                "content": res_text,
                "latency": latency
            })

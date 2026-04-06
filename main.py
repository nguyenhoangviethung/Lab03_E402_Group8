import os
from dotenv import load_dotenv

load_dotenv()

from src.core.gemini_provider import GeminiProvider 
from src.agent.agent import ReActLibraryAgent

def run_baseline_chatbot(provider, query):
    """
    Chạy Chatbot Baseline: Chỉ dùng kiến thức nền (Weights của LLM), 
    không có Tool, không tra cứu Internet hay Database.
    """
    baseline_system_prompt = """Bạn là một nhân viên thư viện. 
Bạn hãy cố gắng trả lời câu hỏi của người dùng một cách tự nhiên.
Tuy nhiên, bạn KHÔNG ĐƯỢC dùng bất kỳ công cụ (tool) hay API nào, cũng không được truy cập Internet.
Hãy trả lời trực tiếp dựa trên kiến thức hiện có của bạn."""
    
    chat_history = [
        {"role": "system", "content": baseline_system_prompt},
        {"role": "user", "content": query}
    ]
    
    try:
        return provider.generate(chat_history)
    except Exception as e:
        return f"Lỗi Baseline: {str(e)}"

def main():
    print("So sánh")
    
    provider = GeminiProvider(model_name="gemma-3-27b-it") 
    
    user_query = "MLOps: Theory and Practice Vol. 8 còn bao nhiêu cuốn?"
    
    print(f"[Người dùng]: {user_query}")
    
    # ---------------------------------------------------------
    # 1. CHẠY LUỒNG BASELINE
    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("[PHẦN 1: BASELINE CHATBOT] (LLM Thuần túy - Không Tools)")
    print("="*60)
    print("Đang hỏi Gemma 3 trực tiếp...")
    baseline_response = run_baseline_chatbot(provider, user_query)
    print(f"[Kết quả Baseline]:\n{baseline_response}")
    
    # ---------------------------------------------------------
    # 2. CHẠY LUỒNG REACT AGENT
    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("[PHẦN 2: REACT AGENT] (Được trang bị 5 Tools thư viện)")
    print("="*60)
    print("Agent đang suy luận (kiểm tra terminal hoặc file log để xem các bước Thought/Action)...")
    
    agent = ReActLibraryAgent(provider=provider, max_iter=5)
    agent_response = agent.run(user_query)
    print(f"\n[Kết quả ReAct Agent]:\n{agent_response}")

if __name__ == "__main__":
    main()
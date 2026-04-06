from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActLibraryAgent
import os
from dotenv import load_dotenv

# Nạp biến môi trường từ file .env
load_dotenv()


# Lớp Adapter để chuyển đổi kết quả từ Dict (của OpenAIProvider) sang String (cho Agent)


class OpenAIAdapter(OpenAIProvider):
    def generate(self, chat_history):
        # OpenAIProvider gốc trả về Dict, chúng ta chỉ lấy phần 'content' là String
        response_dict = super().generate(
            prompt=chat_history[-1]['content'],
            system_prompt=chat_history[0]['content'] if chat_history[0]['role'] == 'system' else None
        )
        # Nếu Agent của bạn truyền vào full chat_history, dùng logic này:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=chat_history,
            temperature=0.1
        )
        return response.choices[0].message.content


def main():
    print("=== HỆ THỐNG QUẢN LÝ THƯ VIỆN (OPENAI VERSION) ===")

    # 1. Kiểm tra API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("LỖI: Bạn chưa cấu hình OPENAI_API_KEY trong file .env")
        return

    # 2. Khởi tạo Provider (dùng Adapter để không phải sửa file gốc)
    provider = OpenAIAdapter(model_name="gpt-4o", api_key=api_key)

    # 3. Khởi tạo Agent
    agent = ReActLibraryAgent(provider=provider, max_iter=5)

    # user_query = "Thư viện có bao nhiêu cuốn sách của Nguyễn Nhật Ánh vậy?"
    user_query = "Thư viện có bao nhiêu cuốn sách của Emma Le?"

    print(f"[Người dùng]: {user_query}")

    # ---------------------------------------------------------
    # PHẦN 1: RUN BASELINE (Gọi trực tiếp qua phương thức mới của Agent)
    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("[PHẦN 1: BASELINE CHATBOT] (Kiến thức thuần LLM)")
    print("="*60)

    # Gọi hàm run_baseline bạn vừa tách trong class ReActLibraryAgent
    baseline_response = agent.run_baseline(user_query)
    print(f"[Kết quả Baseline]:\n{baseline_response}")

    # ---------------------------------------------------------
    # PHẦN 2: RUN AGENT (Chạy vòng lặp ReAct)
    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("[PHẦN 2: REACT AGENT] (LLM + Công cụ thư viện)")
    print("="*60)
    print("Agent đang suy luận...")

    # Gọi hàm run_agent bạn vừa tách trong class ReActLibraryAgent
    agent_response = agent.run_agent(user_query)
    print(f"\n[Kết quả ReAct Agent]:\n{agent_response}")


if __name__ == "__main__":
    main()

import os
from openai import OpenAI
from src.telemetry.logger import system_logger

class OpenAIProvider:
    def __init__(self, model_name="gpt-4o-mini"):
        """
        Khởi tạo OpenAI Provider. 
        Yêu cầu có biến môi trường OPENAI_API_KEY trong file .env
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Không tìm thấy OPENAI_API_KEY. Hãy kiểm tra file .env!")
            
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def generate(self, chat_history):
        """
        Gửi lịch sử hội thoại lên OpenAI và nhận text trả về.
        """
        # Chuẩn hóa lại format: Đảm bảo content luôn là string
        formatted_messages = []
        for msg in chat_history:
            formatted_messages.append({
                "role": msg["role"],
                "content": str(msg["content"])  # Ép kiểu an toàn thành chuỗi
            })

        try:
            system_logger.debug(f"Đang gọi mô hình {self.model_name}...")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=formatted_messages,
                temperature=0.1 # Nhiệt độ thấp giúp Agent suy luận Logic hơn
            )
            return response.choices[0].message.content
            
        except Exception as e:
            system_logger.error(f"Lỗi khi gọi OpenAI API: {str(e)}", exc_info=True)
            raise e
import os
from google import genai
from google.genai import types
from src.telemetry.logger import system_logger


class GeminiProvider:
    def __init__(self, model_name="gemma-3-27b-it"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Không tìm thấy GEMINI_API_KEY trong biến môi trường.")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate(self, chat_history):
        """
        Nhận vào list các tin nhắn (chat_history) và trả về chuỗi text.
        Tương thích với interface mà ReActLibraryAgent yêu cầu.
        """
        system_instruction = ""
        contents = []

        # Tách System Prompt và build lịch sử hội thoại
        for msg in chat_history:
            if msg['role'] == 'system':
                system_instruction += msg['content'] + "\n\n"
            else:
                role = "model" if msg['role'] == "assistant" else "user"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg['content'])]
                    )
                )

        # Gemma không hỗ trợ system_instruction riêng biệt → nhúng vào đầu tin nhắn user đầu tiên
        if "gemma" in self.model_name.lower() and system_instruction:
            for content in contents:
                if content.role == "user":
                    original_text = content.parts[0].text
                    content.parts[0].text = f"Bạn phải tuân thủ các quy định sau:\n{system_instruction}\n---\nCâu hỏi của người dùng:\n{original_text}"
                    break
            config_sys_inst = None
        else:
            config_sys_inst = system_instruction.strip() if system_instruction else None

        config = types.GenerateContentConfig(
            system_instruction=config_sys_inst,
            temperature=0.1,
        )

        try:
            system_logger.debug(f"Đang gọi mô hình {self.model_name}...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            return response.text

        except Exception as e:
            system_logger.error(f"Lỗi khi gọi API: {str(e)}", exc_info=True)
            raise e

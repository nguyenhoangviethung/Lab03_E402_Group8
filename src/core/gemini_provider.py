import os
<<<<<<< HEAD
import time
import google.generativeai as genai
from typing import Dict, Any, Optional, Generator
from src.core.llm_provider import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str = "gemini-1.5-flash", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        
        # In Gemini, system instruction is passed during model initialization or as a prefix
        # For simplicity in this lab, we'll prepend it if provided
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

        response = self.model.generate_content(full_prompt)

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        # Gemini usage data is in response.usage_metadata
        content = response.text
        usage = {
            "prompt_tokens": response.usage_metadata.prompt_token_count,
            "completion_tokens": response.usage_metadata.candidates_token_count,
            "total_tokens": response.usage_metadata.total_token_count
        }

        return {
            "content": content,
            "usage": usage,
            "latency_ms": latency_ms,
            "provider": "google"
        }

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

        response = self.model.generate_content(full_prompt, stream=True)
        for chunk in response:
            yield chunk.text
=======
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
        system_instruction = ""
        contents = []
        
        # 1. Tách System Prompt và build lịch sử hội thoại
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
>>>>>>> base

import logging
import json
import os
import uuid
from datetime import datetime
import time

# ---------------- 1. CẤU HÌNH SYSTEM LOGGER ----------------
def setup_system_logger():
    os.makedirs('logs', exist_ok=True)
    
    logger = logging.getLogger("LibraryReActSystem")
    logger.setLevel(logging.DEBUG)
    
    # Format log text dễ đọc cho con người
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
    
    # Ghi ra file
    file_handler = logging.FileHandler('logs/system_app.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # In ra console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger

system_logger = setup_system_logger()

# ---------------- 2. CẤU HÌNH AGENT TRACER ----------------
class AgentTracer:
    """Class dùng để trackback toàn bộ quá trình suy luận của Agent cho 1 request"""
    def __init__(self, user_query):
        self.session_id = str(uuid.uuid4()) # Tạo ID duy nhất cho mỗi câu hỏi
        self.user_query = user_query
        self.start_time = time.time()
        self.steps = [] # Lưu danh sách các bước (Thought, Action, v.v.)
        self.status = "running" # running, success, failed
        self.final_answer = None
        
        # Tạo thư mục chứa file trace JSON
        os.makedirs('logs/traces', exist_ok=True)
        self.trace_file = f"logs/traces/trace_{self.session_id}.json"

    def add_step(self, iteration, prompt_tokens, llm_response, action_name, action_input, observation):
        """Lưu lại trạng thái của 1 vòng lặp (1 iteration)"""
        step_data = {
            "iteration": iteration,
            "timestamp": str(datetime.now()),
            "llm_raw_response": llm_response,
            "parsed_action": action_name,
            "parsed_input": action_input,
            "observation": observation,
            # "prompt_tokens": prompt_tokens # Nếu bạn muốn track cả chi phí
        }
        self.steps.append(step_data)

    def finish(self, final_answer=None, error=None):
        """Gọi khi Agent kết thúc request (trả lời xong hoặc bị lỗi)"""
        self.status = "error" if error else "success"
        self.final_answer = final_answer
        
        trace_data = {
            "session_id": self.session_id,
            "timestamp": str(datetime.now()),
            "duration_seconds": round(time.time() - self.start_time, 2),
            "user_query": self.user_query,
            "status": self.status,
            "error_msg": str(error) if error else None,
            "final_answer": self.final_answer,
            "total_iterations": len(self.steps),
            "trace_steps": self.steps
        }
        
        # Dump toàn bộ trackback ra file JSON
        with open(self.trace_file, 'w', encoding='utf-8') as f:
            json.dump(trace_data, f, ensure_ascii=False, indent=4)
        
        system_logger.info(f"Đã lưu trace cho session {self.session_id} tại {self.trace_file}")
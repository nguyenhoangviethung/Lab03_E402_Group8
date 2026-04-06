import logging
import json
import os
import uuid
from datetime import datetime
import time
import functools  

# ---------------- 1. CẤU HÌNH SYSTEM LOGGER ----------------
def setup_system_logger():
    os.makedirs('logs', exist_ok=True)
    
    logger = logging.getLogger("LibraryReActSystem")
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
    
    file_handler = logging.FileHandler('logs/system_app.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger

system_logger = setup_system_logger()

class AgentTracer:
    """Class dùng để trackback toàn bộ quá trình suy luận của Agent cho 1 request"""
    def __init__(self, user_query):
        self.session_id = str(uuid.uuid4())
        self.user_query = user_query
        self.start_time = time.time()
        self.steps = [] 
        self.status = "running" 
        self.final_answer = None
        
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
        
        with open(self.trace_file, 'w', encoding='utf-8') as f:
            json.dump(trace_data, f, ensure_ascii=False, indent=4)
        
        system_logger.info(f"Đã lưu trace cho session {self.session_id} tại {self.trace_file}")

def log_function_call(func):
    """
    Decorator tự động ghi log thông tin mỗi khi một function (Tool) được gọi.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func_name = func.__name__
        
        system_logger.info(f"[TOOL START] Bắt đầu gọi '{func_name}' | Args: {args} | Kwargs: {kwargs}")
        
        try:
            result = func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            system_logger.info(f"[TOOL SUCCESS] '{func_name}' hoàn thành trong {execution_time:.4f}s | Result: {result}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            system_logger.error(f"[TOOL ERROR] '{func_name}' thất bại sau {execution_time:.4f}s | Lỗi: {str(e)}", exc_info=True)
            raise e 
            
    return wrapper
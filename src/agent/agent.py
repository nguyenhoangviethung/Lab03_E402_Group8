import json
import re
import time
from src.telemetry.logger import system_logger, AgentTracer, log_function_call
from src.telemetry.metrics import ExecutionMetrics
from src.tools.tools import TOOLS

SYSTEM_PROMPT = """
Bạn là một ReAct Agent quản lý thư viện thông minh. Chức năng của bạn là tư vấn, tra cứu thông tin sách và người dùng.
Bạn có quyền truy cập vào các công cụ (tools) sau:

1. Get_Popular_Books(): Không cần tham số. Trả về danh sách sách phổ biến.
2. Search_Book_Status(title: str): Kiểm tra trạng thái và số lượng tồn kho của sách.
3. Get_User_Ledger(user_id: str): Kiểm tra lịch sử mượn trả và tiền phạt của người dùng.
4. Get_Book_Content(title: str): Lấy tóm tắt nội dung của một cuốn sách.
5. Filter_By_Author(author: str): Tìm các cuốn sách của một tác giả cụ thể.

ĐỊNH DẠNG BẮT BUỘC KHI PHẢN HỒI (Luôn dùng tiếng Việt):
Thought: Suy nghĩ của bạn về việc cần làm tiếp theo dựa trên thông tin hiện có.
Action: Tên công cụ cần gọi (chỉ một trong các tên ở trên, hoặc để trống nếu không cần).
Action Input: Tham số truyền vào công cụ dưới dạng JSON hợp lệ. Ví dụ: {"title": "Sapiens"}

Khi bạn đã có đủ thông tin để trả lời câu hỏi của người dùng, hãy dùng định dạng sau để kết thúc:
Thought: Tôi đã có đủ thông tin để trả lời.
Final Answer: [Câu trả lời hoàn chỉnh và thân thiện dành cho người dùng]
"""

class ReActLibraryAgent:
    def __init__(self, provider, max_iter=5):
        self.provider = provider
        self.max_iter = max_iter
        self.chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]

    @log_function_call
    def parse_llm_output(self, text):
        prompt = f"""
        Bạn là một công cụ phân tích dữ liệu. Trích xuất "Action" và "Action Input" thành chuỗi JSON.
        {{
            "action_name": "Tên_Action_Hoặc_null",
            "action_input": {{}}
        }}
        Văn bản: {text}
        """
        try:
            parsed_response = self.provider.generate([{"role": "system", "content": prompt}])
            clean_response = re.sub(r"^```json|```$", "", parsed_response.strip(), flags=re.MULTILINE).strip()
            parsed_data = json.loads(clean_response)
            
            action_name = parsed_data.get("action_name")
            if action_name == "null": action_name = None
            action_input = parsed_data.get("action_input", {})
            return action_name, action_input

        except Exception as e:
            system_logger.warning(f"Lỗi parse LLM: {str(e)}. Fallback dùng RegEx.")
            action_match = re.search(r"Action:\s*([^\n]+)", text)
            action_input_match = re.search(r"Action Input:\s*(.*)", text, re.DOTALL)

            action_name = action_match.group(1).strip() if action_match else None
            action_input_str = action_input_match.group(1).strip() if action_input_match else "{}"
            action_input_str = re.sub(r"^```json|```$", "", action_input_str, flags=re.MULTILINE).strip()

            try:
                action_input = json.loads(action_input_str)
            except:
                action_input = None
            return action_name, action_input

    @log_function_call
    def execute_tool(self, action_name, action_input):
        if not action_name or str(action_name).lower() == "none":
            return json.dumps({"error": "Không tìm thấy Action hợp lệ."})
        if action_input is None:
            return json.dumps({"error": "Action Input không phải JSON hợp lệ."})
        if action_name not in TOOLS:
            return json.dumps({"error": f"Tool '{action_name}' không tồn tại."})

        try:
            return TOOLS[action_name](action_input)
        except Exception as e:
            return json.dumps({"error": f"Lỗi nội bộ tool: {str(e)}"})

    @log_function_call
    def run_baseline(self, user_query):
        metrics = ExecutionMetrics(method_name="Baseline", query=user_query)
        baseline_history = [
            {"role": "system", "content": "Bạn là nhân viên thư viện. Hãy trả lời dựa trên kiến thức tĩnh. KHÔNG DÙNG TOOL."},
            {"role": "user", "content": user_query}
        ]

        try:
            response = self.provider.generate(baseline_history)
            metrics.status = "success"
        except Exception as e:
            response = "Xin lỗi, tôi không thể xử lý yêu cầu lúc này."
            metrics.status = "error"
        
        metrics.end_time = time.time()
        # Ước tính token cơ bản (nếu provider chưa trả về usage)
        metrics.total_tokens_input = len(str(baseline_history)) // 4
        metrics.total_tokens_output = len(response) // 4
        
        return response, metrics

    @log_function_call
    def run_agent(self, user_query):
        metrics = ExecutionMetrics(method_name="ReAct Agent", query=user_query)
        tracer = AgentTracer(user_query)
        self.chat_history.append({"role": "user", "content": user_query})

        try:
            for step in range(1, self.max_iter + 1):
                metrics.total_steps = step
                
                llm_response = self.provider.generate(self.chat_history)
                self.chat_history.append({"role": "assistant", "content": llm_response})
                
                # Ước lượng token tích lũy
                metrics.total_tokens_input += len(str(self.chat_history)) // 4
                metrics.total_tokens_output += len(llm_response) // 4

                if "Final Answer:" in llm_response:
                    final_answer = llm_response.split("Final Answer:")[-1].strip()
                    metrics.end_time = time.time()
                    tracer.finish(final_answer=final_answer)
                    return final_answer, metrics

                action_name, action_input = self.parse_llm_output(llm_response)
                if action_name:
                    metrics.tool_calls.append(action_name)

                observation = self.execute_tool(action_name, action_input)
                tracer.add_step(step, 0, llm_response, action_name, action_input, observation)
                self.chat_history.append({"role": "user", "content": f"Observation: {observation}"})

            metrics.end_time = time.time()
            metrics.status = "max_iter_reached"
            tracer.finish(error="Vượt quá MAX_ITER.")
            return "Vượt quá giới hạn suy luận.", metrics

        except Exception as e:
            metrics.end_time = time.time()
            metrics.status = "error"
            tracer.finish(error=str(e))
            return "Đã xảy ra lỗi hệ thống nghiêm trọng.", metrics

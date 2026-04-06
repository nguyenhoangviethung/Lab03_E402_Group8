import json
import re
from src.telemetry.logger import system_logger, AgentTracer, log_function_call
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
        """
        Khởi tạo ReAct Agent.
        :param provider: LLM Provider instance (có hàm generate(messages))
        :param max_iter: Số vòng lặp tối đa để tránh infinite loop
        """
        self.provider = provider
        self.max_iter = max_iter
        # Khởi tạo ngữ cảnh với System Prompt
        self.chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]

    @log_function_call
    def parse_llm_output(self, text):
        """
        Trích xuất tên Tool và tham số JSON từ câu trả lời của LLM thông qua LLM provider (OpenAI).
        """
        prompt = f"""
        Bạn là một công cụ phân tích dữ liệu chuyên nghiệp.
        Nhiệm vụ của bạn là trích xuất "Action" và "Action Input" từ đoạn văn bản dưới đây.
        Đầu ra PHẢI LÀ MỘT CHUỖI JSON ĐÚNG CHUẨN (không bọc trong markdown hay backticks), với cấu trúc chính xác như sau:
        {{
            "action_name": "Tên_Action_Hoặc_null",
            "action_input": {{
                // các tham số truyền vào tương ứng
            }}
        }}

        Lưu ý các tham số action_input thường xoay quanh các danh sách sau (dựa trên DB schema):
        - book_title, author, category, isbn, description_short, total_copies, available_copies, created_at
        - borrowing_id, student_id, book_id, borrowed_at, due_date, return_date, status
        - student_name

        Đoạn văn bản cần phân tích:
        {text}
        """
        # Xin lưu ý: Gọi thêm bước parse bằng LLM có thể làm tăng thời gian phản hồi (latency).
        try:
            # Sử dụng provider để sinh ra kết quả parse
            messages = [{"role": "system", "content": prompt}]
            parsed_response = self.provider.generate(messages)

            # Xóa các backticks markdown (ví dụ: ```json ... ```) nếu LLM sinh ra
            clean_response = re.sub(
                r"^```json|```$", "", parsed_response.strip(), flags=re.MULTILINE).strip()

            parsed_data = json.loads(clean_response)
            action_name = parsed_data.get("action_name")
            # Gán null thành None nếu LLM trả về json null
            if action_name == "null":
                action_name = None

            action_input = parsed_data.get("action_input", {})
            return action_name, action_input

        except Exception as e:
            system_logger.warning(
                f"Lỗi khi dùng OpenAI parse output: {str(e)}. Sử dụng RegEx mặc định.")

            # Đoạn Regex dự phòng nếu LLM parse lỗi
            action_match = re.search(r"Action:\s*([^\n]+)", text)
            action_input_match = re.search(
                r"Action Input:\s*(.*)", text, re.DOTALL)

            action_name = action_match.group(
                1).strip() if action_match else None
            action_input_str = "{}"
            if action_input_match:
                raw_input = action_input_match.group(1).strip()
                raw_input = re.sub(r"^```json|```$", "",
                                   raw_input, flags=re.MULTILINE).strip()
                action_input_str = raw_input if raw_input else "{}"

            try:
                action_input = json.loads(action_input_str)
            except json.JSONDecodeError as err:
                system_logger.warning(
                    f"Lỗi Parse JSON từ RegEx dự phòng: {action_input_str}. Chi tiết: {str(err)}")
                action_input = None

            return action_name, action_input
    @log_function_call
    def execute_tool(self, action_name, action_input):
        """
        Thực thi Tool một cách an toàn và trả về Observation.
        """
        if not action_name or action_name.lower() == "none":
            return json.dumps({"error": "Không tìm thấy Action hợp lệ. Hãy kiểm tra lại format hoặc dùng 'Final Answer'."})

        if action_input is None:
            return json.dumps({
                "error": "Action Input không phải là chuỗi JSON hợp lệ. Hãy sửa lại cú pháp (đảm bảo dùng ngoặc kép cho key/value).",
                "instruction": "Hãy thử gọi lại Tool với JSON chuẩn."
            })

        if action_name not in TOOLS:
            return json.dumps({"error": f"Tool '{action_name}' không tồn tại. Chỉ sử dụng các tool được liệt kê trong System Prompt."})

        try:
            # Gọi hàm tool tương ứng
            system_logger.debug(
                f"Đang thực thi Tool: {action_name} với input: {action_input}")
            result = TOOLS[action_name](action_input)
            return result
        except Exception as e:
            system_logger.error(
                f"Lỗi khi chạy Tool {action_name}: {str(e)}", exc_info=True)
            return json.dumps({"error": f"Lỗi nội bộ khi chạy tool: {str(e)}"})
    @log_function_call
    def run_baseline(self, user_query):
        """
        Chạy luồng Baseline: Gọi model trực tiếp và trả về kết quả ngay lập tức.
        """
        system_logger.info(f"Nhận request Baseline: '{user_query}'")

        # Tạo ngữ cảnh riêng biệt cho Baseline (không ảnh hưởng đến chat_history của Agent)
        baseline_history = [
            {"role": "system", "content": "Bạn là một nhân viên thư viện hữu ích. Hãy trả lời trực tiếp dựa trên kiến thức của bạn."},
            {"role": "user", "content": user_query}
        ]

        try:
            # Gọi Provider để sinh nội dung (giả định provider trả về string)
            response = self.provider.generate(baseline_history)
            return response
        except Exception as e:
            system_logger.error(f"Lỗi Baseline: {str(e)}")
            return "Xin lỗi, tôi không thể xử lý yêu cầu lúc này."
    @log_function_call
    def run_agent(self, user_query):
        """
        Hàm chính chạy vòng lặp ReAct xử lý câu hỏi của user có sử dụng Tools.
        """
        system_logger.info(f"Nhận request Agent: '{user_query}'")

        # Khởi tạo Tracer để ghi log trackback cho request này
        tracer = AgentTracer(user_query)
        self.chat_history.append({"role": "user", "content": user_query})

        try:
            for step in range(1, self.max_iter + 1):
                system_logger.debug(
                    f"--- Bắt đầu vòng lặp thứ {step}/{self.max_iter} ---")

                # 1. Gọi LLM Provider để sinh bước tiếp theo
                llm_response = self.provider.generate(self.chat_history)
                self.chat_history.append(
                    {"role": "assistant", "content": llm_response})

                # 2. Kiểm tra điều kiện thoát (Đã có Final Answer)
                if "Final Answer:" in llm_response:
                    final_answer = llm_response.split(
                        "Final Answer:")[-1].strip()
                    system_logger.info("Đã tìm thấy câu trả lời cuối cùng.")
                    tracer.finish(final_answer=final_answer)
                    return final_answer

                # 3. Phân tích Action từ output của LLM
                action_name, action_input = self.parse_llm_output(llm_response)

                # 4. Thực thi Tool và nhận Observation
                observation = self.execute_tool(action_name, action_input)

                # 5. Ghi trackback vào JSON
                tracer.add_step(
                    iteration=step,
                    prompt_tokens=0,
                    llm_response=llm_response,
                    action_name=action_name,
                    action_input=action_input,
                    observation=observation
                )

                # 6. Cập nhật Observation vào ngữ cảnh
                obs_msg = f"Observation: {observation}"
                self.chat_history.append({"role": "user", "content": obs_msg})

            # Xử lý khi vượt quá số vòng lặp
            tracer.finish(error="Vượt quá MAX_ITER.")
            return "Hệ thống không thể xử lý yêu cầu phức tạp này (Vượt quá giới hạn suy luận)."

        except Exception as e:
            system_logger.error(f"Lỗi nghiêm trọng: {str(e)}", exc_info=True)
            tracer.finish(error=str(e))
            return "Đã xảy ra lỗi hệ thống nghiêm trọng."
    
    def run(self, user_query):
        """
        Hàm chính chạy vòng lặp ReAct xử lý câu hỏi của user.
        """
        system_logger.info(f"Nhận request mới: '{user_query}'")

        # Khởi tạo Tracer để ghi log trackback cho request này
        tracer = AgentTracer(user_query)
        self.chat_history.append({"role": "user", "content": user_query})

        try:
            for step in range(1, self.max_iter + 1):
                system_logger.debug(
                    f"--- Bắt đầu vòng lặp thứ {step}/{self.max_iter} ---")

                # 1. Gọi LLM Provider để sinh bước tiếp theo
                llm_response = self.provider.generate(self.chat_history)
                self.chat_history.append(
                    {"role": "assistant", "content": llm_response})

                # 2. Kiểm tra điều kiện thoát (Đã có Final Answer)
                if "Final Answer:" in llm_response:
                    final_answer = llm_response.split(
                        "Final Answer:")[-1].strip()
                    system_logger.info("Đã tìm thấy câu trả lời cuối cùng.")
                    tracer.finish(final_answer=final_answer)
                    return final_answer

                # 3. Phân tích Action từ output của LLM
                action_name, action_input = self.parse_llm_output(llm_response)

                # 4. Thực thi Tool và nhận Observation
                observation = self.execute_tool(action_name, action_input)

                # 5. Ghi trackback cho vòng lặp hiện tại vào JSON
                tracer.add_step(
                    iteration=step,
                    prompt_tokens=0,  # Cập nhật nếu provider của bạn hỗ trợ trả về token usage
                    llm_response=llm_response,
                    action_name=action_name,
                    action_input=action_input,
                    observation=observation
                )

                # 6. Cập nhật Observation vào ngữ cảnh để LLM đọc ở vòng lặp sau
                obs_msg = f"Observation: {observation}"
                self.chat_history.append({"role": "user", "content": obs_msg})
                system_logger.debug(f"Observation thu được: {observation}")

            # Nếu chạy hết vòng lặp for mà không có Final Answer -> Fallback
            warning_msg = "Agent vượt quá số vòng lặp tối đa (MAX_ITER)."
            system_logger.warning(warning_msg)
            tracer.finish(
                error="Vượt quá MAX_ITER. Agent có thể đã bị kẹt trong vòng lặp vô hạn.")
            return "Hệ thống bận hoặc không thể xử lý yêu cầu phức tạp này, vui lòng thử lại sau. (Lỗi: Vượt quá giới hạn suy luận)"

        except Exception as e:
            # Bắt lỗi toàn cục (Code sập, mất kết nối API, v.v.)
            error_msg = f"Lỗi nghiêm trọng trong quá trình chạy Agent: {str(e)}"
            system_logger.error(error_msg, exc_info=True)
            tracer.finish(error=str(e))
            return "Đã xảy ra lỗi hệ thống nghiêm trọng. Vui lòng liên hệ quản trị viên."

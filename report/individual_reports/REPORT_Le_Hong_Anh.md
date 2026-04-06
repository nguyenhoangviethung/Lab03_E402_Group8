# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Lê Hồng Anh
- **Student ID**: 2A202600096
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

Với vai trò phụ trách logic Agent và tích hợp LLM, tôi đã hoàn thiện khung điều hướng (Orchestration) để chuyển đổi từ một Chatbot truyền thống sang một ReAct Agent có khả năng sử dụng công cụ.

- **Modules Implemented**: 
    * **`src/agent/agent.py`**: Phát triển lớp `ReActLibraryAgent` với vòng lặp ReAct hoàn chỉnh, tách biệt phương thức `run_baseline` (kiến thức tĩnh) và `run_agent` (suy luận động).
    * **`main.py`**: Thiết lập luồng thực thi so sánh song song hai cơ chế để đánh giá hiệu quả thực tế giữa tri thức thuần của LLM và công cụ hỗ trợ.
    * **`OpenAIAdapter`**: Triển khai mẫu thiết kế Adapter để chuẩn hóa đầu ra từ `OpenAIProvider` (trả về Dictionary) sang định dạng chuỗi (String) mà Agent yêu cầu để xử lý logic tiếp theo.

- **Documentation**: Tích hợp thành công cơ chế **Double-Pass Parsing** (Dùng LLM tự kiểm tra format sau khi sinh Thought) giúp giảm thiểu lỗi cú pháp khi gọi Tool, đảm bảo tính ổn định cho hệ thống.

---

## II. Debugging Case Study (10 Points)

*Phân tích lỗi trích xuất dữ liệu trong vòng lặp ReAct.*

- **Problem Description**: Trong quá trình chạy `run_agent`, LLM thường xuyên trả về nội dung bao gồm cả các ký tự markdown (ví dụ: \` \` \`json ... \` \` \`) khiến hàm `json.loads()` bị lỗi, dẫn đến Agent không thể thực thi công cụ.
- **Log Source**: Hệ thống ghi nhận cảnh báo: `system_logger.warning(f"Lỗi parse LLM: {str(e)}. Fallback dùng RegEx.")`.
- **Diagnosis**: LLM có xu hướng tự động định dạng mã nguồn để dễ đọc, nhưng hàm parse ban đầu chưa làm sạch các ký tự bao bọc này trước khi giải mã JSON.
- **Solution**: Sử dụng Regex để loại bỏ các block markdown (`re.sub(r"^```json|```$", "", ...)`), đảm bảo dữ liệu đầu vào cho bộ giải mã luôn là chuỗi JSON thuần túy.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

Qua việc cài đặt và thực nghiệm hai phương thức, tôi rút ra các quan sát sau:

1.  **Reasoning (Khả năng suy luận)**: `run_baseline` trả lời dựa trên xác suất ngôn ngữ và kiến thức tĩnh, dễ dẫn đến hiện tượng ảo giác (hallucination). Ngược lại, `run_agent` thực hiện bước `Thought` để nhận ra sự thiếu hụt thông tin và chủ động gọi công cụ tra cứu.
2.  **Reliability (Độ tin cậy)**: Agent có độ chính xác cao hơn nhờ vào bước **Observation**. Dữ liệu thực tế từ Tool đóng vai trò là cơ sở dữ liệu xác thực (Grounding), ngăn chặn việc LLM tự bịa ra thông tin không có thật.
3.  **Efficiency**: ReAct Agent tiêu tốn nhiều tài nguyên (token) và thời gian phản hồi hơn do phải trải qua nhiều bước suy luận và gọi công cụ, nhưng mang lại kết quả chính xác tuyệt đối cho các tác vụ nghiệp vụ thư viện.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Áp dụng cơ chế **Tool Filtering** để chỉ đưa vào Prompt những công cụ thực sự cần thiết dựa trên câu hỏi của người dùng, giúp tiết kiệm context window.
- **Safety**: Cài đặt tầng kiểm duyệt (Guardrails) để kiểm tra các tham số đầu vào của công cụ (Action Input), tránh các lỗi logic hệ thống hoặc truy cập dữ liệu trái phép.
- **Performance**: Triển khai cơ chế lưu bộ nhớ đệm (Caching) cho các kết quả trả về từ công cụ để tối ưu hóa tốc độ phản hồi cho các câu hỏi trùng lặp.

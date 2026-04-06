# Individual Report: Lab 3 - Chatbot vs ReAct Agent: Library management

- **Student Name**: Nguyễn Hoàng Việt Hùng
- **Student ID**: 2A202600164
- **Date**: 2026-04-06


## I. Technical Contribution (15 Points)

Là thành viên phụ trách **System Prompt & Telemetry**, tôi đã thiết kế hành vi cho Agent và xây dựng hệ thống đo lường tự động.

- **Modules Implemented**: 
  - `src/agent/agent.py`: Thiết kế ReAct Prompt và hàm parse JSON an toàn.
  - `src/telemetry/logger.py`: Xây dựng `AgentTracer` ghi log JSON và Decorator `@log_function_call`.
  - `src/telemetry/metrics.py` & `benchmark.py`: Tự động hóa chạy 12 test cases và xuất báo cáo so sánh Token/Latency.

- **Code Highlights**:
  Sử dụng Decorator để ghi log Tool minh bạch, không làm thay đổi logic lõi:
  ```python
  def log_function_call(func):
      @functools.wraps(func)
      def wrapper(*args, **kwargs):
          try:
              result = func(*args, **kwargs)
              system_logger.info(f"[SUCCESS] {func.__name__} | Result: {result}")
              return result
          except Exception as e:
              system_logger.error(f"[ERROR] {func.__name__} | Lỗi: {str(e)}")
              raise e # Ném lỗi để Agent tự Self-Correction
      return wrapper
  ```

Dưới đây là phiên bản được tinh chỉnh thật súc tích, đi thẳng vào vấn đề theo góc nhìn của người làm Logging & Metrics:

## II. Debugging Case Study (10 Points)

*Phân tích sự cố qua góc độ Telemetry (Giám sát hệ thống).*

- **Problem**: Khởi chạy Agent bằng **GPT-4o-mini** thất bại, ứng dụng crash.
- **Log Source**: `BadRequestError: 400 - Missing required parameter: 'messages[0].content[0].type'`
- **Diagnosis**: Truy xuất payload từ hệ thống log cho thấy API OpenAI từ chối request do trường `content` bị truyền dưới dạng object thay vì chuỗi thuần (string).
- **Solution**: Ép kiểu `str()` cho dữ liệu tại `OpenAIProvider`. Đồng thời bổ sung `try-catch` để hệ thống an toàn ghi status "error" vào file `benchmark.json` thay vì làm sập toàn bộ ứng dụng Streamlit.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Đánh giá năng lực dựa trên dữ liệu định lượng từ Metrics và Trace Logs.*

1. **Reasoning (Tính minh bạch)**: Nhờ class `AgentTracer` ghi lại JSON từng bước, ReAct không còn là một "hộp đen". Log hiển thị rõ quá trình Agent chia nhỏ vấn đề, gọi Tool và đánh giá lại kết quả.
2. **Reliability vs Cost (Đánh đổi chi phí)**: Bảng `ComparisonDashboard` chỉ ra sự thật: Để chính xác 100%, ReAct tốn trung bình **~900 tokens và 4-6s** mỗi câu hỏi. Mức này đắt và chậm gấp **10 lần** so với Baseline (~100 tokens, 1-2s). 
3. **Observation (Khả năng tự sửa lỗi)**: Trace log chứng minh Agent biết "thử sai". Khi Tool báo lỗi, log ghi nhận Agent chủ động đổi Tool khác để thử lại. Nếu không có hệ thống Telemetry, ta sẽ nhầm tưởng hệ thống bị treo (hang).

---

## IV. Các cải tiến trong tương lai (5 Điểm)

*Hướng mở rộng hệ thống Telemetry cho môi trường Production:*

1. **Khả năng mở rộng (Scalability)**: *Distributed Tracing*. Tích hợp các nền tảng giám sát LLMOps (LangSmith, Datadog) thay vì lưu file JSON cục bộ, giúp theo dõi thời gian thực hàng ngàn session cùng lúc.
2. **Bảo mật (Safety)**: *Metric-based Guardrails*. Dựa vào hệ thống Metrics để tự động ngắt kết nối (kill session) nếu phát hiện `total_tokens` hoặc `total_steps` tăng vọt bất thường, ngăn chặn rủi ro cạn kiệt tài chính (Denial of Wallet).
3. **Hiệu năng (Performance)**: *Log Compression & Context Pruning*. Tự động nén các file trace cũ và tóm tắt (summarize) bớt các `Observation` dài dòng trước khi ghi log/nạp lại ngữ cảnh để tối ưu dung lượng lưu trữ và chi phí token.
# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Thị Hương Giang
- **Student ID**: 2A202600485
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

Là thành viên viết tool, tôi đã implement các tool cho agent như search_book_status, get_book_content, và filter_by_author. Đã commit ở nhánh riêng 'nthg'

- **Modules Implementated**: `src/tools/tools.py` (các tool mới).
  + ở branches 'nthg': `src/tools/book_tools.py`
- **Key Tools Developed**:
  - `search_book_status` (TC2): Kiểm tra tình trạng mượn/trả sách từ file flat database.
  - `get_book_content` (TC4): Trích xuất tóm tắt nội dung sách (`description_short`).
  - `filter_by_author` (TC5): Thống kê và liệt kê danh mục sách theo tác giả.
- **Code Highlights**:
  1. **Data Sanitization**: Xây dựng hàm `parse_input` để tự động bóc tách giá trị text nếu Agent truyền tham số dưới dạng Dictionary.

    ```python
  def parse_input(input_data):
      """Bóc tách dữ liệu nếu Agent truyền vào dạng dict thay vì chuỗi string thuần túy"""
      if isinstance(input_data, dict):
          return str(next(iter(input_data.values())))
      return str(input_data)
  ```
  2. **Telemetry Integration**: Sử dụng decorator `@log_function_call` (được áp dụng trên hàm `filter_by_author`) để tự động ghi log giám sát luồng gọi tool của Agent.
  3. **Fuzzy Search**: Sử dụng Pandas `str.contains(case=False)` để đảm bảo tính linh hoạt khi tìm kiếm chuỗi.
- **Error Handling**: Áp dụng tư duy Defensive Programming, bọc toàn bộ logic trong `try...except`, xử lý triệt để các ngoại lệ cụ thể như `FileNotFoundError` và định dạng trả về là Text báo lỗi (Observation) thay vì làm crash hệ thống.

- **Documentation**: Các tool được thiết kế bọc trong khối try...except, đảm bảo trả về text báo lỗi (Observation) thay vì làm văng (crash) chương trình khi gặp ngoại lệ.Đã viết tool với error handling, tích hợp vào ReAct loop.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Khi chạy kiểm thử luồng Agent sử dụng Tool, hệ thống gặp lỗi gián đoạn với thông báo văng ra từ Python: `unhashable type: 'dict'`.
- **Log Source**: Trích xuất từ Telemetry trace của hệ thống:
  `[agent.py] - Đang thực thi Tool: search_book_status với input: {'title': 'MLOps: Theory and Practice'}`
- **Diagnosis**: LLM (Gemma-3) có xu hướng sinh ra `Action_Input` dưới dạng cấu trúc JSON/Dictionary thay vì chuỗi văn bản thuần túy (String). Khi cấu trúc Dict này được truyền trực tiếp vào hàm `.str.contains()` của thư viện Pandas, trình thông dịch Python báo lỗi vì không thể băm (hash) kiểu dữ liệu này để so sánh.
- **Solution**: Tôi đã code thêm một hàm tiền xử lý `parse_input(input_data)` đứng trước mọi logic nghiệp vụ của các Tools:
  ```python
  if isinstance(input_data, dict):
      return str(next(iter(input_data.values())))

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

- **Reasoning**: Khối `Thought` giúp Agent vượt trội hoàn toàn so với Chatbot thông thường bằng cách tạo ra một "khoảng nghỉ" để phân tích logic. Thay vì ngay lập tức bịa ra câu trả lời (Hallucination) như Baseline Chatbot khi được hỏi "Cuốn MLOps còn trên kệ không?", Agent dùng `Thought` để nhận thức rằng nó thiếu thông tin thực tế, từ đó quyết định gọi tool `search_book_status` trước khi đưa ra kết luận cuối cùng.
- **Reliability**: Mặc dù chính xác hơn về mặt dữ liệu, Agent lại hoạt động **tệ hơn** Chatbot ở hai trường hợp: (1) **Độ trễ (Latency):** Phải mất nhiều thời gian hơn (đôi khi gấp 3-4 lần) để chạy qua vòng lặp Thought-Action-Observation. (2) **Câu hỏi kiến thức chung:** Với các prompt không cần tra cứu (VD: "Viết email xin gia hạn sách"), Agent đôi khi phản ứng cồng kềnh, phân tích quá mức hoặc cố gắng tìm tool rác thay vì trả lời mượt mà và trực tiếp như Baseline Zero-shot.
- **Observation**: Phản hồi từ môi trường (Observation) đóng vai trò định hướng trực tiếp cho bước tiếp theo của LLM. Trong quá trình implement, tôi đã cố tình trả về các chuỗi báo lỗi bằng tiếng Việt (VD: *"Không tìm thấy thông tin về cuốn sách..."*). Khi đọc được Observation này, Agent không bị đứng hình mà ngay lập tức sinh ra một `Thought` mới để xin lỗi người dùng hoặc gợi ý sách khác (Self-correction), chứng minh vòng lặp ReAct cực kỳ linh hoạt và chịu lỗi tốt.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Thay vì sử dụng thư viện Pandas đọc file CSV một cách đồng bộ (Synchronous) mỗi lần gọi Tool, hệ thống cần được tái cấu trúc để sử dụng I/O bất đồng bộ (Async/Await với `asyncio`). Có thể kết hợp thêm Message Queue (như RabbitMQ/Kafka) để điều phối hàng đợi khi có hàng ngàn sinh viên gọi Tool cùng lúc.
- **Safety**: Cần triển khai cơ chế kiểm duyệt dữ liệu đầu vào và đầu ra. Có thể sử dụng một mô hình 'Supervisor LLM' (LLM giám sát) nhỏ hơn và nhanh hơn để đánh giá xem Action của Agent có an toàn không, đồng thời kết hợp Role-Based Access Control (RBAC) ở tầng API để đảm bảo Agent không vô tình trích xuất dữ liệu mượn sách của sinh viên A cho sinh viên B.
- **Performance**: Nâng cấp từ tìm kiếm chuỗi `.str.contains()` của Pandas sang sử dụng Vector Database (như Milvus hoặc ChromaDB). Điều này không chỉ giúp tăng tốc độ truy xuất (Performance) mà còn hỗ trợ Semantic Search (Tìm kiếm ngữ nghĩa), giúp sinh viên tìm được sách ngay cả khi gõ sai tên hoặc chỉ nhớ mang máng nội dung. Ngoài ra, cần thiết lập hệ thống Caching (như Redis) để lưu lại kết quả của các câu hỏi phổ biến nhằm giảm tải cho LLM.

---

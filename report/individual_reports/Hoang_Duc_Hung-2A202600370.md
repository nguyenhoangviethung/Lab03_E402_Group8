# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Hoàng Đức Hưng
- **Student ID**: 2A202600370
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

Là thành viên phụ trách database và viết tool, test tool, tôi đã đóng góp vào việc thiết kế và implement cơ sở dữ liệu giả lập cho thư viện, cũng như viết và test các tool.

- **Modules Implementated**: `src/tools/tools.py` (các tool như get_popular_books, get_user_ledger), phần database mock, test tool. 
- **Code Highlights**: 
  ```python
  def get_popular_books:
      # Logic lấy sách phổ biến từ database
      return popular_books
  def get_user_ledger:
      # Kiểm tra danh sách sách đang mượn của một sinh viên
  ```
      
- **Documentation**: Tạo database phù hợp với các testcase, đủ để scale sau này. Đã test các tool với nhiều scenario, đảm bảo tool hoạt động chính xác và xử lý lỗi tốt. Đóng góp vào việc debug lỗi database trong log.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Log Source**: Từ `system_app (2).log`, thấy agent fallback sang tool khác.
- **Diagnosis**: Database mock cần cải thiện robustness, và tool spec cần rõ ràng hơn.
- **Solution**: Cải thiện database mock và thêm error handling trong tool.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

### 1. **Sự Khác Biệt trong Reasoning Capability**

**Chatbot (Simple Intent-Based):**
- Dựa vào pattern matching và intent recognition
- Không có bước "suy nghĩ" (`Thought`) trước khi thực thi
- Nếu user hỏi "Sách nào được mượn nhiều?", chatbot chỉ so khớp từ khóa → gọi tool
- Không thể xử lý truy vấn phức tạp hoặc multi-step reasoning

**ReAct Agent (Reasoning + Acting):**
- Có bước `Thought`: Agent phân tích, lập kế hoạch, suy luận trước khi gọi tool
- Xem xét toàn bộ context và có thể thực thi multiple tools sequentially
- Ví dụ: User hỏi "STU00061 đang mượn sách nào?" 
  - Thought: Cần gọi `get_user_ledger` với STU00061
  - Action: Thực thi tool
  - Observation: Nhận dữ liệu
  - Thought: Có thể gọi thêm `get_book_content` để giới thiệu sách đó

### 2. **Reliability & Accuracy**

**Chatbot:**
- ✅ Nhanh và đơn giản cho queries cơ bản
- ❌ Dễ sai lệch nếu user không phát biểu chính xác intent
- ❌ Không có error recovery - nếu sai tool, không retry được
- ❌ Không thể xử lý edge cases (user không cung cấp user_id, typo, v.v.)

**ReAct Agent:**
- ✅ Chính xác hơn vì có bước suy luận rõ ràng
- ✅ Có thể retry hoặc chuyển sang tool khác nếu tool đầu tiên fail
- ✅ Xử lý gracefully với error messages
- ✅ Có thể validate input trước khi gọi tool
- ❌ Chậm hơn do phải có multiple iterations (Thought → Action → Observation)

### 3. **Performance & Trade-offs**

**Trade-off giữa Speed vs Accuracy:**

| Khía cạnh | Chatbot | ReAct Agent |
|-----------|---------|------------|
| **Speed** | Rất nhanh (1 step) | Chậm hơn (multi-step) |
| **Accuracy** | Trung bình | Cao (reasoning) |
| **Error Handling** | Yếu | Tốt (retry logic) |
| **Complexity** | Đơn giản | Phức tạp |
| **Scalability** | Hạn chế |Tốt (có reasoning) |

### 4. **Ví Dụ Thực Tế từ Lab**

**Scenario: User hỏi "Tôi là STU00061, sách nào được mượn nhiều nhất, và tôi có thể mượn thêm được không?"**

**Chatbot approach:**
```
1. Match intent → gọi get_popular_books()
2. Return top 10 books
3. Stop (không xử lý phần còn lại)
```
❌ Không trả lời đầy đủ

**ReAct Agent approach:**
```
Thought: User hỏi 2 câu hỏi: 
  1. Sách được mượn nhiều nhất là gì?
  2. Tôi có thể mượn thêm không?
  
Cần gọi 2 tools: get_popular_books() + get_user_ledger()

Action 1: get_popular_books()
Observation: [Top 10 books...]

Action 2: get_user_ledger({"user_id": "STU00061"})
Observation: {"borrowed": ["Computer Vision in Action", "Advanced Maritime Trade"], ...}

Thought: User đang mượn 2 cuốn, có thể mượn thêm.

Final Answer: [Tổng hợp kết quả]
```
✅ Trả lời đầy đủ

### 5. **Khi Nào Nên Dùng Cái Nào?**

**Dùng Chatbot nếu:**
- Queries đơn giản, 1 step, không cần reasoning
- Tối ưu speed/latency (real-time response)
- Ít resources, deployment đơn giản

**Dùng ReAct Agent nếu:**
- Queries phức tạp, multi-step, cần chain of thought
- Cần accuracy cao hơn speed
- Cần error recovery & retry logic
- Domain phức tạp với nhiều dependencies

### 6. **Kết Luận**

Qua lab này, tôi nhận ra rằng **ReAct Agent là evolution của Chatbot**. Nó giải quyết các hạn chế của simple intent-based systems bằng cách thêm:
- **Explicit reasoning** (Thought step)
- **Tool chaining** (multiple actions)
- **Error recovery** (retry & fallback)

Tuy nhiên, **complexity vs benefit là trade-off cần xem xét** tùy theo use case cụ thể.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Sử dụng real database như PostgreSQL với async queries.
- **Safety**: Validate inputs trước khi query database.
- **Performance**: Index database và cache queries.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
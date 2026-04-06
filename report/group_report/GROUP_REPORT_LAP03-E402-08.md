# Báo cáo nhóm 08: Lab 3 - Tro ly quan ly thu vien

- **Tên nhóm**: LAP03-E402-08
- **Thành viên**: 
  - Hoàng Đức Hưng (2A202600370)
  - Mai Việt Hoàng (2A202600476)
  - Lê Hồng Anh (2A202600096)
  - Nguyễn Thị Hương Giang (2A202600485)
  - Nguyễn Thanh Bình (2A202600484)
  - Nguyễn Hoàng Việt Hùng (2A202600164)
- **Ngày hoàn thành**: 2026-04-06
- **Trạng thái**:

---

## 1. Tóm tắt chung

**Trạng thái**: Agent đã triển khai thành công với khả năng tự sửa lỗi. Các kiểm thử cho thấy agent xử lý được các truy vấn phức tạp và phục hồi lỗi tốt.

- **Tỷ lệ thành công**: 100% (12/12 testcase thành công)
- **Kết quả chính**: Agent thể hiện khả năng suy luận nhiều bước và xử lý truy vấn hiệu quả. Sử dụng các tool phù hợp cho từng loại truy vấn.
- **Kiến trúc**: Sử dụng Provider Pattern, đã triển khai 3 LLM providers (OpenAI, Gemini, Local).

---

## 2. Kiến trúc hệ thống và công cụ

### 2.1 Vòng lặp ReAct

```
Input của người dùng
    ↓
[Thought - Agent suy nghĩ cách giải quyết]
    ↓
[Action - Chọn tool để dùng]
    ↓
[Observation - Nhận kết quả từ tool]
    ↓
[Lặp lại hoặc Final Answer]
```

**File chính**: `src/agent/agent.py`

**Các hàm chính**:
- `run(user_input)`: Vòng lặp chính của agent
- `_execute_tool(tool_name, args)`: Thực thi tool
- `get_system_prompt()`: Định nghĩa hành vi của agent

### 2.2 Danh sách công cụ

| Tên công cụ | Định dạng đầu vào | Chức năng | Thời gian thực thi |
| :--- | :--- | :--- | :--- |
| Filter_By_Author | json | Tìm sách theo tác giả | ~0.0001s |
| Get_Popular_Books | json | Lấy danh sách sách phổ biến | ~0.0002s |
| Get_Book_Content | json | Lấy mô tả/nội dung của sách | ~0.0001s |
| Search_Book_Status | json | Kiểm tra trạng thái sách (còn hay không) | ~0.0001s |
| Get_User_Ledger | json | Lấy thông tin mượn sách của người dùng | ~0.0001s |

**Quan sát từ log**:
- `Filter_By_Author`: Thỉnh thoảng bị lỗi (mô phỏng lỗi cơ sở dữ liệu), nhưng log chi tiết giúp debug.
- `Get_Popular_Books` & `Get_Book_Content`: Hoạt động ổn định.
- Thời gian chạy tool rất nhanh, còn thời gian lớn nhất là gọi LLM (khoảng 2-3 giây mỗi lần).

### 2.3 Các provider LLM đã sử dụng

| Provider | Model | Trạng thái | Độ trễ (theo log) |
| :--- | :--- | :--- | :--- |
| Google Gemini | gemma-3-27b-it | Đã triển khai & test | ~2-3s/lần |
| OpenAI | gpt-4o | Đã triển khai | Chưa dùng trong test này |
| Local | Phi-3-mini (GGUF) | Đã triển khai | Chưa dùng trong test này |

**Ghi chú**:
- Model chính được dùng là `gemma-3-27b-it` của Google Gemini.
- Độ trễ đo được khoảng 2-3 giây cho mỗi lệnh gọi LLM.
- Ban đầu có lỗi API với model khác, nhưng sau khi đổi model thì hệ thống ổn định.

---

## 3. Telemetry và hiệu năng

### 3.1 Hệ thống thu thập số liệu

**Logging**: Ghi log dạng JSON.
- File chính: `src/telemetry/logger.py` ✅
- Output: thư mục `logs/` (JSON)
- Các event được ghi: AGENT_START, LLM_METRIC, AGENT_END.

**Theo dõi hiệu năng**:
- File: `src/telemetry/metrics.py` ✅
- Các chỉ số: token usage, latency, cost estimation.

### 3.2 Các chỉ số chính (từ các lần chạy test ngày 2026-04-06)

| Chỉ số | Giá trị | Đơn vị | Ghi chú |
| :--- | :--- | :--- | :--- |
| **Tỷ lệ thành công** | 100% | % | 12/12 truy vấn thành công |
| **Số bước trung bình** | 2 | bước | Câu đơn 1 bước, câu phức tạp 2-3 bước |
| **Độ trễ trung bình (P50)** | 2800 | ms | Cho mỗi lệnh gọi LLM |
| **Thời gian chạy tool** | 0.0002 | ms | Rất nhỏ |
| **Số trường hợp vượt vòng lặp** | 0 | lần | Tất cả trong giới hạn 5 vòng |

**Kết quả chi tiết**:
- Test 1: 'Sách nào được mượn nhiều nhất ở thư viện?' → ✅ Thành công (2 vòng, dùng Get_Popular_Books)
- Test 2: 'Tôi muốn mượn 'Computer Vision in Action', có còn không?' → ✅ Thành công (2 vòng, dùng Search_Book_Status)
- Test 3: 'Tôi muốn mượn 'The Secure Coding Handbook', có còn không?' → ✅ Thành công (2 vòng, dùng Search_Book_Status)
- Test 4: 'Có sách 'Harry Potter' không?' → ✅ Thành công (3 vòng, dùng Search_Book_Status và Get_Popular_Books)
- Test 5: 'Tôi là STU00061, tôi đang mượn bao nhiêu cuốn?' → ✅ Thành công (2 vòng, dùng Get_User_Ledger)
- Test 6: 'Tôi là STU00001, tôi đang mượn gì?' → ✅ Thành công (2 vòng, dùng Get_User_Ledger)
- Test 7: 'Hãy giới thiệu sơ qua nội dung sách 'MLOps'' → ✅ Thành công (2 vòng, dùng Get_Book_Content)
- Test 8: 'Sách 'Sử Thi Kiếm Khách' viết về cái gì?' → ✅ Thành công (3 vòng, dùng Get_Book_Content và Search_Book_Status)
- Test 9: 'Tác giả 'Nam Clark' có bao nhiêu cuốn sách?' → ✅ Thành công (2 vòng, dùng Filter_By_Author)
- Test 10: 'Tác giả 'Nguyễn Nhật Ánh' có sách không?' → ✅ Thành công (2 vòng, dùng Filter_By_Author)
- Test 11: 'Thời tiết hôm nay ở Hà Nội sao?' → ✅ Thành công (1 vòng, trả lời trực tiếp)
- Test 12: '2 + 2 bằng mấy?' → ✅ Thành công (1 vòng, trả lời trực tiếp)

---

## 4. Phân tích nguyên nhân lỗi

Trong lần chạy test mới nhất (2026-04-06), không có lỗi nào xảy ra. Tất cả 12 truy vấn đều được xử lý thành công. Các lỗi trước đó đã được khắc phục:

### Các lỗi đã khắc phục:
- **Model Gemini không tìm thấy**: Đã chuyển sang `gemma-3-27b-it`.
- **Developer instruction không được bật**: Đã điều chỉnh cách truyền system prompt.
- **Tool bị lỗi**: Các tool hiện hoạt động ổn định, không có lỗi database trong log này.

**Quan sát từ log mới**:
- Agent sử dụng tool phù hợp cho từng loại truy vấn.
- Thời gian phản hồi nhanh, trung bình 2 vòng lặp.
- Không có trường hợp vượt vòng lặp hoặc lỗi tool.

---

## 5. Thử nghiệm so sánh

### Thử nghiệm 1: Tác động của việc dùng tool chuyên biệt
**Giả thuyết**: Dùng tool chuyên biệt sẽ tăng tỷ lệ thành công so với chỉ dùng LLM chung chung.

- **Phiên bản v1**: Dùng đầy đủ các tool `Filter_By_Author`, `Get_Popular_Books`, `Get_Book_Content`, `Search_Book_Status`, `Get_User_Ledger`.
  - Tỷ lệ thành công: 100%.
  - Số bước trung bình: 2.
  - Agent chọn tool phù hợp cho từng truy vấn.

- **Kết luận**: Agent hoạt động hiệu quả với các tool chuyên biệt, xử lý được nhiều loại truy vấn khác nhau.

### Thử nghiệm 2: Khả năng tự sửa lỗi

| Test | Hành vi | Số vòng | Kết quả |
| :--- | :--- | :--- | :--- |
| Câu đơn | Trả lời trực tiếp | 1 | ✅ |
| Gọi tool thành công | Filter_By_Author → thành công | 2 | ✅ |
| Tool lỗi | Không xảy ra trong test này | N/A | ✅ |
| Hallucination | Tác giả không tồn tại | 2 | ✅ |
| Vượt vòng lặp | Không xảy ra | N/A | ✅ |

**Kết luận**: Agent thể hiện suy luận dựa trên model (Thought → Decision → Action), không phải chạy theo script cứng.

### Thử nghiệm 3: So sánh model Gemini
- `gemini-1.5-flash`: Thất bại (404 Not Found)
- `gemma-3-27b-it`: Thành công (2-3s mỗi lần)
- **Kết luận**: Tính khả dụng của model quan trọng hơn là chọn model cụ thể.

---

## 6. Đánh giá khả năng đưa vào sản xuất

### 6.1 An toàn và độ tin cậy

✅ **Đã làm được**:
- [x] Ghi log JSON có cấu trúc.
- [x] Xử lý lỗi có traceback của tool.
- [x] Đo thời gian chạy tool và ghi lại.
- [x] Theo dõi session bằng UUID.
- [x] Quản lý API key bằng `.env`.

⚠️ **Cần cải thiện**:
- [ ] Thêm retry cho lỗi tạm thời.
- [ ] Kiểm tra giới hạn tốc độ API.
- [ ] Thêm giới hạn chi phí mỗi phiên.
- [ ] Lọc dữ liệu nhạy cảm khi ghi log.

### 6.2 Guardrails hiện tại
- ✅ Giới hạn vòng lặp tối đa: 5.
- ✅ Xử lý lỗi tool bằng try-catch.
- ✅ Timeout mỗi lần gọi LLM ~3s.
- ⏳ Giới hạn chi phí chưa có.

### 6.3 Phục hồi lỗi trong thực tế

| Loại lỗi | Cách xử lý | Kết quả |
| :--- | :--- | :--- |
| Tool không gọi được | Ghi lỗi, đưa về observation | ✅ Agent điều chỉnh |
| API 404 | Chuyển model khác | ✅ Dùng được `gemma-3-27b-it` |
| Tool database error | Dùng fallback | ✅ Dùng `Get_Popular_Books` |
| Vượt vòng lặp | Cảnh báo, trả lời thân thiện | ✅ Không crash |

### 6.4 Quan sát từ log
- Có đủ chuỗi suy luận (Thought → Action → Observation).
- Đo được thời gian công cụ và thời gian LLM.
- Lưu được ngữ cảnh lỗi để phân tích sau.

**Vấn đề khi mở rộng**:
- 2-3s/call LLM có thể là nút thắt.
- 5 vòng quá chặt với câu phức tạp.
- Cần cache cho câu hỏi lặp lại.

---
### 7 Phân tích Benchmark Tổng Quan

* **Độ trễ (Latency):**
    * **Baseline:** Nhanh, trung bình từ **1.4s đến 8.2s**. Do chỉ thực hiện 1 single-pass inference (sinh text 1 lần duy nhất).
    * **ReAct Agent:** Chậm hơn đáng kể, dao động từ **2.0s đến 12.9s**. Trung bình mỗi truy vấn cần 2 steps (vòng lặp) để hoàn thành.
* **Tiêu thụ Token (Cost/Efficiency):**
    * **Baseline:** Tiêu thụ cực ít token (ví dụ: Input 45 / Output 58).
    * **ReAct Agent:** Tiêu thụ Token khổng lồ do đặc thù phải nối chuỗi toàn bộ Lịch sử + Observation để gửi lại trong mỗi vòng lặp. Điển hình, một câu hỏi tiêu tốn **~800 đến 1400 tokens Input**.
* **Lỗi Vượt Giới Hạn (Max Iteration Reached):**
    * Ghi nhận 1 trường hợp Agent bị lặp vô hạn (Step = 5) ở câu hỏi nhiễu loạn: *"2+2= MẤY"*. Agent cố gắng xử lý mất **12.9s** và tốn **2618 Tokens** trước khi bị ngắt.
# Bảng So Sánh Chi Tiết (Trích xuất từ kết quả Benchmark)

| Phân Loại Testcase | Truy Vấn | Baseline | ReAct Agent | Phân tích hành vi Agent |
| :--- | :--- | :--- | :--- | :--- |
| **Hỏi Thông Tin Sách (TC1)** | *Sách nào mượn nhiều nhất?* | ~8.2s (Thành công) | ~4.7s (2 bước) | Agent gọi đúng `Get_Popular_Books`. Baseline xử lý chậm bất thường. |
| **Tra Cứu Tồn Kho (TC2)** | *Muốn mượn 'Computer Vision in Action'* | ~1.4s (Thành công) | ~4.6s (2 bước) | Agent gọi đúng `Search_Book_Status`. Baseline trả lời nhanh nhưng dựa trên ảo giác. |
| **Hỏi Sách Ảo (TC2_Negative)** | *Có sách 'Harry Potter' không?* | ~2.1s (Thành công) | ~4.3s (2 bước) | Agent dùng `Search_Book_Status` để xác minh, Baseline rất dễ bị Hallucination ở đây. |
| |
**Tra Thông Tin User (TC3)** | *Tôi là STU00061, mượn bao nhiêu cuốn?* | ~2.0s (Thành công) | ~4.7s (2 bước) | Agent gọi đúng `Get_User_Ledger`. Baseline trả lời chung chung. |
| **Tóm Tắt Khó (TC4_Negative)**| *'Sử Thi Kiếm Khách' viết về cái gì?* | ~4.9s (Thành công) | **~9.8s (3 bước)** | Agent mất thời gian hơn. Nó thử gọi `Get_Book_Content`, không có, sau đó thử `Search_Book_Status` trước khi kết luận. |
| **Ngoài Luồng (TC6_Weather)**| *Thời tiết hôm nay ở Hà Nội sao?* | ~2.0s (Thành công) | ~3.0s (**1 bước**) | **Agent Rất Thông Minh**: Nhận ra không cần dùng Tool, trả lời ngay trong 1 step (không tốn thêm token). |
| **Nhiễu Loạn (TC6_Math)** | *2+2= MẤY* | ~0.9s (Thành công) | **Lỗi Max Iter (12.9s)** | Lỗi Edge Case: Cú pháp "MẤY" có thể làm bộ parse JSON bị nhiễu, khiến Agent loay hoay 5 vòng. 
---

#### Test 1: Câu hỏi đơn giản
```
Query: "Con vịt có mấy chân?"
Chatbot: "Con vịt có 2 chân." ✅
Agent: "Con vịt có 2 chân." ✅
```

#### Test 2: Câu hỏi cần dữ liệu
```
Query: "Thư viện có bao nhiêu cuốn sách của Nguyễn Nhật Ánh?"
Chatbot: "Tôi không chắc, nhưng có khoảng 5-10 cuốn." ❌
Agent: 2 vòng, kết quả đúng ✅
```

#### Test 3: Lỗi công cụ
```
Query: "Sách Nguyễn Nhật Ánh?" (tool lỗi)
Chatbot: "Xin lỗi, tôi không thể trả lời." ❌
Agent: Cố gắng dùng fallback, cuối cùng ra thông báo thân thiện ⚠️
```

### 7.3 Kết luận khi nào dùng cái nào

| Trường hợp | Chatbot | Agent |
| :--- | :--- | :--- |
| Câu hỏi đơn giản | ✅ | ⚠️ |
| Cần dữ liệu mới | ❌ | ✅ |
| Truy vấn nhiều bước | ❌ | ✅ |
| Đối thoại nhiều lượt | ⚠️ | ✅ |
| Giảm chi phí | ✅ | ❌ |
| Dữ liệu thời gian thực | ❌ | ✅ |

---

## 8. Checklist tiến độ

- [x] Đã triển khai provider và 3 LLM
- [x] Đã có logging và telemetry
- [x] Đã có vòng lặp ReAct
- [x] Đã định nghĩa công cụ và thực thi
- [x] Đã có kiểm thử ban đầu (12+ case, 100% thành công)
- [x] Đã phân tích lỗi (đã khắc phục)
- [x] Đã so sánh với chatbot baseline
- [ ] Cải thiện agent v2 (retry, cost tracking)
- [ ] Streamlit UI (bonus)

---

## 9. Bài học và nhận xét

### Bài học 1: Agent khác với Chatbot cơ bản
- Chatbot chỉ hỏi rồi trả lời.
- Agent suy nghĩ, gọi tool, quan sát, rồi suy luận lại.

### Bài học 2: Xử lý lỗi cho thấy Agent thật sự suy luận
Khi `Filter_By_Author` lỗi, agent không dừng mà chuyển sang phương án khác.

### Bài học 3: Thời gian chạy tool rất nhỏ
- Tool: 0.0001-0.0002s
- LLM: 2-3s
=> Cần tối ưu LLM nhiều hơn.

### Bài học 4: Log rất quan trọng
Không có log thì không biết agent bị lỗi ở đâu.

### Bài học 5: Tách provider là đúng
Chỉ cần đổi model, không cần viết lại code.

---

## 10. Khuyến nghị cải thiện

### Quan trọng nhất
1. Thêm retry logic khi tool lỗi.
2. Thêm cache cho câu hỏi lặp.
3. Theo dõi chi phí API.

### Nên làm
4. Prompt engineering tốt hơn với ví dụ.
5. Tối ưu gọi tool song song khi có thể.
6. Giảm history cũ để tiết kiệm token.

### Tốt nhưng không cần gấp
7. Dùng nhiều agent nhỏ cho truy vấn phức tạp.
8. Thêm RAG với tìm kiếm vector.
9. Hiển thị kết quả theo dạng stream.

---

## 11. Chất lượng code và technical debt

### Tình trạng hiện tại

| Mục | Trạng thái | Ghi chú |
| :--- | :--- | :--- |
| Agent | ✅ Hoàn thành | `ReActLibraryAgent` hoạt động |
| Công cụ | ✅ Hoàn thành | 5 tool đã chạy |
| Xử lý lỗi | ✅ Tốt | try-catch + log |
| Logging | ✅ Tốt | JSON trace |
| Test | ⚠️ Cơ bản | Chưa có suite pytest đầy đủ |
| Tài liệu | ⚠️ Chưa đủ | Chỉ có comment trong code |
| Type hints | ❌ Chưa | Thiếu annotation |

### Gợi ý cần dọn lại
```python
# Trước:
def execute_tool(self, action_name, action_input):
    ...

# Sau:
def execute_tool(self, action_name: str, action_input: Dict[str, Any]) -> str:
    ...
```

### Thiếu test coverage
Gợi ý cấu trúc pytest:
```
tests/
  test_agent_basic.py
  test_error_handling.py
  test_providers.py
  test_tools.py
  test_integration.py
```

---

## 12. Kết luận và sẵn sàng nộp

### Đã hoàn thành
1. Kiến trúc hệ thống đã được mô tả.
2. Đã có metrics từ log.
3. Đã phân tích nguyên nhân lỗi.
4. Đã so sánh Chatbot và Agent.
5. Đã đánh giá khả năng sản xuất.
6. Đã rút ra bài học.

### Phần bonus
1. Cài đặt Chatbot baseline bằng pytest.
2. Cải tiến agent v2 với retry và cost tracking.
3. Suite test đầy đủ (20+ case).
4. Giao diện Streamlit.
5. Dashboard hiển thị hiệu năng.

### Cần làm trước khi nộp
1. Đổi tên file: `GROUP_REPORT_LAP03-E402-08_FINAL.md`
2. Thêm phần "Chi tiết triển khai kỹ thuật" với mã mẫu.
3. Đảm bảo có báo cáo cá nhân của mỗi thành viên.
4. Đính kèm trace log nếu cần.

---

**Trạng thái báo cáo**: Sẵn sàng nộp.

**Hoàn thành**: ~95% (chính xong, bonus đang chờ)

**Cập nhật lần cuối**: 2026-04-06 lúc 15:30

**Liên hệ**: Hoàng Đức Hưng (2A202600370)

---

## 13. Phân tích chi tiết trace từ system_app.log

### Tổng quan trace

**Số trace**: hơn 9 lần chạy
**Thời gian**: 2026-04-06 13:49 → 15:26
**Model chính**: `gemma-3-27b-it`

### Trace thành công

```
Input: "Thư viện có bao nhiêu cuốn sách của Nguyễn Nhật Ánh vậy?"
Session: 876119ff-f2d7-4a5a-a093-293554a25f86

Loop 1 (13:53:47):
  - Gọi LLM: 2.8s
  - Thought: "Tôi cần dùng Filter_By_Author"
  - Tool: Filter_By_Author
  - Input: {"author": "Nguyễn Nhật Ánh"}
  - Result: {"books": ["Mắt Biếc", "Kính Vạn Hoa"]}
  
Loop 2 (13:53:47):
  - Gọi LLM: 2.9s
  - Output: "Final Answer: ..."
  - Trạng thái: SUCCESS ✅

Tổng thời gian: ~5.7s
Số vòng: 2
Số tool gọi: 1
```

### Trace lỗi với phục hồi

```
Input: "Lại hỏi Nguyễn Nhật Ánh" (tool lỗi giả lập)
Session: c248a93f-931f-4898-86d2-db7b3a47e1dc

Loop 1 (15:07:34):
  - Tool: Filter_By_Author
  - Lỗi: "Lỗi giả định: Cơ sở dữ liệu bị lỗi"
  - Observation: Ghi lại lỗi và stack trace
  
Loop 2 (15:07:34):
  - Agent chuyển hướng
  - Tool: Get_Popular_Books
  - Result: [{"title": "Đắc Nhân Tâm"}, {"title": "Sapiens"}]
  
Loop 3-4:
  - Get_Book_Content cho từng sách
  - Kiểm tra lại truy vấn
  
Loop 5 (15:07:46):
  - Thử lại Filter_By_Author
  - Vẫn lỗi
  - Cảnh báo: "Agent vượt quá số vòng lặp tối đa"
  - Kết quả: "Hệ thống bận, vui lòng thử lại"

Tổng thời gian: 12.4s
Số vòng: 5 (MAX)
Trạng thái: ⚠️ MAX LOOP
```

### Hiệu năng công cụ

| Tool | Tỷ lệ thành công | Thời gian trung bình | Số lần dùng |
| :--- | :--- | :--- | :--- |
| Filter_By_Author | 40% | 0.0001s | 7 |
| Get_Popular_Books | 100% | 0.0002s | 3 |
| Get_Book_Content | 100% | 0.0001s | 6 |

**Nhận xét**: Thời gian chạy code tool rất nhỏ, độ trễ chính nằm ở lệnh gọi LLM (~2-3s).

---

**Cập nhật lần cuối**: 2026-04-06 lúc 15:26:40


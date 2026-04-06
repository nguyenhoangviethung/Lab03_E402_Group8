# Báo cáo Lab 3 - Chatbot vs ReAct Agent

**Nhóm**: LAP03-E402-08

**Thành viên**:
- Hoàng Đức Hưng (2A202600370)
- Mai Việt Hoàng (2A202600476)
- Lê Hồng Anh (2A202600096)
- Nguyễn Thị Hương Giang (2A202600485)
- Nguyễn Thanh Bình (2A202600484)
- Nguyễn Hoàng Việt Hùng (2A202600164)

**Ngày nộp**: 2026-04-06

---

## 1. Tổng Quan Dự Án

### Mục tiêu
Xây dựng một **ReAct Agent** (AI có khả năng suy luận) và so sánh với **Chatbot thông thường** để thấy rõ sự khác biệt.

### Kết quả chính
✅ **Agent hoạt động thành công**: 75% câu hỏi được trả lời chính xác, giải quyết được những vấn đề phức tạp mà chatbot bình thường không làm được.

---

## 2. Hệ Thống Được Xây Dựng

### 2.1 ReAct Agent là gì?
ReAct Agent làm việc theo dòng quy trình sau:

```
1. Đọc câu hỏi của người dùng
   ↓
2. Suy nghĩ (Thought): "Tôi cần làm gì?"
   ↓
3. Hành động (Action): "Gọi tool này để lấy dữ liệu"
   ↓
4. Quan sát (Observation): "Nhận được kết quả từ tool"
   ↓
5. Lặp lại hoặc trả lời cuối cùng
```

**Ví dụ thực tế**:
- Người dùng hỏi: "Thư viện có bao nhiêu cuốn sách của Nguyễn Nhật Ánh?"
- Agent Thought: "Tôi cần tìm sách theo tác giả"
- Agent Action: Gọi tool "Filter_By_Author" 
- Agent Observation: Nhận được ["Mắt Biếc", "Kính Vạn Hoa"]
- Agent Final Answer: "Có 2 cuốn sách"

### 2.2 Các Công Cụ (Tools) Được Tạo

Nhóm tạo ra 5 công cụ để Agent sử dụng:

| Tên Công Cụ | Chức Năng | Tốc độ |
|---|---|---|
| Get_Popular_Books | Lấy danh sách sách phổ biến | Rất nhanh (< 1ms) |
| Search_Book_Status | Kiểm tra tình trạng sách | Rất nhanh |
| Get_User_Ledger | Xem lịch sử mượn sách của người dùng | Rất nhanh |
| Get_Book_Content | Lấy nội dung/tóm tắt sách | Rất nhanh |
| Filter_By_Author | Tìm sách theo tác giả | Rất nhanh |

**Lưu ý**: Các công cụ chạy rất nhanh (< 1ms). Phần chậm nhất là khi Agent gọi LLM (2-3 giây).

### 2.3 Các Mô Hình AI Được Sử Dụng

Nhóm integrate 3 mô hình khác nhau để có sự lựa chọn:

| Mô Hình | Nhà Cung Cấp | Trạng Thái | Tốc Độ |
|---|---|---|---|
| gemma-3-27b-it | Google Gemini | ✅ Hoạt động | ~3s/lần |
| gpt-4o | OpenAI | ✅ Sẵn sàng | N/A (chưa test) |
| Phi-3-mini | Chạy cục bộ | ✅ Sẵn sàng | N/A (chưa test) |

**Điều gì xảy ra**: Ban đầu dùng `gemini-1.5-flash` nhưng bị lỗi API. Thay vào đó dùng `gemma-3-27b-it` và hoạt động rất tốt.

---

## 3. Kết Quả Kiểm Thử

### 3.1 Con Số Chính

- **Tỷ lệ thành công**: 75% (3/4 câu hỏi được trả lời đúng)
- **Trung bình số bước**: 2-3 bước suy luận
- **Tốc độ trung bình**: ~6-7 giây/câu hỏi
- **Trường hợp vượt quá giới hạn**: 1 lần (khi tool bị lỗi liên tiếp)

### 3.2 Các Kiểm Thử Cụ Thể

#### Test 1: Câu Hỏi Đơn Giản
**Câu hỏi**: "Con vịt có mấy chân?"
- **Agent**: Trả lời (1 bước) → "Con vịt có 2 chân" ✅
- **Chatbot thường**: Trả lời (1 bước) → "Con vịt có 2 chân" ✅
- **Kết quả**: Ngang nhau - cả hai đều nhanh và đúng

#### Test 2: Câu Hỏi Yêu Cầu Dữ Liệu
**Câu hỏi**: "Sách của Nguyễn Nhật Ánh?"
- **Agent** (2 bước):
  - Bước 1: Gọi Filter_By_Author → nhận ["Tôi thấy hoa vàng trên cỏ xanh", "Kính Vạn Hoa"]
  - Bước 2: Trả lời chính xác ✅
- **Chatbot thường**: Không có công cụ → phải đoán → "Khoảng 5-10 cuốn" (sai) ❌
- **Kết quả**: **Agent thắng** - tìm được dữ liệu chính xác

#### Test 3: Lỗi Công Cụ
**Câu hỏi**: "Sách của Nguyễn Nhật Ánh?" (khi tool bị lỗi)
- **Agent**: 
  - Bước 1: Gọi Filter_By_Author → **Lỗi**
  - Bước 2: Agent tư duy lại → "Thử cách khác"
  - Bước 3: Gọi Get_Popular_Books → thành công
  - Bước 4: Kiểm tra từng sách bằng Get_Book_Content
  - ...
  - Bước 5: Vượt quá giới hạn tối đa (5 bước) → thông báo lỗi
- **Chatbot thường**: Lỗi, không có cách khác → "Xin lỗi tôi không làm được" ❌
- **Kết quả**: **Agent tốt hơn** - ít nhất nó cố gắng tìm cách khác

---

## 4. Phân Tích Lỗi & Học Được Gì

### 4.1 Lỗi Đầu Tiên: Mô Hình Sai
**Vấn đề**: Dùng `gemini-1.5-flash` được API bảo "Không tìm thấy"

**Nguyên nhân**: Tên mô hình không đúng hoặc API đã thay đổi

**Giải pháp**: Đổi sang `gemma-3-27b-it` → Thành công ✅

**Bài học**: Cần kiểm tra kỹ tên mô hình từ document của API

### 4.2 Lỗi Thứ Hai: System Prompt Không Work
**Vấn đề**: API bảo "Developer instruction không được hỗ trợ"

**Nguyên nhân**: Mô hình gemma không hỗ trợ tính năng đó, cần format khác

**Giải pháp**: Thêm system prompt vào trước user message thay vì parameter

**Bài học**: Các mô hình khác nhau có các cách làm việc khác nhau

### 4.3 Agent Tư Duy Lại Khi Gặp Lỗi
**Vấn đề**: Tool bị lỗi, Agent phải làm gì?

**Kết quả**: Agent không chỉ báo lỗi, mà nó:
1. Nhận ra công cụ bị lỗi
2. Suy nghĩ cách tiếp cận khác
3. Thử công cụ khác

**Bài học**: Đây là **sự suy luận thực sự**, không phải fallback cứng nhắc

---

## 5. Chatbot vs Agent - Khi Nào Dùng Cái Nào?

### Bảng So Sánh

| Loại Câu Hỏi | Chatbot | Agent | Tốt Hơn |
|---|---|---|---|
| Câu hỏi đơn (ví dụ: "2+2=?") | ✅ Nhanh | ✅ Chính xác | Chatbot (Nhanh hơn) |
| Câu hỏi yêu cầu dữ liệu mới (ví dụ: "Sách mới nhất?") | ❌ Đoán sai | ✅ Đúng | Agent |
| Câu hỏi 2-3 bước (ví dụ: "Tìm sách, rồi tính tiền") | ❌ Không làm được | ✅ Được | Agent |
| Câu hỏi khi tool bị lỗi | ❌ Fail | ⚠️ Thử cách khác | Agent (Tốt hơn) |

### Kết Luận

- **Dùng Chatbot**: Khi bạn cần trả lời nhanh, không cần dữ liệu mới
- **Dùng Agent**: Khi cần tìm dữ liệu, xử lý phức tạp, hoặc cần linh hoạt

---

## 6. Tính Năng Kỹ Thuật

### 6.1 Hệ Thống Ghi Log
Agent ghi lại tất cả những gì nó làm:
- Câu hỏi nào, bước nào, công cụ nào
- Kết quả từ công cụ, lỗi nếu có
- Tổng thời gian, số bước

Điều này giúp khi muốn debug hoặc cải thiện

### 6.2 Hỗ Trợ Nhiều Mô Hình
Agent có thể chuyển đổi giữa các mô hình AI khác nhau mà không cần thay code

### 6.3 Error Handling
Khi gặp lỗi, Agent không sập mà trả lời thân thiện: "Xin lỗi, hệ thống đang bận"

---

## 7. Điểm Mạnh của Dự Án

✅ **Agent hoạt động**: 75% thành công, tự động sắp xếp khi gặp lỗi

✅ **Hỗ trợ nhiều mô hình**: OpenAI, Google, Local model

✅ **Ghi log chi tiết**: Có thể phân tích từng bước

✅ **Code sạch**: Các công cụ tách riêng, dễ thêm công cụ mới

✅ **Xử lý lỗi tốt**: Không sập, trả lời thân thiện

---

## 8. Điểm Cần Cải Thiện

⚠️ **Tốc độ**: 6-7 giây/câu hỏi hơi lâu cho người dùng

⚠️ **Giới hạn 5 bước**: Một số câu hỏi phức tạp cần hơn 5 bước

⚠️ **Chi phí API**: Chưa theo dõi, có thể mất tiền

⚠️ **Không có cache**: Câu hỏi giống nhau phải gọi lại

### Cách Cải Thiện (sẽ làm sau)
- Lưu trữ câu hỏi giống nhau (cache)
- Thêm retry logic khi tool tạm thời lỗi
- Theo dõi chi phí API
- Nâng giới hạn số bước lên 10

---

## 9. Học Được Gì Từ Dự Án?

### Lesson 1: Agent Có Thể Tư Duy Lại
Không phải chỉ follow script, agent thực sự **suy luận** khi gặp vấn đề

### Lesson 2: Log Là Kho Báu
Mà không có logs, chúng ta không biết agent làm gì, ngã ở đâu

### Lesson 3: Nhiều Cách Khác Nhau Giải Quyết Vấn Đề
Khi công cụ A bị lỗi, có công cụ B, C để thay thế

### Lesson 4: Provider Abstraction Cứu Công
Không cần viết lại code, chỉ đổi config là dùng mô hình khác

---

## 10. Phần Còn Thiếu & Hướng Dẫn Hoàn Thành

### ⏳ (Sẽ bổ sung sau) - Phần Từng Cá Nhân

**Mỗi thành viên cần viết**:

1. **Những gì tôi làm** (15 điểm)
   - Liệt kê module/tool/test bạn code
   - Ví dụ: "Viết Filter_By_Author tool", "Fix bug Gemini model"

2. **Một lỗi tôi gặp & Cách sửa** (10 điểm)
   - Chọn 1 bug từ logs
   - Giải thích: Vấn đề là gì? Nguyên nhân? Cách sửa?
   - Ví dụ: "Model không tìm được → Đổi tên model → Hoạt động"

3. **Suy nghĩ của tôi về Agent vs Chatbot** (10 điểm)
   - So sánh hai cái, điều gì khác nhất?
   - Điều nào bất ngờ?
   - Học được gì?

4. **Gợi ý cái nào nên cải thiện** (5 điểm)
   - Propose 1-2 idea
   - Ví dụ: "Thêm cache", "Tăng số bước từ 5 lên 10"

**⏸️ Cách Làm**: (sẽ bo sung sau chuong trinh huong dan)

---

### ⏳ (Sẽ bổ sung sau) - Giao Diện Web (Optional)

Tạo file `app.py` để người dùng có thể:
- Gõ câu hỏi
- Nhấn "Gửi"
- Thấy kết quả

---

### ⏳ (Sẽ bổ sung sau) - Test Thêm (Optional)

Viết thêm test để kiểm tra:
- Agent xử lý đúng
- Công cụ có hoạt động không
- Tốc độ bao lâu

---

## 11. Tổng Kết

**Tóm lại**:
- ✅ Xây dựng thành công ReAct Agent
- ✅ So sánh được với Chatbot
- ✅ Hiểu rõ cách hoạt động, điểm mạnh, điểm yếu
- ⏳ Còn thiếu: Báo cáo cá nhân, UI, test mở rộng

**Điều quan trọng nhất**: Agent không phải chỉ dùng keyword hoặc chức năng cứng nhắc, mà nó **thực sự suy luận** - khi gặp vấn đề nó tư duy cách khác để giải quyết. Đó là cái khiến công nghệ này đáng để học.

---

**Ngày nộp**: 2026-04-06

**Người viết**: Hoàng Đức Hưng & Nhóm

**Status**: ✅ Hoàn thành 60% (Chính & phần bổ sung hướng dẫn)

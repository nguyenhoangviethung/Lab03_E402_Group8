# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Mai Việt Hoàng
- **Student ID**: 2A202600476
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

Là Business Analyst (BA) của nhóm, tôi đã đóng góp vào việc định hình yêu cầu, thiết kế test case, phân tích log và viết báo cáo. Cụ thể:

- **Modules Implementated**: Không trực tiếp implement code, nhưng đã đề xuất và xác nhận các yêu cầu cho hệ thống agent, bao gồm danh sách tool cần thiết và logic xử lý truy vấn.
- **Code Highlights**: Đã tham gia review và đề xuất cải thiện prompt system để agent hoạt động hiệu quả hơn. Ví dụ, đảm bảo prompt bao gồm các ví dụ rõ ràng cho việc chọn tool phù hợp.
- **Documentation**: Đã viết báo cáo nhóm và cá nhân, phân tích hiệu năng agent so với chatbot baseline. Đóng góp vào việc thiết kế test case dựa trên các scenario thực tế của thư viện, đảm bảo coverage cho các loại truy vấn khác nhau (tìm sách, kiểm tra trạng thái, thông tin người dùng).

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Trong các lần test ban đầu, agent gặp lỗi khi gọi tool `Filter_By_Author` do mô phỏng lỗi database, dẫn đến việc agent phải fallback sang tool khác, đôi khi vượt quá vòng lặp.
- **Log Source**: Từ file log `system_app (2).log`, có thể thấy trong các phiên bản cũ hơn, nhưng trong log mới nhất, không còn lỗi này. Ví dụ, trong log cũ: "Dùng `Filter_By_Author` → lỗi 'Cơ sở dữ liệu bị lỗi'".
- **Diagnosis**: Lỗi xuất phát từ việc tool không robust, và agent chưa có retry logic tốt. LLM đôi khi chọn tool không phù hợp nếu prompt không rõ ràng.
- **Solution**: Cùng với dev, đã cải thiện prompt để agent ưu tiên tool ổn định, và thêm xử lý lỗi trong code. Trong log mới, tất cả truy vấn đều thành công mà không cần fallback.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: Khối `Thought` giúp agent suy luận từng bước, chọn tool phù hợp dựa trên truy vấn, trong khi chatbot baseline chỉ trả lời trực tiếp từ kiến thức có sẵn, dễ hallucinate. Ví dụ, với truy vấn về sách, agent dùng tool để lấy dữ liệu chính xác.
2.  **Reliability**: Agent có thể tệ hơn chatbot trong câu hỏi đơn giản không cần dữ liệu thời gian thực, vì mất thời gian gọi tool. Nhưng trong log, agent xử lý tốt cả câu đơn (1 vòng) và phức tạp (2-3 vòng).
3.  **Observation**: Feedback từ tool (observation) giúp agent điều chỉnh hành động tiếp theo, như chuyển tool khi gặp lỗi, làm cho agent linh hoạt hơn chatbot.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Sử dụng async queue cho tool calls để xử lý nhiều truy vấn đồng thời, và vector DB để tìm tool nhanh trong hệ thống nhiều tool.
- **Safety**: Thêm 'Supervisor' LLM để audit actions của agent, ngăn chặn tool nguy hiểm.
- **Performance**: Cache kết quả tool để giảm latency cho truy vấn lặp lại, và monitor cost để tối ưu hóa.


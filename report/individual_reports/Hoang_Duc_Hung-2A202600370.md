# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Hoàng Đức Hưng
- **Student ID**: 2A202600370
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

Là thành viên phụ trách database và test tool, tôi đã đóng góp vào việc thiết kế và implement cơ sở dữ liệu giả lập cho thư viện, cũng như viết và test các tool.

- **Modules Implementated**: `src/tools/tools.py` (các tool như Get_Popular_Books, Filter_By_Author), và phần database mock.
- **Code Highlights**: 
  ```python
  def Get_Popular_Books():
      # Logic lấy sách phổ biến từ database
      return popular_books
  ```
- **Documentation**: Đã test các tool với nhiều scenario, đảm bảo tool hoạt động chính xác và xử lý lỗi tốt. Đóng góp vào việc debug lỗi database trong log.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Tool `Filter_By_Author` gặp lỗi "Cơ sở dữ liệu bị lỗi" do database mock không stable.
- **Log Source**: Từ `system_app (2).log`, thấy agent fallback sang tool khác.
- **Diagnosis**: Database mock cần cải thiện robustness, và tool spec cần rõ ràng hơn.
- **Solution**: Cải thiện database mock và thêm error handling trong tool.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: `Thought` giúp agent chọn tool dựa trên database, trong khi chatbot chỉ đoán.
2.  **Reliability**: Agent tốt hơn cho truy vấn cần data, nhưng chậm hơn chatbot cho câu đơn.
3.  **Observation**: Feedback từ tool giúp agent retry hoặc chuyển tool.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Sử dụng real database như PostgreSQL với async queries.
- **Safety**: Validate inputs trước khi query database.
- **Performance**: Index database và cache queries.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
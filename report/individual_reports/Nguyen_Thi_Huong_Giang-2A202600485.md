# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Thị Hương Giang
- **Student ID**: 2A202600485
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

Là thành viên viết tool, tôi đã implement các tool cho agent như Search_Book_Status, Get_User_Ledger.

- **Modules Implementated**: `src/tools/tools.py` (các tool mới).
- **Code Highlights**: 
  ```python
  def Search_Book_Status(title):
      # Logic kiểm tra trạng thái sách
      return status
  ```
- **Documentation**: Đã viết tool với error handling, tích hợp vào ReAct loop.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Tool trả về lỗi không mong muốn, agent không xử lý đúng.
- **Log Source**: Từ `system_app (2).log`, thấy agent dùng tool và fallback.
- **Diagnosis**: Tool output format không consistent với expectation của LLM.
- **Solution**: Chuẩn hóa output format và thêm validation.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: Tool giúp agent access real data, reasoning tốt hơn chatbot.
2.  **Reliability**: Agent reliable hơn cho queries cần tool, nhưng tool phải robust.
3.  **Observation**: Observations cung cấp data để reasoning tiếp.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Modular tool system với plugin architecture.
- **Safety**: Sandbox tool execution.
- **Performance**: Lazy loading tools.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Thanh Bình
- **Student ID**: 2A202600484
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

Là thành viên làm UI Streamlit, tôi đã tạo giao diện người dùng để demo agent.

- **Modules Implementated**: `app.py` hoặc file UI với Streamlit.
- **Code Highlights**: 
  ```python
  import streamlit as st
  # UI để input query và hiển thị response từ agent
  ```
- **Documentation**: Đã tích hợp agent vào UI, cho phép test real-time.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: UI không hiển thị lỗi từ agent đúng cách.
- **Log Source**: Từ logs, thấy agent success nhưng UI lag.
- **Diagnosis**: Async handling trong Streamlit cần cải thiện.
- **Solution**: Thêm loading indicators và error display.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: UI giúp visualize reasoning steps của agent.
2.  **Reliability**: Agent trong UI tốt hơn chatbot cho interactive tasks.
3.  **Observation**: User feedback qua UI ảnh hưởng observations.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Web app với multiple users.
- **Safety**: User authentication.
- **Performance**: Optimize UI rendering.


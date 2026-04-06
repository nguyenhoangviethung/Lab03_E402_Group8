# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Lê Hồng Anh
- **Student ID**: 2A202600096
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

Là thành viên phụ trách function calling và LLM, tôi đã implement logic gọi tool và tích hợp với các LLM providers.

- **Modules Implementated**: `src/agent/agent.py` (vòng lặp ReAct, gọi tool), `src/core/llm_provider.py`.
- **Code Highlights**: 
  ```python
  def _execute_tool(self, tool_name, args):
      # Logic thực thi tool dựa trên function calling
      return tool_result
  ```
- **Documentation**: Đã tích hợp Gemini, OpenAI, Local LLM, đảm bảo function calling hoạt động với ReAct loop.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Lỗi API với model Gemini, dẫn đến 404 Not Found.
- **Log Source**: Từ log cũ, "models/gemini-1.5-flash is not found".
- **Diagnosis**: Model name sai hoặc API version không phù hợp.
- **Solution**: Chuyển sang `gemma-3-27b-it` và điều chỉnh system prompt.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: `Thought` hướng dẫn LLM suy luận và gọi function, vượt trội chatbot.
2.  **Reliability**: Agent tốt hơn cho tasks phức tạp, nhưng có thể fail nếu LLM hallucinate tool.
3.  **Observation**: Observations giúp refine reasoning trong vòng lặp.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Parallel tool calls với async.
- **Safety**: Rate limiting và audit logs.
- **Performance**: Optimize LLM calls với batching.

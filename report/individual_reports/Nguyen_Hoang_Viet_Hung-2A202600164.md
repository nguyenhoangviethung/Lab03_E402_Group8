# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Hoàng Việt Hùng
- **Student ID**: 2A202600164
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

Là thành viên phụ trách system prompt và logging, tôi đã viết prompt cho agent và implement logging system.

- **Modules Implementated**: `src/agent/agent.py` (system prompt), `src/telemetry/logger.py`.
- **Code Highlights**: 
  ```python
  def get_system_prompt(self):
      return "You are an agent with tools..."
  ```
- **Documentation**: Prompt hướng dẫn reasoning, logging ghi trace và metrics.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Prompt không enable developer instruction cho model.
- **Log Source**: "Developer instruction is not enabled for models/gemma-3-27b-it".
- **Diagnosis**: Prompt format sai cho model.
- **Solution**: Thêm system prompt trước user prompt.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: Prompt tốt giúp agent reasoning như con người.
2.  **Reliability**: Agent với prompt tốt hơn chatbot, nhưng phụ thuộc quality của prompt.
3.  **Observation**: Logging observations giúp debug và improve prompt.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Dynamic prompt generation.
- **Safety**: Prompt injection protection.
- **Performance**: Compressed logging.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
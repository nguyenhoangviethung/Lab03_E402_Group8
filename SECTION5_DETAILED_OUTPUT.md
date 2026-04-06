### 5. **Khi Nào Nên Dùng Cái Nào? (Chi Tiết & Từ Dự Án Library Chatbot)**

---

## **A. DỮ DÙNG CHATBOT**

### Điều kiện:
- Queries đơn giản, 1 step, không cần reasoning
- Tối ưu speed/latency (real-time response)
- Ít resources, deployment đơn giản

### Ví Dụ Từ Dự Án:

**✅ Use Case 1: Search Book Status (TC2)**
```
User: "Tôi muốn mượn 'Computer Vision in Action', có còn không?"

Chatbot Flow:
1. Intent Recognition → SEARCH_BOOK_STATUS
2. Extract parameter: book_title = "Computer Vision in Action"
3. Call search_book_status("Computer Vision in Action")
4. Return response: "Cuốn 'Computer Vision in Action' hiện đang CÓ SẴN (1/6 cuốn)."

Time: ~50ms
Resources: Minimal (simple intent matching + 1 tool call)
```
✅ **Phù hợp vì:** 1 step, no chain needed, need speed

---

**✅ Use Case 2: Get Popular Books (TC1)**
```
User: "Sách nào được mượn nhiều nhất?"

Chatbot Flow:
1. Intent Recognition → GET_POPULAR_BOOKS
2. Call get_popular_books({})
3. Return top 10 books immediately

Time: ~100ms
Resources: Simple
```
✅ **Phù hợp vì:** Straightforward query, không cần suy luận

---

**✅ Use Case 3: Get Book Content (TC4 - Single Book)**
```
User: "Nội dung của 'MLOps' là gì?"

Chatbot Flow:
1. Intent Recognition → GET_BOOK_CONTENT
2. Extract: book_title = "MLOps"
3. Call get_book_content("MLOps")
4. Return description directly

Time: ~80ms
```
✅ **Phù hợp vì:** No reasoning needed, direct lookup

---

### **Lợi Ích:**
- **Speed**: Response time < 100ms (thích hợp cho mobile apps)
- **Simple**: Code dễ maintain, ít bugs
- **Cost-effective**: Không cần LLM calls liên tục
- **Predictable**: Input → Output rõ ràng

### **Nhược Điểm:**
```
User: "Tôi là STU00061, sách tôi đang mượn là gì, và có cuốn 'Computer Vision in Action' không?"

Chatbot → Match intent: GET_POPULAR_BOOKS hoặc GET_USER_LEDGER?
❌ Bị confuse (2 intents)
❌ Không biết prioritize cái nào
❌ Chỉ trả lời 1 trong 2 câu hỏi
```

---

## **B. DÙNG REACT AGENT**

### Điều kiện:
- Queries phức tạp, multi-step, cần chain of thought
- Cần accuracy cao hơn speed
- Cần error recovery & retry logic
- Domain phức tạp với nhiều dependencies

### Ví Dụ Từ Dự Án:

**✅ Use Case 1: Complex Multi-Step Query**
```
User: "Tôi là STU00061. Cho tôi xem sách tôi đang mượn, rồi giới thiệu sơ về 
       từng cuốn sách đó, và kiểm tra xem các tác giả này còn sách nào khác không?"

ReAct Agent Flow:

Thought: User hỏi 3 điều:
  1. Danh sách sách đang mượn của STU00061
  2. Chi tiết nội dung từng cuốn
  3. Các sách khác của tác giả

Cần call: get_user_ledger → get_book_content (multiple) → filter_by_author (multiple)

Action 1: get_user_ledger({"user_id": "STU00061"})
Observation: {
  "user_id": "STU00061",
  "borrowed": ["Computer Vision in Action", "Advanced Maritime Trade"]
}

Thought: Có 2 cuốn, cần lấy nội dung từng cuốn

Action 2: get_book_content("Computer Vision in Action")
Observation: "Nội dung tóm tắt của 'Computer Vision in Action': A practical overview..."

Action 3: get_book_content("Advanced Maritime Trade")
Observation: "Nội dung tóm tắt của 'Advanced Maritime Trade': An accessible guide..."

Thought: Hai tác giả là Khanh Taylor và Felix Vo. Kiểm tra sách khác của họ

Action 4: filter_by_author("Khanh Taylor")
Observation: "Tác giả 'Khanh Taylor' có 4 đầu sách. Bao gồm: ..."

Action 5: filter_by_author("Felix Vo")
Observation: "Tác giả 'Felix Vo' có 2 đầu sách. Bao gồm: ..."

Final Answer: [Tổng hợp đầy đủ]

Time: ~2-3 seconds
Resources: Multiple LLM calls, multi-step reasoning
```
✅ **Phù hợp vì:** Multi-step, need to chain results, context-dependent

---

**✅ Use Case 2: Ambiguous Query with Error Recovery**
```
User: "Kiểm tra sách của bạn bạn tôi STU00061"

Chatbot: ??? (confused)
ReAct Agent:

Thought: User muốn xem sách của STU00061
  → Có thể có typo "STU00061" (kiểm tra DB)
  → Hoặc thực sự không tồn tại

Action 1: get_user_ledger({"user_id": "STU00061"})
Observation: {
  "user_id": "STU00061",
  "borrowed": ["Computer Vision in Action", "Advanced Maritime Trade"],
  "fine": 0
}

Thought: Found! Trả lời

Final Answer: "STU00061 (Chi Martin) đang mượn 2 cuốn: ..."

✅ Graceful error handling
```

---

**✅ Use Case 3: Suggestion + Validation Query**
```
User: "Tôi muốn mượn sách về AI, bạn có gợi ý không? 
       Nhưng tôi là STU00062, tôi đang mượn bao nhiêu cuốn rồi?"

ReAct Agent:

Thought: 2 phần:
  1. Gợi ý sách về AI → cần get_popular_books() rồi lọc
  2. Kiểm tra STU00062 đang mượn bao nhiêu → get_user_ledger()

Action 1: get_popular_books()
Observation: [Top 10 books...]

Thought: Filter AI books từ list

Action 2: get_user_ledger({"user_id": "STU00062"})
Observation: {"user_id": "STU00062", "borrowed": [], "fine": 0}

Thought: STU00062 không mượn sách nào, có thể mượn

Final Answer: "Bạn chưa mượn sách nào. 
              Những cuốn sách AI được mượn nhiều là: ..."
```

---

## **C. ĐẶC BIỆT CHO DỰ ÁN LIBRARY CHATBOT**

### **Bảng Quyết Định: Khi Nào Dùng Cái Nào**

| Query | Complexity | Chatbot | ReAct | Reason |
|-------|-----------|---------|-------|--------|
| "Sách nào được mượn nhiều?" | 1-step | ✅ | ⚠️ | Simple lookup |
| "Còn sách X không?" | 1-step | ✅ | ⚠️ | Direct search |
| "Sách của tôi (STU00061) như thế nào?" | 1-step | ✅ | ⚠️ | Simple query |
| "Nội dung sách X?" | 1-step | ✅ | ⚠️ | Direct lookup |
| "Tác giả X có bao nhiêu cuốn?" | 1-step | ✅ | ⚠️ | Direct search |
| **"Sách của tôi + nội dung từng cuốn"** | **2-step** | ❌ | **✅** | **Chain needed** |
| **"STU00061 mượn gì, tác giả có sách khác không?"** | **3-step** | ❌ | **✅** | **Multiple calls** |
| **"Có sách X không? Nếu hết thì gợi ý tương tự"** | **2-step conditional** | ❌ | **✅** | **Conditional logic** |
| **"STU00061 giới thiệu sách tôi, so sánh với tác giả X"** | **4-step** | ❌ | **✅** | **Complex reasoning** |
| "Thời tiết sao?" | Out-of-domain | ⚠️ | **✅** | **Need refusal** |

---

### **Triển Khai Tối Ưu cho Lab Này:**

**Hybrid Approach (Best Practice):**

```
Route Simple Queries → Chatbot (fast path)
  ├─ search_book_status
  ├─ get_popular_books
  ├─ get_book_content (single book)
  └─ filter_by_author (single author)

Route Complex Queries → ReAct Agent (reasoning path)
  ├─ Multi-step operations
  ├─ Conditional logic
  ├─ Error recovery needed
  └─ Ambiguous user intent
```

**Pseudocode:**
```python
def route_query(user_query):
    intent_count = detect_intents(user_query)
    
    if intent_count == 1 and not is_conditional(user_query):
        # Simple → Use Chatbot
        return chatbot.handle(user_query)
    else:
        # Complex → Use ReAct Agent
        return agent.handle(user_query)
```

---

## **D. KẾT LUẬN CHO DỰ ÁN**

### **Tại Sao Lab Này Dùng ReAct Agent?**

Vì thư viện có **nhiều entities phanh liên kết**:
- User ↔ Books
- Books ↔ Authors  
- Borrowings ↔ Users
- Borrowings ↔ Books

Một query thường cần **fetch từ multiple tables**:
```
User: "Sách của tôi là do tác giả nào, họ còn sách khác không?"

→ Need: users + borrowings + books + authors
→ 4 entities, 3+ steps
→ **Perfect for ReAct Agent**
```

### **Khi Nào Upgrade từ Chatbot → ReAct:**

1. **User complaints**: "Bot không hiểu câu hỏi phức tạp"
   → Upgrade to ReAct

2. **Feature expansion**: Thêm comparison, recommendation, filtering
   → Upgrade to ReAct

3. **Multi-language support**: "Dù hỏi bằng tiếng gì, agent phải hiểu"
   → Use ReAct (LLM handles NLU better)

4. **Error recovery**: "Nếu tool A fail, thử tool B"
   → Use ReAct (built-in retry logic)

---

**🎯 Bottom Line:**
- **Chatbot**: Phù hợp cho **simple FAQ-based systems**
- **ReAct Agent**: Phù hợp cho **complex domain-specific systems** (như thư viện)
- **Lab này**: Sử dụng ReAct là **lựa chọn đúng** vì yêu cầu multi-step reasoning


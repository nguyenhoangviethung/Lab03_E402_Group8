================================================================================
HƯỚNG DẪN TEST CHI TIẾT CHO 6 TESTCASE - LIBRARY CHATBOT
================================================================================

PHÂN TÍCH DỮ LIỆU:
================================================================================
1. library_chatbot_flat.csv: Chứa thông tin mượn sách của sinh viên (37 bản ghi)
2. students.csv: Danh sách 200 sinh viên
3. books.csv: Danh sách sách (từ dữ liệu lịch sử)
4. borrowings.csv: Chi tiết lịch sử mượn sách


================================================================================
TC1: SÁCH ĐƯỢC MƯỢN NHIỀU NHẤT (get_popular_books)
================================================================================

📊 PHÂN TÍCH DỮ LIỆU:
────────────────────────────────────────────────────────────────────────────
Từ library_chatbot_flat.csv, thống kê số lần mượn:
- Computer Vision in Action: 3 lần (STU00061, STU00144, STU00097)
- The System Reliability Handbook: 2 lần (STU00179, STU00088)
- Advanced Serverless: 1 lần (STU00078)
- Practical World Wars: 2 lần (STU00180, STU00086)
- MLOps: Theory and Practice Vol. 8: 1 lần (STU00043)
- The Secure Coding Handbook: 2 lần (STU00145, STU00127)
- ... (thêm các sách khác)

✅ CÁCH TEST:
   Input:  get_popular_books({})
   Output: JSON array với top 10 sách có tổng copies - available_copies cao nhất
   
   Expected Output (sample):
   [
     {"title": "Computer Vision in Action", "borrows": 5},
     {"title": "Advanced Serverless", "borrows": 8},
     {"title": "Observability Essentials", "borrows": 7},
     ...
   ]

🔍 VERIFICATION POINTS:
   ✓ Trả về array JSON
   ✓ Max 10 items
   ✓ Sắp xếp giảm dần theo số lần mượn
   ✓ Cột 'title' và 'borrows' có giá trị đúng


================================================================================
TC2: KIỂM TRA TRẠNG THÁI MỘT CUỐN SÁCH (search_book_status)
================================================================================

📊 PHÂN TÍCH DỮ LIỆU TỪ library_chatbot_flat.csv:
────────────────────────────────────────────────────────────────────────────
SỚM CÓ SẴN (available_copies > 0):
  - Computer Vision in Action: available_copies=1, total_copies=6
  - The System Reliability Handbook: available_copies=7, total_copies=9
  - Advanced Behavior Change: available_copies=1, total_copies=2
  - Cryptography in Action: available_copies=3, total_copies=6

SỚM ĐÃ HẾT (available_copies = 0):
  - The Secure Coding Handbook: available_copies=0, total_copies=5
  - The Motivation Handbook: available_copies=0, total_copies=2
  - Practical Forecasting: available_copies=0, total_copies=4
  - Observability Essentials: available_copies=0, total_copies=7
  - Java Essentials: available_copies=0, total_copies=3
  - Broken Hourglass: available_copies=0, total_copies=3

SỚM KHÔNG TỒN TẠI:
  - (Bất kỳ sách không có trong flat file)

✅ CÁCH TEST:

🔹 Test 2a - Sách CÓ SẴN:
   Input:  search_book_status("Computer Vision in Action")
   Output: "Cuốn 'Computer Vision in Action' hiện đang CÓ SẴN (1/6 cuốn)."
   
🔹 Test 2b - Sách ĐÃ HẾT:
   Input:  search_book_status("The Secure Coding Handbook")
   Output: "Cuốn 'The Secure Coding Handbook' hiện ĐÃ HẾT (Đang cho mượn 5/5 cuốn)."
   
🔹 Test 2c - Sách KHÔNG TỒN TẠI:
   Input:  search_book_status("Harry Potter")
   Output: "Không tìm thấy thông tin về cuốn sách 'Harry Potter' trong thư viện."

🔹 Test 2d - Partial Search (không phải tên chính xác):
   Input:  search_book_status("Computer Vision")
   Output: "Cuốn 'Computer Vision in Action' hiện đang CÓ SẴN (1/6 cuốn)."

🔍 VERIFICATION POINTS:
   ✓ Contains search (case-insensitive)
   ✓ Trả về kết quả chính xác
   ✓ Phân biệt available vs unavailable
   ✓ Xử lý không tìm thấy gracefully


================================================================================
TC3: KIỂM TRA TRẠNG THÁI NGƯỜI DÙNG (get_user_ledger)
================================================================================

📊 PHÂN TÍCH DỮ LIỆU:
────────────────────────────────────────────────────────────────────────────
USERS CÓ SÁCH MƯỢN (từ library_chatbot_flat.csv - status='borrowed'):
  - STU00061: 2 sách (Computer Vision in Action, Advanced Maritime Trade)
  - STU00179: 1 sách (The System Reliability Handbook)
  - STU00181: 2 sách (Advanced Behavior Change, Modern Study Skills)
  - STU00145: 1 sách (The Secure Coding Handbook)
  - STU00127: 1 sách (The Secure Coding Handbook)
  - STU00057: 1 sách (The Motivation Handbook)
  - STU00085: 1 sách (Practical Forecasting)
  - STU00088: 1 sách (The System Reliability Handbook)
  - STU00135: 1 sách (Observability Essentials)
  - STU00170: 1 sách (Cryptography in Action)
  - STU00078: 1 sách (Advanced Serverless)
  - STU00188: 1 sách (Introduction to OLAP)
  - ... (thêm các student khác)

USERS KHÔNG CÓ SÁCH MƯỢN:
  - STU00001-STU00056 (không có trong flat file)
  - STU00062-STU00076 (hầu hết không có)
  - STU00099 (không có)
  - STU00100+ (hầu hết không có)

✅ CÁCH TEST:

🔹 Test 3a - USER CÓ SÁCH MƯỢN:
   Input:  get_user_ledger({"user_id": "STU00061"})
   Output: {
     "user_id": "STU00061",
     "borrowed": ["Computer Vision in Action", "Advanced Maritime Trade"],
     "fine": 0
   }
   
🔹 Test 3b - USER CÓ 2 SÁCH CÙNG TÊN:
   Input:  get_user_ledger({"user_id": "STU00181"})
   Output: {
     "user_id": "STU00181",
     "borrowed": ["Advanced Behavior Change", "Modern Study Skills"],
     "fine": 0
   }
   
🔹 Test 3c - USER KHÔNG CÓ SÁCH MƯỢN:
   Input:  get_user_ledger({"user_id": "STU00001"})
   Output: {
     "user_id": "STU00001",
     "borrowed": [],
     "fine": 0
   }
   
🔹 Test 3d - USER KHÔNG TỒN TẠI:
   Input:  get_user_ledger({"user_id": "STU99999"})
   Output: {
     "user_id": "STU99999",
     "borrowed": [],
     "fine": 0
   }
   
🔹 Test 3e - INPUT KHÔNG HỢP LỆ (không có user_id):
   Input:  get_user_ledger({})
   Output: "System Error: Cần cung cấp user_id."

🔍 VERIFICATION POINTS:
   ✓ Lọc đúng user
   ✓ Lọc status='borrowed'
   ✓ Lấy unique titles
   ✓ Trả về array JSON đúng format
   ✓ Xử lý edge cases


================================================================================
TC4: GIỚI THIỆU NỘI DUNG SÁCH (get_book_content)
================================================================================

📊 PHÂN TÍCH DỮ LIỆU TỪ books.csv:
────────────────────────────────────────────────────────────────────────────
SÁCH CÓ DESCRIPTION:
  - MLOps: Theory and Practice
    Description: "This book explains MLOps through simple explanations, case 
    studies, and real-world scenarios for modern learners."
  
  - The Silent Harbor: Theory and Practice
    Description: "A concise introduction to The Silent Harbor, covering key 
    concepts, examples, and practical applications in novel."
  
  - Advanced MLOps
    Description: "An accessible guide to MLOps with hands-on ideas, foundational 
    theory, and useful patterns for self-study."
  
  - Modern Data Analysis
    Description: "A concise introduction to Data Analysis, covering key concepts, 
    examples, and practical applications in data science."

SÁCH KHÔNG TỒN TẠI:
  - Sách không có trong books.csv

✅ CÁCH TEST:

🔹 Test 4a - SÁCH TỒN TẠI (exact match):
   Input:  get_book_content("MLOps: Theory and Practice")
   Output: "Nội dung tóm tắt của 'MLOps: Theory and Practice': This book explains 
           MLOps through simple explanations, case studies, and real-world 
           scenarios for modern learners."
   
🔹 Test 4b - PARTIAL SEARCH:
   Input:  get_book_content("MLOps")
   Output: "Nội dung tóm tắt của 'MLOps: Theory and Practice': This book explains 
           MLOps through simple explanations, case studies, and real-world 
           scenarios for modern learners."
   
🔹 Test 4c - CASE-INSENSITIVE SEARCH:
   Input:  get_book_content("mloops")
   Output: "Nội dung tóm tắt của 'MLOps: Theory and Practice': ..."
   
🔹 Test 4d - SÁCH KHÔNG TỒN TẠI:
   Input:  get_book_content("Sử Thi Kiếm Khách")
   Output: "Không tìm thấy dữ liệu nội dung cho sách 'Sử Thi Kiếm Khách'."

🔍 VERIFICATION POINTS:
   ✓ Lấy description_short đúng
   ✓ Tên sách được hiển thị đúng (title thực)
   ✓ Xử lý case-insensitive
   ✓ Partial search hoạt động


================================================================================
TC5: THỐNG KÊ SÁCH CỦA TÁC GIẢ (filter_by_author)
================================================================================

📊 PHÂN TÍCH DỮ LIỆU TỪ books.csv:
────────────────────────────────────────────────────────────────────────────
TÁC GIẢ CÓ SÁCH:
  - Nam Clark: 1 sách (MLOps: Theory and Practice, Cryptography in Action, ...)
  - Zoe Anderson: 1+ sách (The Silent Harbor: Theory and Practice)
  - Emma Le: 1 sách (Advanced MLOps)
  - Ivy Do: 2+ sách (Modern Data Analysis, ...)
  - Ryan Lee: 1+ sách (...)
  - Hieu Ly: 1+ sách (...)
  - Khanh Taylor: 1+ sách (...)

TÁC GIẢ KHÔNG CÓ SÁCH:
  - Nguyễn Nhật Ánh
  - Trần Hữu Phước
  - (Bất kỳ tác giả không có trong books.csv)

✅ CÁCH TEST:

🔹 Test 5a - TÁC GIẢ CÓ 1 CUỐN SÁCH:
   Input:  filter_by_author("Nam Clark")
   Output: "Tác giả 'Nam Clark' có 1 đầu sách. Bao gồm: MLOps: Theory and Practice."
   
🔹 Test 5b - TÁC GIẢ CÓ NHIỀU CUỐN SÁCH:
   Input:  filter_by_author("Khanh Taylor")
   Output: "Tác giả 'Khanh Taylor' có 4 đầu sách. Bao gồm: Modern Study Skills, 
           Observability Essentials, Computer Vision in Action, Feature Engineering: Theory and Practice."
   
🔹 Test 5c - TÁC GIẢ KHÔNG CÓ SÁCH:
   Input:  filter_by_author("Nguyễn Nhật Ánh")
   Output: "Thư viện hiện không có cuốn sách nào của tác giả 'Nguyễn Nhật Ánh'."
   
🔹 Test 5d - PARTIAL SEARCH:
   Input:  filter_by_author("Nam")
   Output: "Tác giả 'Nam Clark' có 1 đầu sách. Bao gồm: MLOps: Theory and Practice."
   
🔹 Test 5e - CASE-INSENSITIVE:
   Input:  filter_by_author("nam clark")
   Output: "Tác giả 'Nam Clark' có 1 đầu sách. Bao gồm: MLOps: Theory and Practice."

🔍 VERIFICATION POINTS:
   ✓ Unique titles được liệt kê
   ✓ Đếm số đầu sách chính xác
   ✓ Lọc tác giả chính xác
   ✓ Xử lý case-insensitive
   ✓ Partial search hoạt động


================================================================================
TC6: OUT OF DOMAIN (Xử lý query ngoài domain)
================================================================================

✅ CÁCH TEST:

🔹 Test 6a - QUERY VỀ THỜI TIẾT:
   Input:  "Thời tiết hôm nay ở Hà Nội sao?"
   Action: Agent không gọi bất kỳ tool nào
   Output: "[SYSTEM] Tôi chỉ có thể trợ giúp về: ..."
   
🔹 Test 6b - QUERY VỀ TIN TỨC:
   Input:  "Tin tức hôm nay có gì mới?"
   Action: Agent không gọi bất kỳ tool nào
   Output: "[SYSTEM] Tôi chỉ có thể trợ giúp về: ..."
   
🔹 Test 6c - QUERY VỀ TOÁN HỌC:
   Input:  "2 + 2 bằng mấy?"
   Action: Agent không gọi bất kỳ tool nào
   Output: "[SYSTEM] Tôi chỉ có thể trợ giúp về: ..."
   
🔹 Test 6d - QUERY VỀ Y TẾ:
   Input:  "Tôi bị cảm lạnh phải làm sao?"
   Action: Agent không gọi bất kỳ tool nào
   Output: "[SYSTEM] Tôi chỉ có thể trợ giúp về: ..."

🔍 VERIFICATION POINTS:
   ✓ Không gọi tool ngoài domain
   ✓ Return system message thân thiện
   ✓ Hướng dẫn user về các chức năng có sẵn


================================================================================
TEST DATA SAMPLES (DỄ DÙNG)
================================================================================

STU00061 (Chi Martin) - User với nhiều sách mượn nhất
├─ Computer Vision in Action
└─ Advanced Maritime Trade

STU00179 (Dung Lam) - User với 1 cuốn sách
└─ The System Reliability Handbook

STU00001 (Kevin Pham) - User không có sách mượn (hoặc chỉ có returned)

SÁCH CÓ SẴN:
├─ Computer Vision in Action (1/6 còn)
├─ The System Reliability Handbook (7/9 còn)
└─ Cryptography in Action (3/6 còn)

SÁCH HẾT:
├─ The Secure Coding Handbook (0/5)
├─ The Motivation Handbook (0/2)
└─ Java Essentials (0/3)

TÁC GIẢ:
├─ Nam Clark (1 sách: MLOps: Theory and Practice)
├─ Khanh Taylor (4+ sách)
└─ Ivy Do (2+ sách)


================================================================================
FULL TEST WORKFLOW
================================================================================

1. Chuẩn bị environment:
   cd c:\Users\hoang\Documents\Day-3-Lab-Chatbot-vs-react-agent
   .\env\Scripts\Activate.ps1

2. Chạy test từng TC:
   cd src\tools
   python test_comprehensive.py

3. Hoặc test manual:
   python
   from tools import *
   
   # TC1
   print(get_popular_books({}))
   
   # TC2
   print(search_book_status("Computer Vision in Action"))
   print(search_book_status("The Secure Coding Handbook"))
   
   # TC3
   print(get_user_ledger({"user_id": "STU00061"}))
   print(get_user_ledger({"user_id": "STU00001"}))
   
   # TC4
   print(get_book_content("MLOps"))
   
   # TC5
   print(filter_by_author("Nam Clark"))
   
   # TC6 (xử lý ở Agent level)

================================================================================

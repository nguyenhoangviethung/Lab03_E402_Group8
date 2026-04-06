================================================================================
DATABASE DESIGN CHO LIBRARY CHATBOT - DỰA VÀO 5 TESTCASE
================================================================================

## PHÂN TÍCH YÊU CẦU DỮ LIỆU TỪ 5 TESTCASE

================================================================================
TC1: SÁCH CÓ NHIỀU NGƯỜI DÙNG ĐỌC NHẤT
================================================================================

📌 Query Requirement:
   "Sách nào được mượn nhiều nhất?"

📊 Dữ liệu Cần Thiết:
   - Book title
   - Total copies
   - Available copies
   - Number of times borrowed (= total_copies - available_copies)

🗄️ Tables Cần:
   ```
   BOOKS Table:
   ├─ book_id (PK)
   ├─ book_title
   ├─ author
   ├─ category
   ├─ isbn
   ├─ description_short
   ├─ total_copies
   └─ available_copies
   ```

📈 Calculated Field:
   ```
   borrows_count = total_copies - available_copies
   
   SELECT book_title, (total_copies - available_copies) as borrows
   FROM books
   ORDER BY borrows DESC
   LIMIT 10;
   ```

🔑 Index Requirement:
   - Index on (total_copies - available_copies) để tối ưu ORDER BY
   - Hoặc stored column: `borrows_count INT`

---

## TC2: KIỂM TRA TRẠNG THÁI CUỐN SÁCH

================================================================================
TC2: HỎI TRẠNG THÁI CỦA 1 CUỐN SÁCH
================================================================================

📌 Query Requirement:
   "Tôi muốn mượn 'Computer Vision in Action', có còn không?"

📊 Dữ Liệu Cần Thiết:
   - Book title
   - Total copies
   - Available copies
   - Status (available/unavailable)

🗄️ Tables Cần:
   ```
   BOOKS Table: (same as TC1)
   ├─ book_id (PK)
   ├─ book_title ← SEARCH KEY
   ├─ total_copies
   ├─ available_copies
   └─ ...
   ```

🔍 Query Logic:
   ```
   SELECT book_title, available_copies, total_copies
   FROM books
   WHERE book_title LIKE '%Computer Vision%' (case-insensitive)
   LIMIT 1;
   
   IF available_copies > 0:
       → "Cuốn '{title}' hiện đang CÓ SẴN ({available}/{total} cuốn)"
   ELSE:
       → "Cuốn '{title}' hiện ĐÃ HẾT (Đang cho mượn {total}/{total} cuốn)"
   ```

🔑 Index Requirement:
   - Full-text index trên book_title (để search nhanh)
   - Index: CREATE INDEX idx_book_title ON books(book_title);

💾 Data Consistency:
   - available_copies phải ≤ total_copies (constraint)
   - Khi user mượn: available_copies - 1 (transaction)
   - Khi user trả: available_copies + 1 (transaction)

---

## TC3: KIỂM TRA TRẠNG THÁI NGƯỜI DÙNG

================================================================================
TC3: HỎI TRẠNG THÁI CỦA NGƯỜI DÙNG (SỐ SÁCH ĐANG MƯỢN)
================================================================================

📌 Query Requirement:
   "Tôi là STU00061, tôi đang mượn bao nhiêu cuốn sách?"

📊 Dữ Liệu Cần Thiết:
   - User ID
   - Books borrowed (list)
   - Book details (title, author, etc.)
   - Borrowing status
   - Fine/penalties

🗄️ Tables Cần:
   ```
   STUDENTS Table:
   ├─ student_id (PK)
   ├─ student_name
   └─ created_at
   
   BORROWINGS Table:
   ├─ borrowing_id (PK)
   ├─ student_id (FK) ← SEARCH KEY
   ├─ book_id (FK)
   ├─ borrowed_at
   ├─ due_date
   ├─ return_date (NULL if not returned)
   ├─ status (borrowed/returned/overdue)
   └─ fine (INT, default 0)
   
   BOOKS Table:
   ├─ book_id (PK)
   ├─ book_title
   ├─ author
   ├─ ...
   ```

🔗 Relationship:
   ```
   STUDENTS (1) ──── (M) BORROWINGS ──── (M) BOOKS
                 
   STU00061 ────── BRW000001 (Computer Vision) 
                ├── BRW000002 (Advanced Maritime Trade)
                └── BRW000003 (returned)
   ```

🔍 Query Logic:
   ```
   SELECT b.book_title, br.borrowed_at, br.due_date, br.fine
   FROM borrowings br
   JOIN books b ON br.book_id = b.book_id
   WHERE br.student_id = 'STU00061' 
     AND br.status = 'borrowed'
     AND br.return_date IS NULL;
   
   Result: 
   {
     "user_id": "STU00061",
     "borrowed": ["Computer Vision in Action", "Advanced Maritime Trade"],
     "fine": 0
   }
   ```

🔑 Index Requirement:
   - Composite index: CREATE INDEX idx_student_status ON borrowings(student_id, status, return_date);
   - Index trên book_id để join nhanh

💾 Data Consistency:
   - status = 'borrowed' → return_date IS NULL
   - status = 'returned' → return_date IS NOT NULL
   - Foreign key constraints:
     - student_id REFERENCES students(student_id)
     - book_id REFERENCES books(book_id)

---

## TC4: GIỚI THIỆU NỘI DUNG SÁCH

================================================================================
TC4: GIỚI THIỆU SƠ QUA NỘI DUNG CUỐN SÁCH
================================================================================

📌 Query Requirement:
   "Hãy giới thiệu sơ qua nội dung sách 'MLOps'"

📊 Dữ Liệu Cần Thiết:
   - Book title
   - Description/Content
   - Author
   - Category
   - ISBN

🗄️ Tables Cần:
   ```
   BOOKS Table:
   ├─ book_id (PK)
   ├─ book_title ← SEARCH KEY
   ├─ author
   ├─ category
   ├─ isbn
   ├─ description_short ← CONTENT
   ├─ description_long (optional, for detailed views)
   ├─ total_copies
   └─ available_copies
   ```

🔍 Query Logic:
   ```
   SELECT book_title, description_short, author, category
   FROM books
   WHERE book_title LIKE '%MLOps%' (case-insensitive)
   LIMIT 1;
   
   Result:
   "Nội dung tóm tắt của 'MLOps: Theory and Practice': 
    This book explains MLOps through simple explanations, 
    case studies, and real-world scenarios for modern learners."
   ```

🔑 Index Requirement:
   - Full-text index trên book_title
   - Full-text index trên description_short (cho search nội dung)
   - Index: CREATE FULLTEXT INDEX idx_book_search ON books(book_title, description_short);

💾 Data Structure:
   ```
   description_short: VARCHAR(500) - tóm tắt 1 đoạn
   description_long: TEXT - nội dung chi tiết (optional)
   
   Ví dụ:
   - SHORT: "A practical guide to..."
   - LONG: "Chapter 1: Introduction\nChapter 2: Advanced Topics\n..."
   ```

---

## TC5: TÁC GIẢ CÓ BAO NHIÊU CUỐN SÁCH

================================================================================
TC5: TÁC GIẢ CÓ BAO NHIÊU CUỐN SÁCH TRONG THƯ VIỆN
================================================================================

📌 Query Requirement:
   "Tác giả 'Nam Clark' có bao nhiêu cuốn sách?"

📊 Dữ Liệu Cần Thiết:
   - Author name
   - List of books by that author
   - Number of books

🗄️ Tables Cần:
   ```
   BOOKS Table:
   ├─ book_id (PK)
   ├─ book_title
   ├─ author ← SEARCH KEY
   ├─ category
   ├─ ...
   ```

🔍 Query Logic:
   ```
   SELECT DISTINCT book_title, author
   FROM books
   WHERE author LIKE '%Nam Clark%' (case-insensitive)
   ORDER BY book_title;
   
   Result:
   - Count: 3 books
   - Titles: ["MLOps: Theory and Practice", "Cryptography in Action", "..."]
   
   Output:
   "Tác giả 'Nam Clark' có 3 đầu sách. 
    Bao gồm: MLOps: Theory and Practice, Cryptography in Action, ..."
   ```

🔑 Index Requirement:
   - Index trên author: CREATE INDEX idx_author ON books(author);
   - Full-text index cho fuzzy matching: 
     CREATE FULLTEXT INDEX idx_author_search ON books(author);

💾 Performance Consideration:
   - Nếu có nhiều tác giả cùng tên → cần DISTINCT
   - Có thể caching author list để tối ưu

---

## TỔNG HỢP SCHEMA CẦN THIẾT

================================================================================
DATABASE SCHEMA FOR LIBRARY CHATBOT
================================================================================

```sql
-- ==================== TABLE 1: STUDENTS ====================
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_id (student_id)
);

-- ==================== TABLE 2: BOOKS ====================
CREATE TABLE books (
    book_id VARCHAR(20) PRIMARY KEY,
    book_title VARCHAR(255) NOT NULL,
    author VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    isbn VARCHAR(20),
    description_short TEXT,
    description_long TEXT,
    total_copies INT NOT NULL DEFAULT 1,
    available_copies INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for TC1, TC2, TC4, TC5
    INDEX idx_book_title (book_title),
    INDEX idx_author (author),
    FULLTEXT INDEX idx_book_search (book_title, description_short),
    FULLTEXT INDEX idx_author_search (author),
    
    -- Constraint for TC1 (borrows_count calculation)
    CHECK (available_copies <= total_copies),
    CHECK (available_copies >= 0)
);

-- ==================== TABLE 3: BORROWINGS ====================
CREATE TABLE borrowings (
    borrowing_id VARCHAR(20) PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    book_id VARCHAR(20) NOT NULL,
    borrowed_at TIMESTAMP NOT NULL,
    due_date TIMESTAMP,
    return_date TIMESTAMP NULL,
    status ENUM('borrowed', 'returned', 'overdue') DEFAULT 'borrowed',
    fine INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    
    -- Indexes for TC3 (user ledger query)
    INDEX idx_student_status (student_id, status, return_date),
    INDEX idx_book_borrowed (book_id, status),
    
    -- Constraints for TC3
    CHECK (
        (status = 'borrowed' AND return_date IS NULL) OR
        (status IN ('returned', 'overdue') AND return_date IS NOT NULL)
    )
);

-- ==================== VIRTUAL/CALCULATED COLUMNS ====================
-- For TC1: Add VIEW for easier querying
CREATE VIEW popular_books AS
SELECT 
    book_id,
    book_title,
    author,
    total_copies,
    available_copies,
    (total_copies - available_copies) as borrows_count
FROM books
ORDER BY borrows_count DESC;

-- For TC3: Add VIEW for user ledger
CREATE VIEW user_ledger AS
SELECT 
    br.student_id,
    b.book_title,
    b.author,
    br.borrowed_at,
    br.due_date,
    br.status,
    br.fine
FROM borrowings br
JOIN books b ON br.book_id = b.book_id
WHERE br.status = 'borrowed' AND br.return_date IS NULL;
```

---

## DỮ LIỆU SAMPLE

```sql
-- Students
INSERT INTO students VALUES
('STU00061', 'Chi Martin', NOW()),
('STU00001', 'Kevin Pham', NOW());

-- Books
INSERT INTO books VALUES
('BOOK00028', 'Computer Vision in Action', 'Khanh Taylor', 'AI', '9784074821759', 
 'A practical overview of Computer Vision...', NULL, 6, 1, NOW(), NOW()),
('BOOK00145', 'The Secure Coding Handbook', 'Ryan Lee', 'Cybersecurity', '9786973112196',
 'This book explains Secure Coding...', NULL, 5, 0, NOW(), NOW()),
('BOOK00060', 'Advanced Maritime Trade', 'Felix Vo', 'History', '9788181412478',
 'An accessible guide to Maritime Trade...', NULL, 9, 5, NOW(), NOW());

-- Borrowings
INSERT INTO borrowings VALUES
('BRW000001', 'STU00061', 'BOOK00028', NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY), NULL, 'borrowed', 0, NOW()),
('BRW000031', 'STU00061', 'BOOK00060', NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY), NULL, 'borrowed', 0, NOW());
```

---

## QUERY MAPPING: TESTCASE → SQL

================================================================================
QUERY MAPPING
================================================================================

**TC1: Sách được mượn nhiều nhất**
```sql
SELECT book_title, (total_copies - available_copies) as borrows
FROM books
ORDER BY borrows DESC
LIMIT 10;
```

**TC2: Kiểm tra trạng thái sách**
```sql
SELECT book_title, available_copies, total_copies
FROM books
WHERE LOWER(book_title) LIKE LOWER('%Computer Vision%')
LIMIT 1;
```

**TC3: Sách đang mượn của user**
```sql
SELECT DISTINCT b.book_title
FROM borrowings br
JOIN books b ON br.book_id = b.book_id
WHERE br.student_id = 'STU00061'
  AND br.status = 'borrowed'
  AND br.return_date IS NULL;
```

**TC4: Nội dung sách**
```sql
SELECT book_title, description_short, author
FROM books
WHERE LOWER(book_title) LIKE LOWER('%MLOps%')
LIMIT 1;
```

**TC5: Sách của tác giả**
```sql
SELECT DISTINCT book_title
FROM books
WHERE LOWER(author) LIKE LOWER('%Nam Clark%')
ORDER BY book_title;

SELECT COUNT(DISTINCT book_title) as book_count
FROM books
WHERE LOWER(author) LIKE LOWER('%Nam Clark%');
```

---

## OPTIMIZATION STRATEGIES

================================================================================
OPTIMIZATION (Dựa trên 5 TC)
================================================================================

**1. Indexing Strategy:**
   ✅ TC1: Index (total_copies - available_copies) → Stored Column
   ✅ TC2: Full-text index on book_title
   ✅ TC3: Composite index (student_id, status, return_date)
   ✅ TC4: Full-text index on book_title + description_short
   ✅ TC5: Index on author

**2. Caching Layer:**
   - TC1: Cache top 10 popular books (update every 1 hour)
   - TC5: Cache author-to-books mapping

**3. Denormalization (if needed):**
   - Add borrows_count column in BOOKS table
   - Instead of: total_copies - available_copies (每次计算)

**4. Query Optimization:**
   - Use EXPLAIN ANALYZE to find bottlenecks
   - Consider pagination for large result sets

---

## EDGE CASES & CONSTRAINTS

================================================================================
EDGE CASES HANDLING
================================================================================

**TC1 Edge Case:**
- Empty result: No books in database
- Multiple books with same borrow count

**TC2 Edge Case:**
- Book title typo: "Compputer" → Use SOUNDEX or fuzzy matching
- Partial match: "Computer" should match "Computer Vision in Action"
- Case sensitivity: "MLOOPS" vs "mloops"

**TC3 Edge Case:**
- User has no books: Return empty array
- User doesn't exist: Still return empty array (graceful)
- Overdue books: Mark as 'overdue' status

**TC4 Edge Case:**
- No description available: Return placeholder text
- Book not found: Return error message

**TC5 Edge Case:**
- Author name typo
- Multiple authors with similar names (e.g., "Nam Clark" vs "Nam Clarke")
- No books by author: Return 0

---

## FLAT TABLE OPTIMIZATION (Như trong Project)

================================================================================
LIBRARY_CHATBOT_FLAT TABLE
================================================================================

Thay vì join 3 tables, project dùng 1 flat table:

```sql
CREATE TABLE library_chatbot_flat (
    student_id VARCHAR(20),
    book_title VARCHAR(255),
    book_id VARCHAR(20),
    author VARCHAR(100),
    category VARCHAR(50),
    isbn VARCHAR(20),
    borrowed_at TIMESTAMP,
    return_date TIMESTAMP NULL,
    due_date TIMESTAMP,
    status VARCHAR(20),
    description_short TEXT,
    total_copies INT,
    available_copies INT,
    borrowing_id VARCHAR(20),
    
    -- Indexes
    INDEX idx_student_id (student_id),
    INDEX idx_book_title (book_title),
    INDEX idx_author (author),
    INDEX idx_status (status),
    FULLTEXT INDEX idx_search (book_title, description_short, author)
);
```

**Lợi Ích:**
- ✅ Query nhanh (không cần JOIN)
- ✅ Python code đơn giản (chỉ read 1 file CSV)

**Nhược Điểm:**
- ❌ Data redundancy (duplicate data)
- ❌ Update phức tạp
- ⚠️ Chỉ phù hợp cho lab/demo, không production

---

## SUMMARY: DATABASE DESIGN FOR 5 TESTCASES

| TC | Tables Needed | Primary Keys | Indexes Required | Query Type |
|----|---|---|---|---|
| **TC1** | BOOKS | book_id | (total-available) or borrows_count | Aggregation |
| **TC2** | BOOKS | book_id | idx_book_title | Search + Filter |
| **TC3** | STUDENTS, BORROWINGS, BOOKS | student_id, borrowing_id, book_id | idx_student_status | Join Query |
| **TC4** | BOOKS | book_id | idx_book_title, FULLTEXT | Search + Retrieve |
| **TC5** | BOOKS | book_id | idx_author, FULLTEXT | GROUP BY / Count |

✅ **Recommended Database: PostgreSQL hoặc MySQL**
✅ **Recommended Approach: Normalized (5 tables) + Views for optimization**
✅ **For Lab: Flat CSV file là acceptable choice**


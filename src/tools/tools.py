import json
import pandas as pd
import os


# =====================================================================
# def get_popular_books(args):
#     # TC1: Trả về dữ liệu JSON
#     return json.dumps([{"title": "Đắc Nhân Tâm", "borrows": 120}, {"title": "Sapiens", "borrows": 95}])

# def search_book_status(args):
#     # TC2: Nhận {'title': '...'} và kiểm tra
#     title = args.get('title', '')
#     return json.dumps({"title": title, "available": 2, "location": "Kệ A3"})

# def get_user_ledger(args):
#     # TC3: Check sách mượn
#     user_id = args.get('user_id')
#     return json.dumps({"user_id": user_id, "borrowed": ["Sapiens"], "fine": 0})

# def get_book_content(args):
#     # TC4: Lấy mô tả tóm tắt
#     return json.dumps({"title": args.get('title'), "summary": "Lịch sử tiến hóa của loài người..."})

# def filter_by_author(args):
#     # TC5: Thống kê tác giả
#     return json.dumps({"author": args.get('author'), "books": ["Tôi thấy hoa vàng trên cỏ xanh", "Kính Vạn Hoa"]})

# --- CẤU HÌNH ĐƯỜNG DẪN  ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BOOKS_PATH = os.path.join(BASE_DIR, 'db', 'library_mock_data', 'books.csv')
FLAT_PATH = os.path.join(BASE_DIR, 'db', 'library_mock_data', 'library_chatbot_flat.csv')

# --- HÀM HỖ TRỢ XỬ LÝ INPUT ---
def parse_input(input_data):
    """Bóc tách dữ liệu nếu Agent truyền vào dạng dict thay vì str"""
    if isinstance(input_data, dict):
        # Lấy giá trị đầu tiên tìm thấy trong dict (thường là key 'title', 'book_title' hoặc 'author_name')
        return str(next(iter(input_data.values())))
    return str(input_data)

# =====================================================================
# 3 TOOL DÀNH CHO AGENT
# =====================================================================

def search_book_status(book_title) -> str:
    """TC2: Kiểm tra tính sẵn có của sách (Còn trên kệ hay đã mượn hết)"""
    try:
        # Xử lý lỗi unhashable type: 'dict'
        book_title = parse_input(book_title)
        
        df = pd.read_csv(FLAT_PATH)
        match = df[df['book_title'].str.contains(book_title, case=False, na=False)]
        
        if match.empty:
            return f"Không tìm thấy thông tin về cuốn sách '{book_title}' trong thư viện."
        
        real_title = match.iloc[0]['book_title']
        available = match.iloc[0]['available_copies']
        total = match.iloc[0]['total_copies']
        
        if available > 0:
            return f"Cuốn '{real_title}' hiện đang CÓ SẴN ({int(available)}/{int(total)} cuốn)."
        else:
            return f"Cuốn '{real_title}' hiện ĐÃ HẾT (Đang cho mượn {int(total)}/{int(total)} cuốn)."
            
    except FileNotFoundError:
        return "System Error: Không tìm thấy file dữ liệu CSV."
    except Exception as e:
        return f"System Error: Lỗi tra cứu sách - {str(e)}"


def get_book_content(book_title) -> str:
    """TC4: Lấy tóm tắt nội dung sách (Cột description_short)"""
    try:
        # Xử lý lỗi unhashable type: 'dict'
        book_title = parse_input(book_title)
        
        df = pd.read_csv(BOOKS_PATH)
        match = df[df['book_title'].str.contains(book_title, case=False, na=False)]
        
        if match.empty:
            return f"Không tìm thấy dữ liệu nội dung cho sách '{book_title}'."
            
        real_title = match.iloc[0]['book_title']
        desc = match.iloc[0]['description_short']
        return f"Nội dung tóm tắt của '{real_title}': {desc}"
        
    except Exception as e:
        return f"System Error: Lỗi lấy nội dung sách - {str(e)}"


def filter_by_author(author_name) -> str:
    """TC5: Thống kê và liệt kê đầu sách của một tác giả"""
    try:
        # Xử lý lỗi unhashable type: 'dict'
        author_name = parse_input(author_name)
        
        df = pd.read_csv(BOOKS_PATH)
        match = df[df['author'].str.contains(author_name, case=False, na=False)]
        
        if match.empty:
            return f"Thư viện hiện không có cuốn sách nào của tác giả '{author_name}'."
            
        count = len(match)
        titles = match['book_title'].unique()
        titles_str = ", ".join(titles)
        
        return f"Tác giả '{author_name}' có {count} đầu sách. Bao gồm: {titles_str}."
        
    except Exception as e:
        return f"System Error: Lỗi lọc tác giả - {str(e)}"

TOOLS = {
    # "Get_Popular_Books": get_popular_books,
    "Search_Book_Status": search_book_status,
    # "Get_User_Ledger": get_user_ledger,
    "Get_Book_Content": get_book_content,
    "Filter_By_Author": filter_by_author
}
import json
from src.telemetry.logger import system_logger, log_function_call

@log_function_call
def get_popular_books(args):
    # TC1: Trả về dữ liệu JSON
    return json.dumps([{"title": "Đắc Nhân Tâm", "borrows": 120}, {"title": "Sapiens", "borrows": 95}])
@log_function_call
def search_book_status(args):
    # TC2: Nhận {'title': '...'} và kiểm tra
    title = args.get('title', '')
    return json.dumps({"title": title, "available": 2, "location": "Kệ A3"})
@log_function_call
def get_user_ledger(args):
    # TC3: Check sách mượn
    user_id = args.get('user_id')
    return json.dumps({"user_id": user_id, "borrowed": ["Sapiens"], "fine": 0})
@log_function_call
def get_book_content(args):
    # TC4: Lấy mô tả tóm tắt
    return json.dumps({"title": args.get('title'), "summary": "Lịch sử tiến hóa của loài người..."})
@log_function_call
def filter_by_author(args):
    # TC5: Thống kê tác giả
    raise Exception("Lỗi giả định: Cơ sở dữ liệu bị lỗi")  # Mô phỏng lỗi để kiểm tra error handling
    return json.dumps({"author": args.get('author'), "books": ["Tôi thấy hoa vàng trên cỏ xanh", "Kính Vạn Hoa"]})

# Mapping tool name từ LLM sang function thực tế
TOOLS = {
    "Get_Popular_Books": get_popular_books,
    "Search_Book_Status": search_book_status,
    "Get_User_Ledger": get_user_ledger,
    "Get_Book_Content": get_book_content,
    "Filter_By_Author": filter_by_author
}
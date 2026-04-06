import json
import pandas as pd
import os
from src.telemetry.logger import log_function_call


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BOOKS_PATH = os.path.join(BASE_DIR, 'db', 'library_mock_data', 'books.csv')
FLAT_PATH = os.path.join(
    BASE_DIR, 'db', 'library_mock_data', 'library_chatbot_flat.csv')
BORROWINGS_PATH = os.path.join(
    BASE_DIR, 'db', 'library_mock_data', 'borrowings.csv')

@log_function_call
def parse_input(input_data) -> str:
    """
    Xử lý dữ liệu đầu vào. Nếu Agent truyền vào một dictionary (ví dụ: {'title': '...'}),
    hàm sẽ bóc tách lấy giá trị đầu tiên. Nếu là string thì giữ nguyên.
    """
    if isinstance(input_data, dict):
        # Lấy giá trị đầu tiên tìm thấy trong dict (thường là key 'title', 'book_title'...)
        return str(next(iter(input_data.values())))
    return str(input_data)


@log_function_call
def get_popular_books(args) -> str:
    """TC1: Lấy danh sách 10 cuốn sách được mượn nhiều nhất."""
    try:
        df = pd.read_csv(BOOKS_PATH)
        # Tính số lần mượn: borrows = tổng số bản - số bản đang còn trên kệ
        df['borrows'] = df['total_copies'] - df['available_copies']

        # Sắp xếp giảm dần theo lượt mượn và lấy Top 10
        top_books = df.nlargest(10, 'borrows')[
            ['book_title', 'borrows']].to_dict('records')

        result = [
            {"title": book['book_title'], "borrows": int(book['borrows'])}
            for book in top_books
        ]
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return f"System Error: Lỗi lấy danh sách sách phổ biến - {str(e)}"

@log_function_call
def search_book_status(book_title) -> str:
    """TC2: Kiểm tra tình trạng sách (Còn hay hết)."""
    try:
        book_title = parse_input(book_title)
        df = pd.read_csv(FLAT_PATH)

        # Tìm kiếm không phân biệt hoa thường
        match = df[df['book_title'].str.contains(
            book_title, case=False, na=False)]

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
        return f"System Error: Lỗi tra cứu trạng thái sách - {str(e)}"

@log_function_call
def get_user_ledger(args) -> str:
    """TC3: Kiểm tra danh sách sách đang mượn của một sinh viên."""
    try:
        user_id = args.get('user_id') if isinstance(args, dict) else args
        if not user_id:
            return "System Error: Cần cung cấp user_id."

        df = pd.read_csv(FLAT_PATH)
        # Lọc theo student_id và trạng thái là đang mượn
        user_books = df[(df['student_id'] == user_id) &
                        (df['status'] == 'borrowed')]

        if user_books.empty:
            return json.dumps({"user_id": user_id, "borrowed": [], "fine": 0}, ensure_ascii=False)

        borrowed_titles = user_books['book_title'].unique().tolist()
        result = {
            "user_id": user_id,
            "borrowed": borrowed_titles,
            "fine": 0  # Mặc định fine = 0 theo cấu trúc hiện tại
        }
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return f"System Error: Lỗi tra cứu sổ mượn của sinh viên - {str(e)}"

@log_function_call
def get_book_content(book_title) -> str:
    """TC4: Lấy tóm tắt nội dung của sách."""
    try:
        book_title = parse_input(book_title)
        df = pd.read_csv(BOOKS_PATH)

        match = df[df['book_title'].str.contains(
            book_title, case=False, na=False)]

        if match.empty:
            return f"Không tìm thấy dữ liệu nội dung cho sách '{book_title}'."

        real_title = match.iloc[0]['book_title']
        desc = match.iloc[0]['description_short']
        return f"Nội dung tóm tắt của '{real_title}': {desc}"

    except Exception as e:
        return f"System Error: Lỗi lấy nội dung sách - {str(e)}"

@log_function_call
def filter_by_author(author_name) -> str:
    """TC5: Thống kê và liệt kê các đầu sách của một tác giả."""
    try:
        author_name = parse_input(author_name)
        df = pd.read_csv(BOOKS_PATH)

        match = df[df['author'].str.contains(
            author_name, case=False, na=False)]

        if match.empty:
            return f"Thư viện hiện không có cuốn sách nào của tác giả '{author_name}'."

        count = len(match)
        titles = match['book_title'].unique()
        titles_str = ", ".join(titles)

        return f"Tác giả '{author_name}' có {count} đầu sách. Bao gồm: {titles_str}."

    except Exception as e:
        return f"System Error: Lỗi lọc theo tác giả - {str(e)}"


TOOLS = {
    "Get_Popular_Books": get_popular_books,
    "Search_Book_Status": search_book_status,
    "Get_User_Ledger": get_user_ledger,
    "Get_Book_Content": get_book_content,
    "Filter_By_Author": filter_by_author
}

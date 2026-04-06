import pandas as pd
import os

# --- CẤU HÌNH ĐƯỜNG DẪN  ---

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# Trỏ vào thư mục chứa data
BOOKS_PATH = os.path.join(BASE_DIR, 'db', 'library_mock_data', 'books.csv')
FLAT_PATH = os.path.join(BASE_DIR, 'db', 'library_mock_data', 'library_chatbot_flat.csv')

# =====================================================================
# 3 TOOL DÀNH CHO AGENT
# =====================================================================

def search_book_status(book_title: str) -> str:
    """TC2: Kiểm tra tính sẵn có của sách (Còn trên kệ hay đã mượn hết)"""
    try:
        df = pd.read_csv(FLAT_PATH)
        # Tìm kiếm gần đúng không phân biệt hoa thường
        match = df[df['book_title'].str.contains(book_title, case=False, na=False)]
        
        if match.empty:
            return f"Không tìm thấy thông tin về cuốn sách '{book_title}' trong thư viện."
        
        # Lấy thông tin từ dòng đầu tiên tìm thấy
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


def get_book_content(book_title: str) -> str:
    """TC4: Lấy tóm tắt nội dung sách (Cột description_short)"""
    try:
        df = pd.read_csv(BOOKS_PATH)
        match = df[df['book_title'].str.contains(book_title, case=False, na=False)]
        
        if match.empty:
            return f"Không tìm thấy dữ liệu nội dung cho sách '{book_title}'."
            
        real_title = match.iloc[0]['book_title']
        desc = match.iloc[0]['description_short']
        return f"Nội dung tóm tắt của '{real_title}': {desc}"
        
    except Exception as e:
        return f"System Error: Lỗi lấy nội dung sách - {str(e)}"


def filter_by_author(author_name: str) -> str:
    """TC5: Thống kê và liệt kê đầu sách của một tác giả"""
    try:
        df = pd.read_csv(BOOKS_PATH)
        match = df[df['author'].str.contains(author_name, case=False, na=False)]
        
        if match.empty:
            # Dòng này rất quan trọng để Agent biết đường kích hoạt Fallback (báo CSKH)
            return f"Thư viện hiện không có cuốn sách nào của tác giả '{author_name}'."
            
        count = len(match)
        # Lọc lấy tên sách duy nhất
        titles = match['book_title'].unique()
        titles_str = ", ".join(titles)
        
        return f"Tác giả '{author_name}' có {count} đầu sách. Bao gồm: {titles_str}."
        
    except Exception as e:
        return f"System Error: Lỗi lọc tác giả - {str(e)}"


# =====================================================================
# TEST CHẠY THỬ (Sẽ không chạy khi file này được import ở nơi khác)
# =====================================================================
if __name__ == "__main__":
    print("--- CHẠY THỬ TOOL ---")
    print(search_book_status("MLOps"))
    print("-" * 20)
    print(get_book_content("System Reliability"))
    print("-" * 20)
    print(filter_by_author("Nam Clark"))
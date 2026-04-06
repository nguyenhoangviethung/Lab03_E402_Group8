import os
import google.generativeai as genai
from dotenv import load_dotenv

# Tải biến môi trường từ file .env (nếu có)
load_dotenv()

# Lấy API key từ biến môi trường
api_key = os.environ.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    # Khởi tạo mô hình. Có thể thay bằng gemini-1.5-flash hoặc gemini-1.5-pro
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None
    print("Warning: Không tìm thấy GEMINI_API_KEY. Vui lòng thiết lập biến môi trường này.")

def get_response(prompt: str) -> str:
    """
    Hàm nền tảng để giao tiếp với Gemini.
    Nhận vào prompt và trả về kết quả dạng text.
    Đây là "nguồn sống" cho cả Agent (TV1) và Baseline (TV3).
    """
    if not model:
        return "Lỗi: Chưa cấu hình GEMINI_API_KEY. Không thể gọi API."
        
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Đã xảy ra lỗi khi gọi Gemini API: {e}"

if __name__ == "__main__":
    # Test nhanh xem hàm get_response có trả về chữ hay không
    print("Đang test kết nối Gemini...")
    kết_quả = get_response("Chào bạn, bạn có thể nghe tôi nói không?")
    print("Kết quả:", kết_quả)

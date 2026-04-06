import sys, json
from tools import get_popular_books, get_user_ledger, get_book_content, search_book_status

# Test get_popular_books
result1 = get_popular_books({})
print(json.loads(result1))

# Test get_user_ledger
result2 = get_user_ledger({"user_id": "STU00061"})
print("Tets user ledger")
print(json.loads(result2))

result3 = get_book_content({"book_title": "MLOps"})
print("mo ta book")
print(result3)

result4 = search_book_status({"book_title": "Nam Clark"})
print("So luong sach")
print(result4)



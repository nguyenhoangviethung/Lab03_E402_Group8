import sys, json
from tools import get_popular_books, get_user_ledger

# Test get_popular_books
result1 = get_popular_books({})
print(json.loads(result1))

# Test get_user_ledger
result2 = get_user_ledger({"user_id": "STU00061"})
print(json.loads(result2))
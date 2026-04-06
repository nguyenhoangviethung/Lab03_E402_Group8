#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script for get_popular_books và get_user_ledger functions"""

import sys
import os
import json

# Thêm src vào path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools.tools import get_popular_books, get_user_ledger

def test_get_popular_books():
    """Test hàm get_popular_books"""
    print("=" * 60)
    print("TEST: get_popular_books(args)")
    print("=" * 60)
    
    result = get_popular_books({})
    print(f"Raw result: {result}\n")
    
    try:
        data = json.loads(result)
        print(f"Parsed result: {json.dumps(data, ensure_ascii=False, indent=2)}")
        print(f"\nTotal books: {len(data)}")
        if data:
            print(f"Top 1 book: {data[0]['title']} - {data[0]['borrows']} lần mượn")
    except Exception as e:
        print(f"Error parsing result: {e}")
    print()

def test_get_user_ledger():
    """Test hàm get_user_ledger"""
    print("=" * 60)
    print("TEST: get_user_ledger(args)")
    print("=" * 60)
    
    # Test với user_id STU00061 (từ borrowings.csv)
    test_user_id = "STU00061"
    print(f"Testing với user_id: {test_user_id}\n")
    
    result = get_user_ledger({"user_id": test_user_id})
    print(f"Raw result: {result}\n")
    
    try:
        data = json.loads(result)
        print(f"Parsed result: {json.dumps(data, ensure_ascii=False, indent=2)}")
        if data['borrowed']:
            print(f"\nSông sách đang mượn: {len(data['borrowed'])}")
            for book in data['borrowed']:
                print(f"  - {book}")
        else:
            print("\nKhông có sách nào đang mượn")
    except Exception as e:
        print(f"Error parsing result: {e}")
    print()
    
    # Test với user_id không tồn tại
    print("-" * 60)
    test_user_id_2 = "STU99999"
    print(f"Testing với user_id không tồn tại: {test_user_id_2}\n")
    
    result2 = get_user_ledger({"user_id": test_user_id_2})
    print(f"Raw result: {result2}\n")
    
    try:
        data2 = json.loads(result2)
        print(f"Parsed result: {json.dumps(data2, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"Error parsing result: {e}")
    print()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TESTING TOOLS FUNCTIONS")
    print("=" * 60 + "\n")
    
    test_get_popular_books()
    test_get_user_ledger()
    
    print("=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

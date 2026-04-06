#!/usr/bin/env python3
"""
Generate mock CSV data for a library chatbot demo.

Outputs:
- students.csv
- books.csv
- borrowings.csv
- library_chatbot_flat.csv

Why 4 files?
- books.csv: book metadata + inventory/availability
- borrowings.csv: borrowing transactions
- students.csv: user lookup
- library_chatbot_flat.csv: denormalized file for quick chatbot demos

The flat file contains the required columns requested by the user:
student_id, book_title, book_id, author, catogory, isbn,
borrowed_at, return_date, due_date, status

Extra helper columns are also included in books.csv to support demo features:
- description_short  -> for "introduce this book"
- total_copies / available_copies -> for "is book A still available?"
"""

from __future__ import annotations

import argparse
import csv
import random
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List


CATEGORY_TOPICS = {
    "Programming": [
        "Python", "Java", "C++", "Algorithms", "Clean Code", "APIs",
        "Testing", "Concurrency", "Git", "Backend Design"
    ],
    "Data Science": [
        "Data Analysis", "Statistics", "Feature Engineering", "EDA",
        "Forecasting", "Visualization", "Experimentation", "SQL Analytics"
    ],
    "AI": [
        "LLM Systems", "Prompt Engineering", "Computer Vision", "NLP",
        "Recommendation Systems", "Generative AI", "MLOps", "Deep Learning"
    ],
    "Database": [
        "PostgreSQL", "SQL Tuning", "Data Modeling", "Transactions",
        "Indexing", "Data Warehousing", "OLAP", "NoSQL"
    ],
    "Cloud": [
        "Docker", "Kubernetes", "AWS", "Azure", "CI/CD",
        "System Reliability", "Observability", "Serverless"
    ],
    "Cybersecurity": [
        "Network Security", "Threat Modeling", "Secure Coding", "IAM",
        "Web Security", "Incident Response", "Zero Trust", "Cryptography"
    ],
    "Business": [
        "Product Strategy", "Negotiation", "Leadership", "Operations",
        "Startup Finance", "Marketing", "Customer Research", "Decision Making"
    ],
    "Psychology": [
        "Habits", "Motivation", "Learning", "Communication",
        "Focus", "Behavior Change", "Creativity", "Memory"
    ],
    "History": [
        "Ancient Civilizations", "World Wars", "Maritime Trade", "Industrial Age",
        "Asian History", "European History", "Cultural Exchange", "Political Thought"
    ],
    "Novel": [
        "The Silent Harbor", "Moonlit Archive", "Whispering Streets", "Fading Lanterns",
        "The Last Compass", "Paper Boats", "Broken Hourglass", "Hidden Tides"
    ],
    "Education": [
        "Active Learning", "STEM Teaching", "Assessment Design", "Curriculum Planning",
        "Classroom Innovation", "Digital Learning", "Mentoring", "Study Skills"
    ],
}

TITLE_TEMPLATES = [
    "{topic} Essentials",
    "Practical {topic}",
    "Modern {topic}",
    "{topic} in Action",
    "Advanced {topic}",
    "Introduction to {topic}",
    "{topic}: Theory and Practice",
    "The {topic} Handbook",
]

DESCRIPTION_TEMPLATES = [
    "A concise introduction to {topic}, covering key concepts, examples, and practical applications in {category}.",
    "This book explains {topic} through simple explanations, case studies, and real-world scenarios for modern learners.",
    "An accessible guide to {topic} with hands-on ideas, foundational theory, and useful patterns for self-study.",
    "A practical overview of {topic}, designed to help readers build intuition and apply the material in realistic contexts.",
]

FIRST_NAMES = [
    "An", "Binh", "Chi", "Dung", "Giang", "Hai", "Hanh", "Hieu", "Hoang", "Huong",
    "Khanh", "Lan", "Linh", "Mai", "Minh", "Nam", "Ngoc", "Phuong", "Quang", "Son",
    "Tam", "Thanh", "Thao", "Trang", "Trung", "Tuan", "Van", "Vy", "Yen", "Long",
    "Alice", "Brian", "Clara", "Daniel", "Emma", "Felix", "Grace", "Hannah", "Ivy", "Jason",
    "Kevin", "Luna", "Mia", "Noah", "Olivia", "Peter", "Ryan", "Sophia", "Thomas", "Zoe",
]

LAST_NAMES = [
    "Nguyen", "Tran", "Le", "Pham", "Hoang", "Phan", "Vu", "Vo", "Dang", "Bui",
    "Do", "Ho", "Ngo", "Duong", "Ly", "Truong", "Mai", "Dinh", "Lam", "Chau",
    "Smith", "Johnson", "Brown", "Taylor", "Anderson", "Martin", "Clark", "Young", "Lee", "Walker",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate mock CSV data for a library chatbot demo.")
    parser.add_argument("--output-dir", default="./library_mock_data", help="Folder to save CSV files")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--students", type=int, default=200, help="Number of students")
    parser.add_argument("--authors", type=int, default=40, help="Number of authors")
    parser.add_argument("--books", type=int, default=150, help="Number of books")
    parser.add_argument("--borrowings", type=int, default=2500, help="Number of borrowing transactions")
    return parser.parse_args()


def iso(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.replace(microsecond=0).isoformat()


def random_datetime_between(start: datetime, end: datetime) -> datetime:
    delta_seconds = int((end - start).total_seconds())
    if delta_seconds <= 0:
        return start
    return start + timedelta(seconds=random.randint(0, delta_seconds))


def make_unique_names(count: int) -> List[str]:
    names = []
    used = set()
    while len(names) < count:
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        if name not in used:
            used.add(name)
            names.append(name)
    return names


def generate_students(num_students: int, now: datetime) -> List[Dict[str, str]]:
    names = make_unique_names(num_students)
    created_start = now - timedelta(days=900)
    students = []
    for idx, name in enumerate(names, start=1):
        students.append({
            "student_id": f"STU{idx:05d}",
            "student_name": name,
            "created_at": iso(random_datetime_between(created_start, now - timedelta(days=30))),
        })
    return students


def generate_authors(num_authors: int) -> List[str]:
    return make_unique_names(num_authors)


def generate_books(num_books: int, authors: List[str], now: datetime) -> List[Dict[str, str]]:
    books = []
    used_titles = set()
    categories = list(CATEGORY_TOPICS.keys())
    category_weights = [1.2, 1.2, 1.4, 1.0, 0.9, 0.8, 0.7, 0.7, 0.6, 0.8, 0.7]

    # Encourage some authors to have multiple books for author-based queries.
    author_weights = [1 / (1 + i * 0.08) for i in range(len(authors))]

    for idx in range(1, num_books + 1):
        category = random.choices(categories, weights=category_weights, k=1)[0]
        topic = random.choice(CATEGORY_TOPICS[category])
        title = random.choice(TITLE_TEMPLATES).format(topic=topic)

        # Ensure unique titles.
        if title in used_titles:
            title = f"{title} Vol. {random.randint(2, 9)}"
        while title in used_titles:
            title = f"{title} {random.randint(10, 99)}"
        used_titles.add(title)

        author = random.choices(authors, weights=author_weights, k=1)[0]
        total_copies = random.randint(2, 10)
        description = random.choice(DESCRIPTION_TEMPLATES).format(
            topic=topic,
            category=category.lower(),
        )

        isbn = "978" + "".join(str(random.randint(0, 9)) for _ in range(10))
        created_at = random_datetime_between(now - timedelta(days=1200), now - timedelta(days=20))

        books.append({
            "book_id": f"BOOK{idx:05d}",
            "book_title": title,
            "author": author,
            "category": category,
            "isbn": isbn,
            "description_short": description,
            "total_copies": total_copies,
            "available_copies": total_copies,  # updated later after active borrowings are generated
            "created_at": iso(created_at),
        })

    return books


def assign_popularity_weights(books: List[Dict[str, str]]) -> Dict[str, float]:
    # Make a few books clearly more popular so testcase 1 has meaningful output.
    shuffled = books[:]
    random.shuffle(shuffled)

    weights = {}
    for i, book in enumerate(shuffled, start=1):
        if i <= 10:
            weights[book["book_id"]] = 8.0 - (i * 0.35)
        elif i <= 30:
            weights[book["book_id"]] = 4.0 - (i - 10) * 0.08
        else:
            weights[book["book_id"]] = random.uniform(0.8, 2.2)
    return weights


def pick_book_id(book_ids: List[str], popularity_weights: Dict[str, float]) -> str:
    weights = [popularity_weights[book_id] for book_id in book_ids]
    return random.choices(book_ids, weights=weights, k=1)[0]


def generate_borrowings(
    students: List[Dict[str, str]],
    books: List[Dict[str, str]],
    total_borrowings: int,
    now: datetime,
) -> List[Dict[str, str]]:
    borrowings: List[Dict[str, str]] = []
    book_map = {b["book_id"]: b for b in books}
    book_ids = [b["book_id"] for b in books]
    student_ids = [s["student_id"] for s in students]
    popularity_weights = assign_popularity_weights(books)

    active_count_by_book = Counter()
    active_books_by_student = defaultdict(set)

    total_inventory = sum(int(b["total_copies"]) for b in books)
    target_active = min(max(total_inventory // 3, 120), total_borrowings // 3)
    target_overdue = max(int(target_active * 0.28), 25)
    target_borrowed = target_active - target_overdue

    borrowing_id_seq = 1

    def next_borrowing_id() -> str:
        nonlocal borrowing_id_seq
        bid = f"BRW{borrowing_id_seq:06d}"
        borrowing_id_seq += 1
        return bid

    # 1) Generate active borrowed records (not yet returned, not overdue).
    attempts = 0
    while target_borrowed > 0 and attempts < total_borrowings * 20:
        attempts += 1
        book_id = pick_book_id(book_ids, popularity_weights)
        book = book_map[book_id]
        if active_count_by_book[book_id] >= int(book["total_copies"]):
            continue

        student_id = random.choice(student_ids)
        # Avoid one student borrowing the same active book multiple times simultaneously.
        if book_id in active_books_by_student[student_id]:
            continue

        borrowed_at = random_datetime_between(now - timedelta(days=10), now - timedelta(days=1))
        due_date = borrowed_at + timedelta(days=random.randint(7, 21))
        if due_date <= now:
            continue

        borrowings.append({
            "borrowing_id": next_borrowing_id(),
            "student_id": student_id,
            "book_id": book_id,
            "borrowed_at": iso(borrowed_at),
            "due_date": iso(due_date),
            "return_date": "",
            "status": "borrowed",
        })
        active_count_by_book[book_id] += 1
        active_books_by_student[student_id].add(book_id)
        target_borrowed -= 1

    # 2) Generate active overdue records.
    attempts = 0
    while target_overdue > 0 and attempts < total_borrowings * 20:
        attempts += 1
        book_id = pick_book_id(book_ids, popularity_weights)
        book = book_map[book_id]
        if active_count_by_book[book_id] >= int(book["total_copies"]):
            continue

        student_id = random.choice(student_ids)
        if book_id in active_books_by_student[student_id]:
            continue

        borrowed_at = random_datetime_between(now - timedelta(days=45), now - timedelta(days=16))
        due_date = borrowed_at + timedelta(days=random.randint(7, 14))
        if due_date >= now:
            continue

        borrowings.append({
            "borrowing_id": next_borrowing_id(),
            "student_id": student_id,
            "book_id": book_id,
            "borrowed_at": iso(borrowed_at),
            "due_date": iso(due_date),
            "return_date": "",
            "status": "overdue",
        })
        active_count_by_book[book_id] += 1
        active_books_by_student[student_id].add(book_id)
        target_overdue -= 1

    # 3) Generate historical returned records.
    while len(borrowings) < total_borrowings:
        book_id = pick_book_id(book_ids, popularity_weights)
        student_id = random.choice(student_ids)

        borrowed_at = random_datetime_between(now - timedelta(days=540), now - timedelta(days=3))
        due_date = borrowed_at + timedelta(days=random.randint(7, 21))

        # Sometimes returned late to create realistic history.
        if random.random() < 0.18:
            return_date = due_date + timedelta(days=random.randint(1, 12))
        else:
            latest_return = min(now - timedelta(hours=1), due_date)
            return_date = random_datetime_between(borrowed_at + timedelta(days=1), latest_return)

        if return_date <= borrowed_at:
            return_date = borrowed_at + timedelta(days=1)

        borrowings.append({
            "borrowing_id": next_borrowing_id(),
            "student_id": student_id,
            "book_id": book_id,
            "borrowed_at": iso(borrowed_at),
            "due_date": iso(due_date),
            "return_date": iso(return_date),
            "status": "returned",
        })

    # Update availability.
    for book in books:
        total_copies = int(book["total_copies"])
        available = total_copies - active_count_by_book[book["book_id"]]
        book["available_copies"] = max(0, available)

    return borrowings


def build_flat_rows(
    books: List[Dict[str, str]],
    borrowings: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    book_map = {b["book_id"]: b for b in books}
    rows = []
    for br in borrowings:
        book = book_map[br["book_id"]]
        rows.append({
            # Required fields for demo/chatbot
            "student_id": br["student_id"],
            "book_title": book["book_title"],
            "book_id": book["book_id"],
            "author": book["author"],
            "catogory": book["category"],  # kept intentionally to match the user's requested field name
            "isbn": book["isbn"],
            "borrowed_at": br["borrowed_at"],
            "return_date": br["return_date"],
            "due_date": br["due_date"],
            "status": br["status"],
            # Helpful extra fields for better demos
            "description_short": book["description_short"],
            "total_copies": book["total_copies"],
            "available_copies": book["available_copies"],
            "borrowing_id": br["borrowing_id"],
        })
    return rows


def write_csv(path: Path, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize(books: List[Dict[str, str]], borrowings: List[Dict[str, str]]) -> str:
    status_counts = Counter(row["status"] for row in borrowings)
    top_books = Counter(row["book_id"] for row in borrowings).most_common(5)
    book_map = {b["book_id"]: b["book_title"] for b in books}
    top_books_str = ", ".join(f"{book_map[book_id]} ({count})" for book_id, count in top_books)
    unavailable_books = sum(1 for b in books if int(b["available_copies"]) == 0)

    return (
        f"Generated {len(books)} books, {len(borrowings)} borrowings. "
        f"Status distribution: returned={status_counts['returned']}, "
        f"borrowed={status_counts['borrowed']}, overdue={status_counts['overdue']}. "
        f"Books currently out of stock: {unavailable_books}. "
        f"Top borrowed books: {top_books_str}"
    )


def main() -> None:
    args = parse_args()
    random.seed(args.seed)

    now = datetime.now(timezone.utc).replace(microsecond=0)
    output_dir = Path(args.output_dir)

    students = generate_students(args.students, now)
    authors = generate_authors(args.authors)
    books = generate_books(args.books, authors, now)
    borrowings = generate_borrowings(students, books, args.borrowings, now)
    flat_rows = build_flat_rows(books, borrowings)

    write_csv(
        output_dir / "students.csv",
        students,
        ["student_id", "student_name", "created_at"],
    )
    write_csv(
        output_dir / "books.csv",
        books,
        [
            "book_id", "book_title", "author", "category", "isbn",
            "description_short", "total_copies", "available_copies", "created_at"
        ],
    )
    write_csv(
        output_dir / "borrowings.csv",
        borrowings,
        ["borrowing_id", "student_id", "book_id", "borrowed_at", "due_date", "return_date", "status"],
    )
    write_csv(
        output_dir / "library_chatbot_flat.csv",
        flat_rows,
        [
            "student_id", "book_title", "book_id", "author", "catogory", "isbn",
            "borrowed_at", "return_date", "due_date", "status",
            "description_short", "total_copies", "available_copies", "borrowing_id"
        ],
    )

    print(summarize(books, borrowings))
    print(f"Output directory: {output_dir.resolve()}")
    print("Recommended for demo: use books.csv + borrowings.csv for logic, library_chatbot_flat.csv for quick prompting.")


if __name__ == "__main__":
    main()

from app import app
from models import db, Progress

topics = [
    "Arrays",
    "Strings",
    "HashMap",
    "HashSet",
    "Stack",
    "Queue",
    "Linked List",
    "Binary Search",
    "Sorting",
    "Two Pointers",
    "Sliding Window",
    "Prefix Sum",
    "Recursion",
    "Backtracking",
    "Trees",
    "BST",
    "Heap",
    "Trie",
    "Graph",
    "DFS",
    "BFS",
    "Dynamic Programming",
    "Greedy",
    "Bit Manipulation",
    "Math",
    "Matrix",
    "Intervals",
    "Monotonic Stack",
    "Union Find",
    "Topological Sort",
    "Shortest Path",
    "Minimum Spanning Tree",
    "Segment Tree",
    "Fenwick Tree",
    "Binary Indexed Tree",
    "Deque",
    "Priority Queue",
    "Memoization",
    "Kadane Algorithm",
    "Fast Slow Pointer",
    "Merge Intervals",
    "KMP",
    "Rabin Karp",
    "Rolling Hash",
    "Meet in the Middle",
    "Game Theory",
    "Number Theory",
    "Combinatorics",
    "Geometry",
    "SQL Basics"
]

with app.app_context():

    Progress.query.delete()

    for topic in topics:
        db.session.add(
            Progress(
                user_id=1,
                topic=topic,
                completed=False
            )
        )

    db.session.commit()

print("Topics Added Successfully!")
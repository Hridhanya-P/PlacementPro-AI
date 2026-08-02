from app import app
from models import db, Progress

topics = [
    "Arrays",
    "Strings",
    "HashMap",
    "Linked List",
    "Stack",
    "Queue",
    "Tree",
    "Graph"
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
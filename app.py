from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import pdfplumber
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Progress, ResumeReport

app = Flask(__name__)
latest_report = {}
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "placementpro_secret"
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///database.db"
)

if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres://"):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config[
        "SQLALCHEMY_DATABASE_URI"
    ].replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]   

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            return redirect(url_for("dashboard"))

        return "Invalid Email or Password!"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        new_user = User(
            name=name,
            email=email,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()
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

        for topic in topics:
            db.session.add(
                Progress(
                    user_id=new_user.id,
                    topic=topic,
                    completed=False
                )
            )

        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():

    # If user is not logged in, redirect to login page
    if "user_id" not in session:
        return redirect(url_for("login"))

    completed = Progress.query.filter_by(
        user_id=session["user_id"],
        completed=True
    ).count()

    xp = completed * 100
    level = (xp // 500) + 1

    uploads = ResumeReport.query.filter_by(
        user_id=session["user_id"]
    ).count()

    reports = ResumeReport.query.filter_by(
        user_id=session["user_id"]
    ).all()

    if uploads > 0:
        average = sum(r.score for r in reports) // uploads
        best_ats = max(r.ats_score for r in reports)
    else:
        average = 0
        best_ats = 0

    return render_template(
        "dashboard.html",
        name=session["user_name"],
        completed=completed,
        xp=xp,
        level=level,
        uploads=uploads,
        average=average,
        best_ats=best_ats
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/progress")
def progress():

    if "user_name" not in session:
        return redirect(url_for("login"))

    topics = Progress.query.filter_by(user_id=session["user_id"]).all()

    return render_template(
        "progress.html",
        topics=topics
    )

@app.route("/complete/<int:id>")
def complete(id):

    topic = Progress.query.filter_by(
        id=id,
        user_id=session["user_id"]
    ).first_or_404()

    topic.completed = True

    db.session.commit()

    return redirect(url_for("progress"))

@app.route("/resume", methods=["GET", "POST"])
def resume():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        file = request.files["resume"]

        if file.filename == "":
            return "Please select a PDF."

        # Create uploads folder
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)

        file.save(filepath)

        try:
            text = ""

            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text

            text = text.upper()

            skills = {
                "Python": 8,
                "Java": 8,
                "C": 5,
                "C++": 5,
                "HTML": 4,
                "CSS": 4,
                "JavaScript": 6,
                "React": 8,
                "Flask": 8,
                "SQL": 8,
                "Git": 5,
                "GitHub": 6,
                "Figma": 5,
                "Machine Learning": 10,
                "Data Science": 10
            }

            score = 0
            analysis = []

            for skill, marks in skills.items():
                if skill.lower() in text.lower():
                    analysis.append(f"✅ {skill} Found (+{marks})")
                    score += marks
                else:
                    analysis.append(f"❌ {skill} Missing")

            sections = {
                "PROJECTS": 10,
                "INTERNSHIP": 10,
                "CERTIFICATIONS": 6,
                "EDUCATION": 8,
                "SKILLS": 8,
                "SUMMARY": 5
            }

            for section, marks in sections.items():
                if section in text.upper():
                    analysis.append(f"✅ {section.title()} Found (+{marks})")
                    score += marks
                else:
                    analysis.append(f"❌ {section.title()} Missing")

            if "github.com" in text.lower():
                analysis.append("✅ GitHub Profile Found (+6)")
                score += 6
            else:
                analysis.append("❌ GitHub Profile Missing")

            if "linkedin.com" in text.lower():
                analysis.append("✅ LinkedIn Profile Found (+6)")
                score += 6
            else:
                analysis.append("❌ LinkedIn Profile Missing")

            suggestions = []

            if "java" not in text.lower():
                suggestions.append("Learn Java.")

            if "react" not in text.lower():
                suggestions.append("Learn React.")

            if "javascript" not in text.lower():
                suggestions.append("Learn JavaScript.")

            if "sql" not in text.lower():
                suggestions.append("Add SQL.")

            if "github.com" not in text.lower():
                suggestions.append("Add GitHub profile.")

            if "linkedin.com" not in text.lower():
                suggestions.append("Add LinkedIn profile.")

            if "certifications" not in text.lower():
                suggestions.append("Add Certifications.")

            if "internship" not in text.lower():
                suggestions.append("Add Internship Experience.")

            max_score = 113   # Total possible marks

            score = int((score / max_score) * 100)

            if score > 100:
                score = 100

            ats_score = min(score + 5, 100)

            if score >= 90:
                strength = "Excellent"

            elif score >= 75:
                strength = "Good"

            elif score >= 60:
                strength = "Average"

            else:
                strength = "Needs Improvement"

            jobs = []

            if "python" in text.lower():
                jobs.append("Python Developer")

            if "html" in text.lower() or "css" in text.lower() or "javascript" in text.lower():
                jobs.append("Frontend Developer")

            if "flask" in text.lower():
                jobs.append("Backend Developer")

            if "figma" in text.lower():
                jobs.append("UI/UX Designer")

            if "machine learning" in text.lower():
                jobs.append("Machine Learning Engineer")

            if "data science" in text.lower():
                jobs.append("Data Analyst")

            global latest_report

            latest_report = {
                "score": score,
                "ats_score": ats_score,
                "strength": strength,
                "analysis": analysis,
                "suggestions": suggestions,
                "jobs": jobs
            }

            session["score"] = score
            session["ats_score"] = ats_score
            session["strength"] = strength
            session["analysis"] = analysis
            session["suggestions"] = suggestions
            session["jobs"] = jobs

            report = ResumeReport(
                user_id=session["user_id"],
                filename=file.filename,
                score=score,
                ats_score=ats_score,
                strength=strength
            )

            db.session.add(report)
            db.session.commit()

            return render_template(
                "analysis.html",
                analysis=analysis,
                score=score,
                ats_score=ats_score,
                strength=strength,
                suggestions=suggestions,
                jobs=jobs
            )

        except Exception as e:
            return f"❌ Error: {e}"

    return render_template("resume.html")

@app.route("/download_report")
def download_report():

    if "user_id" not in session:
        return redirect(url_for("login"))

    global latest_report

    pdf = SimpleDocTemplate("Resume_Report.pdf")

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>PlacementPro-AI Resume Report</b>", styles["Title"]))

    story.append(Paragraph(f"Resume Score: {latest_report['score']}/100", styles["Normal"]))

    story.append(Paragraph(f"ATS Score: {latest_report['ats_score']}/100", styles["Normal"]))

    story.append(Paragraph(f"Resume Strength: {latest_report['strength']}", styles["Normal"]))

    story.append(Paragraph("<br/><b>Analysis</b>", styles["Heading2"]))

    for item in latest_report["analysis"]:
        story.append(Paragraph(item, styles["Normal"]))

    story.append(Paragraph("<br/><b>Suggestions</b>", styles["Heading2"]))

    for item in latest_report["suggestions"]:
        story.append(Paragraph(item, styles["Normal"]))

    story.append(Paragraph("<br/><b>Recommended Jobs</b>", styles["Heading2"]))

    for item in latest_report["jobs"]:
        story.append(Paragraph(item, styles["Normal"]))

    pdf.build(story)

    return send_file(
        "Resume_Report.pdf",
        as_attachment=True
    )

@app.route("/resume_history")
def resume_history():

    if "user_id" not in session:
        return redirect(url_for("login"))

    reports = ResumeReport.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        ResumeReport.upload_date.desc()
    ).all()

    return render_template(
        "resume_history.html",
        reports=reports
    )

@app.route("/charts")
def charts():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "charts.html",
        score=session.get("score", 0),
        ats_score=session.get("ats_score", 0)
    )

if __name__ == "__main__":
    app.run(debug=True)
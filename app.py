import pdfplumber
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Progress

app = Flask(__name__)
app.secret_key = "placementpro_secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placementpro.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():

    completed = Progress.query.filter_by(completed=True).count()

    xp = completed * 100

    level = (xp // 500) + 1

    return render_template(
        "dashboard.html",
        xp=xp,
        level=level,
        completed=completed
    )

@app.route("/logout")
def logout():
    session.pop("user_name", None)
    return redirect(url_for("login"))

@app.route("/progress")
def progress():

    if "user_name" not in session:
        return redirect(url_for("login"))

    topics = Progress.query.filter_by(user_id=1).all()

    return render_template(
        "progress.html",
        topics=topics
    )

@app.route("/complete/<int:id>")
def complete(id):

    topic = Progress.query.get_or_404(id)

    topic.completed = True

    db.session.commit()

    return redirect(url_for("progress"))

@app.route("/resume", methods=["GET", "POST"])
def resume():

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

            analysis = []
            suggestions = []
            score = 0

            skills = [
                "PYTHON",
                "JAVA",
                "C",
                "C++",
                "HTML",
                "CSS",
                "JAVASCRIPT",
                "REACT",
                "FLASK",
                "SQL",
                "GIT",
                "GITHUB",
                "FIGMA",
                "MACHINE LEARNING",
                "DATA SCIENCE"
            ]

            sections = [
                "PROJECTS",
                "INTERNSHIP",
                "CERTIFICATIONS",
                "EDUCATION",
                "SKILLS",
                "SUMMARY"
            ]

            for section in sections:
                if section in text.upper():
                    analysis.append(f"✅ {section.title()} Section Found")
                    score += 5
                else:
                    analysis.append(f"❌ {section.title()} Section Missing")

            for skill in skills:

                if skill in text:
                    analysis.append(f"✅ {skill.title()} Found")
                    score += 5
                else:
                    analysis.append(f"❌ {skill.title()} Missing")
                    suggestions.append(f"Learn {skill.title()}.")

            if "PROJECT" in text:
                analysis.append("✅ Projects Section Found")
                score += 10
            else:
                analysis.append("❌ Projects Section Missing")
                suggestions.append("Add at least 2 projects.")

            if "INTERNSHIP" in text:
                analysis.append("✅ Internship Experience Found")
                score += 10
            else:
                analysis.append("❌ Internship Experience Missing")
                suggestions.append("Add internship experience.")

            if "CERTIFICATION" in text or "CERTIFICATIONS" in text:
                analysis.append("✅ Certifications Found")
                score += 10
            else:
                analysis.append("❌ Certifications Missing")
                suggestions.append("Add certifications.")

            if "GITHUB" in text:
                analysis.append("✅ GitHub Profile Mentioned")
            else:
                suggestions.append("Add GitHub profile link.")

            if "LINKEDIN" in text:
                analysis.append("✅ LinkedIn Profile Mentioned")
            else:
                suggestions.append("Add LinkedIn profile.")

            score = min(score, 100)

            return render_template(
                "analysis.html",
                analysis=analysis,
                score=score,
                suggestions=suggestions
            )

        except Exception as e:
            return f"❌ Error: {e}"

    return render_template("resume.html")

if __name__ == "__main__":
    app.run(debug=True)
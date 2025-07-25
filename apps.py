from flask import Flask, request, redirect, session, render_template, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import spacy
import os
import pdfkit

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ---------- Database ----------
db = mysql.connector.connect(
    host="localhost", user="root", password="123456", database="careerLift"
)
cursor = db.cursor()

# ---------- spaCy ----------
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# ---------- Auth ----------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/dashboard")
    return render_template("index.html")

@app.route("/signup", methods=["POST"])
def signup():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    if password != confirm_password:
        return "Passwords do not match."

    password_hash = generate_password_hash(password)

    try:
        cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                       (name, email, password_hash))
        db.commit()
        return redirect("/")
    except mysql.connector.errors.IntegrityError:
        return "Email already exists."

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    cursor.execute("SELECT id, name, password_hash FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user[2], password):
        session["user_id"] = user[0]
        session["user_name"] = user[1]
        return redirect("/dashboard")
    return "Invalid credentials"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- Dashboard ----------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    return render_template("Sdashboard.html", name=session.get("user_name"))

# ---------- Resume Analysis ----------
@app.route("/analyze", methods=["POST"])
def analyze_resume():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided."}), 400
    return jsonify({"message": "Resume analyzed."})

@app.route("/recommend", methods=["POST"])
def recommend_jobs():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided."}), 400
    return jsonify({"message": "Jobs recommended."})

# ---------- Resume Builder ----------
@app.route("/create_resume")
def create_resume():
    if "user_id" not in session:
        return redirect("/")
    return render_template("SresumeForm.html")

@app.route("/generate_resume", methods=["POST"])
def generate_resume():
    if "user_id" not in session:
        return redirect("/")
    data = {
        "name": request.form.get("name"),
        "email": request.form.get("email"),
        "education": request.form.get("education"),
        "skills": request.form.get("skills"),
        "experience": request.form.get("experience")
    }
    rendered = render_template("StemplateResume.html", **data)
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdf_path = os.path.join("resume_output.pdf")
    pdfkit.from_string(rendered, pdf_path, configuration=config)
    return send_file(pdf_path, as_attachment=True, download_name="resume.pdf")

# ---------- Template Editing ----------
@app.route("/edit_template")
def edit_template_home():
    return render_template("Schoose_template.html")

@app.route("/edit_template/<template_name>", methods=["GET", "POST"])
def edit_selected_template(template_name):
    if request.method == "POST":
        return render_template(
            f"filled_{template_name}.html",
            name=request.form.get("name"),
            email=request.form.get("email"),
            education=request.form.get("education"),
            experience=request.form.get("experience"),
            skills=request.form.get("skills")
        )
    return render_template(f"Seditable_{template_name}.html")

@app.route("/form_resume")
def form_resume():
    return render_template("SresumeForm.html")

# ---------- Main ----------
if __name__ == "__main__":
    app.run(debug=True)

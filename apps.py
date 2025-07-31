from flask import Flask, request, redirect, session, render_template, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import spacy
from io import BytesIO
from xhtml2pdf import pisa

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ---------- Database Config ----------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="careerLift"
)
cursor = db.cursor()

# ---------- spaCy NLP ----------
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# ---------- ROUTES ----------

# Home / About
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template('about.html')

# ---------- Auth ----------
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
    return "Invalid credentials."

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- Dashboard ----------
@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    user_id = session["user_id"]

    cursor.execute("SELECT COUNT(*) FROM applications WHERE user_id = %s", (user_id,))
    applications = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM saved_jobs WHERE user_id = %s", (user_id,))
    saved_jobs = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM interviews WHERE user_id = %s", (user_id,))
    interviews = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM user_skills WHERE user_id = %s", (user_id,))
    skills = cursor.fetchone()[0] or 0

    user_data = {
        'username': session.get('user_name'),
        'applications': applications,
        'interviews': interviews,
        'saved_jobs': saved_jobs,
        'skills': skills
    }

    return render_template('Gdashboard.html', **user_data)

# ---------- Resume Analyzer ----------
@app.route("/analyze", methods=["POST"])
def analyze_resume():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided."}), 400

    doc = nlp(text)
    skills = [ent.text for ent in doc.ents if ent.label_ == "SKILL"]

    return jsonify({"skills": skills})

@app.route("/recommend", methods=["POST"])
def recommend_jobs():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided."}), 400

    return jsonify({"message": "Recommended jobs based on your resume"})

# ---------- Resume Builder ----------
# Route to render the resume form
@app.route("/create_resume")
def create_resume():
    if "user_id" not in session:
        return redirect("/")
    return render_template("SresumeForm.html")

# Route to generate and return the PDF resume
@app.route("/generate_resume", methods=["POST"])
def generate_resume():
    if "user_id" not in session:
        return redirect("/")

    # Extract form data
    data = {
        "name": request.form.get("name", ""),
        "email": request.form.get("email", ""),
        "phone": request.form.get("phone", ""),
        "linkedin": request.form.get("linkedin", ""),
        "education": request.form.get("education", ""),
        "skills": request.form.get("skills", ""),
        "certifications": request.form.get("certifications", ""),
        "projects": request.form.get("projects", ""),
        "experience": request.form.get("experience", "")
    }

    # Render HTML with data
    html = render_template("StemplateResume.html", **data)

    # Convert HTML to PDF
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf)

    if pisa_status.err:
        return "PDF generation failed"

    pdf.seek(0)
    return send_file(pdf, as_attachment=True, download_name="resume.pdf", mimetype='application/pdf')

# Home route
@app.route("/")
def home():
    return redirect("/create_resume")


@app.route("/preview_resume", methods=["POST"])
def preview_resume():
    if "user_id" not in session:
        return redirect("/")

    data = {key: request.form.get(key, "") for key in [
        "name", "email", "phone", "linkedin",
        "education", "skills", "certifications",
        "projects", "experience"]
    }

    return render_template("StemplateResume.html", **data)

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

# ---------- Run App ----------
if __name__ == "__main__":
    app.run(debug=True)

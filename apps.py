from flask import Flask, request, redirect, session, render_template, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import spacy
from io import BytesIO
from xhtml2pdf import pisa
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import quote
import requests
from datetime import datetime, timezone

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ---------- COURSE SEARCH: MODEL AND DATA ----------


with open('job_skills_model.pkl', 'rb') as f:
    model_bundle = pickle.load(f)
model = model_bundle['model']
vectorizer = model_bundle['vectorizer']
mlb = model_bundle['mlb']

# Load Coursera data
df = pd.read_csv("coursera_courses.csv")
df['course_skills'] = df['course_skills'].fillna('')
df['course_title'] = df['course_title'].fillna('Unknown')
if 'difficulty_level' not in df.columns:
    df['difficulty_level'] = 'N/A'
if 'course_url' not in df.columns:
    df['course_url'] = ''

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['course_skills'])


def build_course_url(raw_url, course_title):
    if isinstance(raw_url, str) and raw_url.strip():
        if raw_url.startswith("http"):
            return raw_url
        else:
            return f"https://www.coursera.org{raw_url}"
    else:
        return f"https://www.google.com/search?q={quote(course_title)}+site:coursera.org"


def recommend_courses(user_skills, top_n=5):
    user_vec = tfidf.transform([user_skills])
    similarity_scores = cosine_similarity(user_vec, tfidf_matrix)
    top_indices = similarity_scores[0].argsort()[-top_n:][::-1]

    recs = []
    for idx in top_indices:
        course_title = df.iloc[idx]['course_title']
        course_url = build_course_url(df.iloc[idx]['course_url'], course_title)
        recs.append({
            "title": course_title,
            "url": course_url,
            "difficulty": df.iloc[idx]['course_difficulty']
        })
    return recs

#-----------------Jobs search------------------
def time_since_posted_adzuna(created_str):
    try:
        dt = datetime.strptime(created_str, '%Y-%m-%dT%H:%M:%SZ')
    except Exception:
        return "unknown time"
    dt = dt.replace(tzinfo=timezone.utc)
    return compute_time_ago(dt)

def time_since_posted_jooble(updated_str):
    if '.' in updated_str:
        date_part, frac = updated_str.split('.', 1)
        frac = ''.join([ch for ch in frac if ch.isdigit()])
        frac = frac[:6]
        cleaned_str = f"{date_part}.{frac}"
    else:
        cleaned_str = updated_str
    if not cleaned_str.endswith('Z'):
        cleaned_str += 'Z'
    dt_formats = [
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%Y-%m-%dT%H:%M:%SZ'
    ]
    for fmt in dt_formats:
        try:
            dt = datetime.strptime(cleaned_str, fmt)
            dt = dt.replace(tzinfo=timezone.utc)
            break
        except Exception:
            continue
    else:
        return "unknown time"
    return compute_time_ago(dt)

def compute_time_ago(dt):
    now = datetime.now(timezone.utc)
    diff = now - dt
    days = diff.days
    seconds = diff.seconds
    if days > 0:
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds >= 3600:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds >= 60:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "just now"

# Adzuna Credentials
APP_ID = "c47cc823"
APP_KEY = "57e574c31f9bde401faf3b2d9f16bc3b"

# Jooble Credentials
JOOBLE_API_KEY = "fc6aca45-9909-486a-b131-528e2f7232b9"
JOOBLE_URL = f"https://jooble.org/api/{JOOBLE_API_KEY}"

# ----------- New: Jobs route -----------
@app.route('/realtime_jobs', methods=["GET", "POST"])
def realtime_jobs():
    jobs = []
    query = ""
    location = ""
    if request.method == "POST":
        query = request.form.get("jobrole", "")
        location = request.form.get("location", "")

        # ADZUNA
        adzuna_jobs = []
        url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "results_per_page": 10,
            "what": query,
            "where": location
        }
        try:
            response = requests.get(url, params=params, timeout=6)
            if response.status_code == 200:
                for job in response.json().get("results", []):
                    adzuna_jobs.append({
                        "source": "adzuna",
                        "title": job.get("title", "Untitled"),
                        "company": job.get("company", {}).get("display_name", ""),
                        "location": job.get("location", {}).get("display_name", ""),
                        "link": job.get("redirect_url", "#"),
                        "time_ago": time_since_posted_adzuna(job.get("created", "")),
                    })
        except Exception as e:
            pass

        # JOOBLE
        jooble_jobs = []
        payload = {
            "keywords": query,
            "location": location,
            "page": 1,
            "ResultOnPage": 10
        }
        try:
            response = requests.post(JOOBLE_URL, json=payload, timeout=8)
            if response.status_code == 200:
                for job in response.json().get("jobs", []):
                    jooble_jobs.append({
                        "source": "jooble",
                        "title": job.get("title", "Untitled"),
                        "company": job.get("company", ""),
                        "location": job.get("location", ""),
                        "link": job.get("link", "#"),
                        "time_ago": time_since_posted_jooble(job.get("updated", "")),
                    })
        except Exception as e:
            pass

        jobs = adzuna_jobs + jooble_jobs

    return render_template("Ajobs.html", jobs=jobs, query=query, location=location)


# ---------- Database Config ----------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Azra@23oct",
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


#---------Search courses app route-------------------
@app.route('/search_courses', methods=['GET', 'POST'])
def search_courses():
    if request.method == 'POST':
        job_title = request.form.get('jobrole', '').strip().lower()
        if not job_title:
            prediction_text = '<span style="color:red;">Please enter a job role.</span>'
            courses = None
        else:
            # Predict skills
            X_in = vectorizer.transform([job_title])
            proba = model.predict_proba(X_in)[0]
            top5_idx = proba.argsort()[-5:][::-1]
            top5_skills = [mlb.classes_[i] for i in top5_idx]
            top5_probs = [proba[i] for i in top5_idx]
            skill_html_parts = [f"<span>{skill} ({score:.2f})</span>" for skill, score in zip(top5_skills, top5_probs)]
            skill_html = '<div class="skills-list">' + ', '.join(skill_html_parts) + '</div>'
            prediction_text = f"For <b>{job_title.title()}</b>, the top 5 predicted skills are:<br>{skill_html}"

            courses = recommend_courses(", ".join(top5_skills), top_n=6)
    else:
        prediction_text = ''
        courses = None

    # If using a base layout, extend it
    return render_template('Ajobskills.html', prediction_text=prediction_text, courses=courses)




# ---------- Run App ----------
if __name__ == "__main__":
    app.run(debug=True)

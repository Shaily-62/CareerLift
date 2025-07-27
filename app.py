from flask import Flask, render_template, request
import os
from utils.resume_parser import extract_skills_from_pdf
from utils.recommender import recommend_courses

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    if 'resume' in request.files:
        resume = request.files['resume']
        skills = extract_skills_from_pdf(resume)
        recommended = recommend_courses(skills)
        return render_template('recommendations.html', skills=skills, courses=recommended.to_dict(orient='records'))

    return "No file uploaded."

if __name__ == "__main__":
    app.run(debug=True)

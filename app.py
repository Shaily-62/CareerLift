from flask import Flask, request, redirect, session, render_template
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"

db = mysql.connector.connect(
    host="localhost", user="root", password="123456", database="careerLift"
)
cursor = db.cursor()

@app.route("/")
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template('about.html')

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
        return redirect("/")
    else:
        return "Invalid credentials"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")




if __name__ == "__main__":
    app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "student_management_secret"

# Database connection
def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create database and tables
def create_table():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL,
            year TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Login page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid username or password"

    return render_template("index.html")


# Dashboard
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    recent_students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC LIMIT 5"
    ).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_courses=12,
        total_teachers=20,
        students=recent_students
    )


# Display students
@app.route("/students")
def students():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    data = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    return render_template("students.html", students=data)


# Add student
@app.route("/add_student", methods=["POST"])
def add_student():
    if "user" not in session:
        return redirect(url_for("login"))

    name = request.form["name"]
    email = request.form["email"]
    course = request.form["course"]
    year = request.form["year"]

    conn = get_db()

    conn.execute("""
        INSERT INTO students (name, email, course, year)
        VALUES (?, ?, ?, ?)
    """, (name, email, course, year))

    conn.commit()
    conn.close()

    return redirect(url_for("students"))


# Delete student
@app.route("/delete_student/<int:id>")
def delete_student(id):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    conn.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("students"))


# Edit student
@app.route("/edit_student/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        course = request.form["course"]
        year = request.form["year"]

        conn.execute("""
            UPDATE students
            SET name=?, email=?, course=?, year=?
            WHERE id=?
        """, (name, email, course, year, id))

        conn.commit()
        conn.close()

        return redirect(url_for("students"))

    student = conn.execute(
        "SELECT * FROM students WHERE id=?", (id,)
    ).fetchone()

    conn.close()

    return render_template("edit_student.html", student=student)


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    create_table()
    app.run(debug=True)

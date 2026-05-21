# Developed by Sai Reddy
from flask import Flask, render_template, request
import re
import random
import string
import hashlib
import sqlite3

app = Flask(__name__)

common_passwords = ["123456", "password", "admin", "qwerty", "abc123"]

def suggest_password():
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for i in range(14))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_database():
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS used_passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            password_hash TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def is_password_reused(password):
    password_hash = hash_password(password)
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM used_passwords WHERE password_hash = ?", (password_hash,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_password(password):
    password_hash = hash_password(password)
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO used_passwords (password_hash) VALUES (?)", (password_hash,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def check_strength(password):
    score = 0
    suggestions = []

    if password.lower() in common_passwords:
        return "Very Weak", ["This is a common password"], 0

    if len(password) >= 8:
        score += 1
    else:
        suggestions.append("Use at least 8 characters")

    if len(password) >= 12:
        score += 1
    else:
        suggestions.append("Use 12 or more characters")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        suggestions.append("Add an uppercase letter")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        suggestions.append("Add a lowercase letter")

    if re.search(r"[0-9]", password):
        score += 1
    else:
        suggestions.append("Add a number")

    if re.search(r"[!@#$%^&*]", password):
        score += 1
    else:
        suggestions.append("Add a special symbol")

    if score <= 2:
        strength = "Weak"
    elif score <= 4:
        strength = "Medium"
    else:
        strength = "Strong"

    return strength, suggestions, score

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        password = request.form["password"]

        if is_password_reused(password):
            result = {
                "strength": "Weak",
                "score": 0,
                "suggestions": ["This password was already used before. Choose a new one."],
                "suggested_password": suggest_password(),
                "hashed_password": hash_password(password)
            }
        else:
            strength, suggestions, score = check_strength(password)
            save_password(password)

            result = {
                "strength": strength,
                "score": score,
                "suggestions": suggestions,
                "suggested_password": suggest_password(),
                "hashed_password": hash_password(password)
            }

    return render_template("index.html", result=result)

if __name__ == "__main__":
    create_database()
    app.run(debug=True)

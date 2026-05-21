# Developed by Sai Reddy
import re
import random
import string
import hashlib
import sqlite3
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

    cursor.execute(
        "SELECT * FROM used_passwords WHERE password_hash = ?",
        (password_hash,)
    )

    result = cursor.fetchone()
    conn.close()

    return result is not None

def save_password(password):
    password_hash = hash_password(password)

    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO used_passwords (password_hash) VALUES (?)",
            (password_hash,)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass

    conn.close()

create_database()

password = input("Enter your password: ")

if is_password_reused(password):
    print("\nPassword already used before. Choose a new password.")
    print("\nSuggested Strong Password:")
    print(suggest_password())
    exit()

score = 0
suggestions = []

if password.lower() in common_passwords:
    print("\nPassword Strength: Very Weak")
    print("Reason: This is a common password")

else:
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

    print("\nScore:", score)

    if score <= 2:
        strength = "Weak"
    elif score <= 4:
        strength = "Medium"
    else:
        strength = "Strong"

    print("Password Strength:", strength)

    print("\nSuggestions:")
    if suggestions:
        for s in suggestions:
            print("-", s)
    else:
        print("Your password is strong")

print("\nSuggested Strong Password:")
print(suggest_password())

print("\nHashed Password:")
print(hash_password(password))

save_password(password)
print("\nPassword hash saved successfully.")

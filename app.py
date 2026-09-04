from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from datetime import datetime
import random
import os

app = Flask(__name__)

app.secret_key = "geoshield-demo-secret-key"

DATABASE = "geoshield.db"


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            location TEXT NOT NULL,
            device TEXT NOT NULL,
            risk TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    # Demo user
    existing_user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        ("demo@geoshield.com",)
    ).fetchone()

    if not existing_user:
        conn.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            ("demo@geoshield.com", "demo123")
        )

    # Add initial demo events if database is empty
    count = conn.execute(
        "SELECT COUNT(*) FROM security_events"
    ).fetchone()[0]

    if count == 0:
        demo_events = [
            (
                "Normal Login",
                "Chennai, India",
                "Chrome / Windows",
                "Low"
            ),
            (
                "New Device Detected",
                "Bengaluru, India",
                "Android Phone",
                "High"
            ),
            (
                "Unusual Login Location",
                "Mumbai, India",
                "Unknown Device",
                "High"
            ),
            (
                "Password Changed",
                "Chennai, India",
                "Chrome / Windows",
                "Low"
            ),
            (
                "Multiple Failed Attempts",
                "Unknown",
                "Unknown Device",
                "High"
            )
        ]

        for event in demo_events:
            conn.execute("""
                INSERT INTO security_events
                (event_type, location, device, risk, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                event[0],
                event[1],
                event[2],
                event[3],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

    conn.commit()
    conn.close()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()

        conn.close()

        if user:
            session["user"] = email
            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid email or password"
        )

    return render_template("login.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        email=session["user"]
    )


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ---------------- GET EVENTS ----------------

@app.route("/api/events")
def get_events():

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()

    events = conn.execute("""
        SELECT *
        FROM security_events
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    result = []

    for event in events:
        result.append({
            "id": event["id"],
            "event_type": event["event_type"],
            "location": event["location"],
            "device": event["device"],
            "risk": event["risk"],
            "timestamp": event["timestamp"]
        })

    return jsonify(result)


# ---------------- ADD EVENT ----------------

@app.route("/api/add-event", methods=["POST"])
def add_event():

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    event_type = data.get("event_type", "Unknown Activity")
    location = data.get("location", "Unknown")
    device = data.get("device", "Unknown Device")
    risk = data.get("risk", "Low")

    conn = get_db()

    conn.execute("""
        INSERT INTO security_events
        (event_type, location, device, risk, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        event_type,
        location,
        device,
        risk,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Security event added"
    })


# ---------------- GENERATE DEMO EVENTS ----------------

@app.route("/api/demo-events", methods=["POST"])
def demo_events():

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    locations = [
        "Chennai, India",
        "Bengaluru, India",
        "Mumbai, India",
        "Delhi, India",
        "Hyderabad, India"
    ]

    devices = [
        "Chrome / Windows",
        "Android Phone",
        "iPhone",
        "Firefox / Windows",
        "Unknown Device"
    ]

    activities = [
        "Login Attempt",
        "New Device Detected",
        "Unusual Login Location",
        "Multiple Failed Attempts",
        "Security Setting Changed"
    ]

    risks = [
        "Low",
        "Medium",
        "High"
    ]

    conn = get_db()

    for i in range(3):

        conn.execute("""
            INSERT INTO security_events
            (event_type, location, device, risk, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            random.choice(activities),
            random.choice(locations),
            random.choice(devices),
            random.choice(risks),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Demo security events generated"
    })


# ---------------- LOCATION ----------------

@app.route("/api/location", methods=["POST"])
def save_location():

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is None or longitude is None:
        return jsonify({
            "error": "Location data missing"
        }), 400

    conn = get_db()

    conn.execute("""
        INSERT INTO security_events
        (event_type, location, device, risk, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "Authorized Location Shared",
        f"{latitude:.5f}, {longitude:.5f}",
        "User Browser",
        "Low",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "latitude": latitude,
        "longitude": longitude
    })


# ---------------- START APP ----------------

if __name__ == "__main__":
    init_db()

    print("\n===================================")
    print("        GEOSHIELD SECURITY APP")
    print("===================================")
    print("Demo Login:")
    print("Email: demo@geoshield.com")
    print("Password: demo123")
    print("===================================\n")

    app.run(debug=True)
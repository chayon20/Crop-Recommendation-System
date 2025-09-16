import os
import sqlite3
import pickle
from datetime import datetime, timedelta

import pytz
from flask import (
    Flask, request, jsonify, render_template,
    redirect, url_for, flash, session, send_from_directory
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from functools import wraps

# ---------------------------
# Flask setup
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = "replace-with-a-secret-key"
app.permanent_session_lifetime = timedelta(days=7)

# ---------------------------
# Database setup
# ---------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
db = SQLAlchemy(app)

# Sensor DB (raw sqlite)
DB_FILE = "crop_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            N REAL,
            P REAL,
            K REAL,
            temperature REAL,
            humidity REAL,
            ph REAL,
            rainfall REAL,
            predicted_crop TEXT,
            created_at TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------------------
# ML Model
# ---------------------------
with open("models/crop_model.pkl", "rb") as f:
    model = pickle.load(f)
with open("models/label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

# ---------------------------
# Mail setup
# ---------------------------
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME="",
    MAIL_PASSWORD="",
    MAIL_DEFAULT_SENDER=""
)

mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

# ---------------------------
# User model
# ---------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(300))
    occupation = db.Column(db.String(120))
    profile_photo = db.Column(db.String(300))
    password_hash = db.Column(db.String(300))
    is_verified = db.Column(db.Boolean, default=False)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

with app.app_context():
    db.create_all()

# ---------------------------
# Auth helpers
# ---------------------------
def login_user(user):
    session.permanent = True
    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_email"] = user.email
    session["user_photo"] = user.profile_photo

def logout_user():
    session.clear()

def current_user():
    uid = session.get("user_id")
    if uid:
        return User.query.get(uid)
    return None

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user():
            flash("Login required.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ---------------------------
# Routes
# ---------------------------
@app.route("/")
def home():
    return render_template("home.html", user=current_user())

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user())

# ---------- Register ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        address = request.form.get("address", "").strip()
        occupation = request.form.get("occupation", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not all([name, email, password, confirm]):
            flash("Please fill all required fields", "error")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match", "error")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please login.", "error")
            return redirect(url_for("login"))

        file = request.files.get("profile_photo")
        filename = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        new_user = User(
            name=name,
            email=email,
            address=address,
            occupation=occupation,
            profile_photo=filename,
            password_hash=generate_password_hash(password),
            is_verified=False,
        )
        db.session.add(new_user)
        db.session.commit()

        # Send verification email
        token = s.dumps(email, salt="email-confirm")
        link = url_for("verify_email", token=token, _external=True)
        msg = Message("Verify Your Email", recipients=[email])
        msg.body = f"Hi {name},\n\nClick to verify your account:\n{link}\n\nThanks!"
        mail.send(msg)

        flash("Registration successful! Check your email to verify.", "info")
        return redirect(url_for("login"))
    return render_template("register.html", user=current_user())

# ---------- Verify ----------
@app.route("/verify/<token>")
def verify_email(token):
    try:
        email = s.loads(token, salt="email-confirm", max_age=3600)
    except SignatureExpired:
        flash("Verification link expired!", "error")
        return redirect(url_for("login"))
    except BadSignature:
        flash("Invalid verification link!", "error")
        return redirect(url_for("login"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found!", "error")
        return redirect(url_for("register"))

    if user.is_verified:
        flash("Email already verified. Please login.", "info")
    else:
        user.is_verified = True
        db.session.commit()
        flash("Email verified! You can now login.", "success")

    return redirect(url_for("login"))

# ---------- Login ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No account found. Please register.", "error")
            return redirect(url_for("register"))
        if not user.check_password(password):
            flash("Password incorrect.", "error")
            return redirect(url_for("login"))
        if not user.is_verified:
            flash("Please verify your email before logging in.", "warning")
            return redirect(url_for("login"))

        login_user(user)
        flash("Logged in successfully.", "success")
        return redirect(url_for("home"))
    return render_template("login.html", user=current_user())

# ---------- Logout ----------
@app.route("/logout")
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("home"))

# ---------- Profile ----------
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user())

# ---------- Sensor API ----------
@app.route("/sensor", methods=["POST"])
def sensor_post():
    data = request.get_json()
    try:
        features = [
            float(data["N"]),
            float(data["P"]),
            float(data["K"]),
            float(data["temperature"]),
            float(data["humidity"]),
            float(data["ph"]),
            float(data["rainfall"])
        ]
    except Exception as e:
        return jsonify({"error": f"Invalid input: {e}"}), 400

    prediction = model.predict([features])[0]
    crop_name = label_encoder.inverse_transform([prediction])[0]

    # Bangladesh timezone
    bangladesh_tz = pytz.timezone('Asia/Dhaka')
    current_time = datetime.now(bangladesh_tz)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO sensor_data (N,P,K,temperature,humidity,ph,rainfall,predicted_crop,created_at)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (*features, crop_name, current_time))
    conn.commit()
    conn.close()

    return jsonify({"predicted_crop": crop_name})

@app.route("/api/latest")
def api_latest():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM sensor_data ORDER BY id DESC LIMIT 50")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    user = current_user()

    if request.method == "POST":
        # Get form data
        name = request.form.get("name", "").strip()
        address = request.form.get("address", "").strip()
        occupation = request.form.get("occupation", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm_password", "").strip()

        # Update basic fields
        user.name = name
        user.address = address
        user.occupation = occupation

        # Update password if provided
        if password:
            if password != confirm:
                flash("Passwords do not match.", "error")
                return redirect(url_for("edit_profile"))
            user.password_hash = generate_password_hash(password)

        # Update profile photo if uploaded
        file = request.files.get("profile_photo")
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            user.profile_photo = filename

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    return render_template("edit_profile.html", user=user)

# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

import os
import json
import random
import qrcode
import uuid

from flask import Flask, render_template, request, redirect, url_for, session,send_from_directory
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

app.secret_key = "lifetag-secret-key"

USERS_FILE = os.path.join(BASE_DIR, "users.json")
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXT = {"pdf", "png", "jpg", "jpeg"}


# =============================
# USERS
# =============================
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def user_exists(username):
    return any(u["username"] == username for u in load_users())


def get_user(username, password, role):
    for u in load_users():
        if (
            u["username"] == username
            and u["password"] == password
            and u["role"] == role
        ):
            return u
    return None


# =============================
# PROFILE STORAGE
# =============================
def profile_file(username):
    return os.path.join(DATA_DIR, f"profile_{username}.json")


def load_profile(username):
    path = profile_file(username)

    if not os.path.exists(path):
        return {
            "username": username,
            "lifetag_id": f"LT-{username.upper()}-001",
            "blood_group": "",
            "allergy": "",
            "conditions": "",
            "emergency_contact_name": "",
            "emergency_contact_phone": "",
            "emergency_numbers": ["108", "112"],
        }

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(username, data):
    with open(profile_file(username), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# =============================
# PRIVACY
# =============================
def privacy_file(username):
    return os.path.join(DATA_DIR, f"privacy_{username}.json")


def load_privacy(username):
    path = privacy_file(username)
    if not os.path.exists(path):
        return {
            "blood_group": True,
            "allergy": True,
            "conditions": True,
            "emergency_contact": True,
            "emergency_numbers": True,
        }
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_privacy(username, settings):
    with open(privacy_file(username), "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


# =============================
# QR GENERATION
# =============================
def generate_qr(profile):
    settings = load_privacy(profile["username"])

    payload = {"LifeTagID": profile["lifetag_id"]}

    if settings["blood_group"]:
        payload["BloodGroup"] = profile["blood_group"]

    if settings["allergy"]:
        payload["Allergy"] = profile["allergy"]

    if settings["conditions"]:
        payload["Conditions"] = profile["conditions"]

    if settings["emergency_contact"]:
        payload["EmergencyContact"] = {
            "name": profile["emergency_contact_name"],
            "phone": profile["emergency_contact_phone"],
        }

    if settings["emergency_numbers"]:
        payload["EmergencyNumbers"] = profile["emergency_numbers"]

    qr_folder = os.path.join(app.static_folder, "qr_codes")
    os.makedirs(qr_folder, exist_ok=True)

    filename = f"{profile['lifetag_id']}.png"
    full_path = os.path.join(qr_folder, filename)

    img = qrcode.make(json.dumps(payload))
    img.save(full_path)

    return f"qr_codes/{filename}"


# =============================
# UPLOAD
# =============================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def user_upload_folder(username):
    folder = os.path.join(UPLOAD_DIR, username)
    os.makedirs(folder, exist_ok=True)
    return folder

# =============================
# APPOINTMENTS
# =============================
APPOINT_FILE = os.path.join(BASE_DIR, "appointments.json")

def load_appointments():
    if not os.path.exists(APPOINT_FILE):
        return []
    with open(APPOINT_FILE, "r") as f:
        return json.load(f)

def save_appointments(data):
    with open(APPOINT_FILE, "w") as f:
        json.dump(data, f, indent=2)


# =============================
# ROUTES
# =============================
@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].lower().strip()
        password = request.form["password"]
        role = request.form.get("role", "patient")

        if user_exists(username):
            return render_template("auth/signup.html", error="Username exists")

        users = load_users()
        users.append({"username": username, "password": password, "role": role})
        save_users(users)

        return redirect(url_for("login"))

    return render_template("auth/signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].lower().strip()
        password = request.form["password"]
        role = request.form.get("role", "patient")

        user = get_user(username, password, role)

        if not user:
            return render_template("login.html", error="Invalid credentials")

        session.clear()
        session["username"] = username
        session["role"] = role

        if role == "doctor":
            return redirect(url_for("doctor_dashboard"))
        return redirect(url_for("patient_dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =============================
# DOCTOR
# =============================
@app.route("/doctor/dashboard")
def doctor_dashboard():
    if session.get("role") != "doctor":
        return redirect(url_for("login"))
    return render_template("doctor/dashboard.html")

@app.route("/doctor/appointments")
def doctor_appointments():
    if session.get("role") != "doctor":
        return redirect(url_for("login"))

    appointments = load_appointments()

    return render_template("doctor/appointments.html", appointments=appointments)


@app.route("/doctor/patient-search", methods=["GET", "POST"])
def doctor_patient_search():
    if session.get("role") != "doctor":
        return redirect(url_for("login"))

    result = None
    reports = []

    if request.method == "POST":
        lifetag_id = request.form.get("lifetag_id")

        for file in os.listdir(DATA_DIR):
            if file.startswith("profile_"):
                with open(os.path.join(DATA_DIR, file), "r") as f:
                    profile = json.load(f)

                    if profile.get("lifetag_id") == lifetag_id:
                        result = profile

                        # 🔥 IMPORTANT: username nikalo
                        username = profile.get("username")

                        # 🔥 reports fetch karo
                        folder = user_upload_folder(username)
                        reports = os.listdir(folder)

                        break

    return render_template(
        "doctor/patient_search.html",
        result=result,
        reports=reports
    )
@app.route("/doctor/update-appointment/<id>/<action>")
def update_appointment(id, action):
    if session.get("role") != "doctor":
        return redirect(url_for("login"))

    appointments = load_appointments()

    for a in appointments:
        if a["id"] == id:
            if action == "approve":
                a["status"] = "Approved"
            elif action == "reject":
                a["status"] = "Rejected"

    save_appointments(appointments)

    return redirect(url_for("doctor_appointments"))


# =============================
# PATIENT
# =============================
@app.route("/patient/dashboard")
def patient_dashboard():
    if session.get("role") != "patient":
        return redirect(url_for("login"))

    username = session.get("username")
    profile = load_profile(username)

    appointments = load_appointments()
    user_appointments = [a for a in appointments if a["patient"] == username]

    return render_template(
        "patient/dashboard.html",
        profile=profile,
        appointments=user_appointments
    )


@app.route("/patient/qr", methods=["GET", "POST"])
def patient_qr():
    if session.get("role") != "patient":
        return redirect(url_for("login"))

    username = session.get("username")
    profile = load_profile(username)

    if request.method == "POST":
        profile.update({
            "blood_group": request.form.get("blood_group"),
            "allergy": request.form.get("allergy"),
            "conditions": request.form.get("conditions"),
            "emergency_contact_name": request.form.get("contact_name"),
            "emergency_contact_phone": request.form.get("contact_phone"),
        })
        save_profile(username, profile)

    if not profile["blood_group"]:
        return render_template("patient/qr_form.html", profile=profile)

    qr_image = generate_qr(profile)

    return render_template(
        "patient/qr.html",
        profile=profile,
        qr_image_url=url_for("static", filename=qr_image),
    )


@app.route("/patient/privacy", methods=["GET", "POST"])
def patient_privacy():
    if session.get("role") != "patient":
        return redirect(url_for("login"))

    username = session.get("username")

    if request.method == "POST":
        settings = {
            "blood_group": bool(request.form.get("blood_group")),
            "allergy": bool(request.form.get("allergy")),
            "conditions": bool(request.form.get("conditions")),
            "emergency_contact": bool(request.form.get("emergency_contact")),
            "emergency_numbers": bool(request.form.get("emergency_numbers")),
        }
        save_privacy(username, settings)
        return redirect(url_for("patient_privacy"))

    settings = load_privacy(username)
    profile = load_profile(username)

    return render_template("patient/privacy.html", profile=profile, settings=settings)


@app.route("/patient/upload", methods=["GET", "POST"])
def patient_upload():
    if session.get("role") != "patient":
        return redirect(url_for("login"))

    username = session.get("username")
    folder = user_upload_folder(username)

    if request.method == "POST":
        file = request.files.get("report")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(folder, filename))

    files = sorted(os.listdir(folder))
    return render_template("patient/upload.html", files=files)

@app.route("/patient/book-appointment", methods=["GET", "POST"])
def book_appointment():
    if session.get("role") != "patient":
        return redirect(url_for("login"))

    username = session.get("username")
    profile = load_profile(username)

    if request.method == "POST":
        appointments = load_appointments()

        new_appointment = {
            "id": str(uuid.uuid4()),
            "patient": username,
            "lifetag_id": profile["lifetag_id"],
            "date": request.form.get("date"),
            "time": request.form.get("time"),
            "doctor": request.form.get("doctor"),
            "status": "Pending"
        }

        appointments.append(new_appointment)
        save_appointments(appointments)

        return redirect(url_for("patient_dashboard"))

    return render_template("patient/book_appointment.html")

@app.route("/patient/report/<filename>")
def patient_report(filename):
    if session.get("role") not in ["patient", "doctor"]:
        return redirect(url_for("login"))

    username = session.get("username")

    # 🔥 doctor case handle karo
    if session.get("role") == "doctor":
        username = request.args.get("user")

    folder = user_upload_folder(username)
    return send_from_directory(folder, filename)


@app.route("/offline-scan")
def offline_scan():
    return render_template("public/offline_scan.html")

@app.route("/api/vitals/<username>")
def get_vitals(username):
    data = {
        "heart_rate": random.randint(70, 110),
        "spo2": random.randint(95, 100),
        "bp": f"{random.randint(110,130)}/{random.randint(70,90)}"
    }
    return data


# =============================
# RUN
# =============================
if __name__ == "__main__":
    app.run(debug=True)

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, Response
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Patient, Doctor, TerraWebhookData
from . import db
from .terra_integration import get_user_trends, generate_widget_session, terra, _LOGGER
from .llm_chat import get_llm_response
from werkzeug.security import generate_password_hash
import json
from datetime import datetime

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return redirect(url_for("main.login"))


@main.route("/login")
def login():
    return render_template("login.html")


@main.route("/login/<user_type>", methods=["GET", "POST"])
def login_form(user_type):
    if user_type not in ["patient", "doctor"]:
        return redirect(url_for("main.login"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if (user_type == "patient" and not user.is_doctor) or (
                user_type == "doctor" and user.is_doctor
            ):
                login_user(user)
                flash("Logged in successfully.", "success")
                return redirect(
                    url_for(
                        "main.patient_dashboard"
                        if user_type == "patient"
                        else "main.doctor_dashboard"
                    )
                )
            else:
                flash("Invalid user type for this account", "error")
        else:
            flash("Invalid username or password", "error")

    return render_template("login_form.html", user_type=user_type)


@main.route("/signup/<user_type>", methods=["GET", "POST"])
def signup(user_type):
    if user_type not in ["patient", "doctor"]:
        return redirect(url_for("main.login"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Check if username or email already exists
        user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if user:
            flash("Username or email already exists", "error")
            return render_template("signup.html", user_type=user_type)

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("signup.html", user_type=user_type)

        # Create new user
        new_user = User(
            username=username, email=email, is_doctor=(user_type == "doctor")
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()

            # Create associated Patient or Doctor object
            if user_type == "patient":
                new_patient = Patient(user_id=new_user.id)
                db.session.add(new_patient)
            else:
                new_doctor = Doctor(user_id=new_user.id)
                db.session.add(new_doctor)
            db.session.commit()

            flash("Account created successfully. Please log in.", "success")
            return redirect(url_for("main.login_form", user_type=user_type))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred. Please try again.", "error")
            print(f"Error during signup: {str(e)}")  # Log the error for debugging

    return render_template("signup.html", user_type=user_type)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))


@main.route("/doctor/dashboard")
@login_required
def doctor_dashboard():
    if not current_user.is_doctor:
        return redirect(url_for("main.patient_dashboard"))
    patients = Patient.query.all()
    return render_template("doctor/dashboard.html", patients=patients)


@main.route("/doctor/patient/<int:patient_id>")
@login_required
def patient_info(patient_id):
    if not current_user.is_doctor:
        return redirect(url_for("main.patient_dashboard"))
    patient = Patient.query.get_or_404(patient_id)
    trends = get_user_trends(patient.terra_user_id)
    return render_template("doctor/patient_info.html", patient=patient, trends=trends)


@main.route("/patient/dashboard")
@login_required
def patient_dashboard():
    if current_user.is_doctor:
        return redirect(url_for("main.doctor_dashboard"))
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    trends = get_user_trends(patient.terra_user_id)
    return render_template("patient/dashboard.html", patient=patient, trends=trends)


@main.route("/patient/chat", methods=["GET", "POST"])
@login_required
def patient_chat():
    if current_user.is_doctor:
        return redirect(url_for("main.doctor_dashboard"))

    chat_history = []
    if request.method == "POST":
        user_input = request.form.get("user_input")
        response = get_llm_response(user_input)
        chat_history = request.form.get("chat_history", "[]")
        chat_history = eval(chat_history)  # Convert string to list
        chat_history.append({"user": user_input, "bot": response})

    return render_template("patient/chat.html", chat_history=chat_history)


@main.route("/patient_login", methods=["GET", "POST"])
def patient_login():
    # Implement patient login logic here
    flash("Patient login not yet implemented", "info")
    return redirect(url_for("main.login"))


@main.route("/doctor_login", methods=["GET", "POST"])
def doctor_login():
    # Implement doctor login logic here
    flash("Doctor login not yet implemented", "info")
    return redirect(url_for("main.login"))


@main.route("/patient/doctor_info")
@login_required
def patient_doctor_info():
    if current_user.is_doctor:
        return redirect(url_for("main.doctor_dashboard"))
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    return render_template("patient/doctor_info.html", doctor=patient.doctor)


@main.route("/doctor/edit_profile", methods=["GET", "POST"])
@login_required
def doctor_edit_profile():
    if not current_user.is_doctor:
        return redirect(url_for("main.patient_dashboard"))
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if request.method == "POST":
        doctor.specialization = request.form.get("specialization")
        doctor.bio = request.form.get("bio")
        doctor.office_address = request.form.get("office_address")
        doctor.phone_number = request.form.get("phone_number")
        doctor.license_number = request.form.get("license_number")
        doctor.education = request.form.get("education")
        doctor.years_of_experience = request.form.get("years_of_experience")
        db.session.commit()
        flash("Profile updated successfully", "success")
        return redirect(url_for("main.doctor_dashboard"))
    return render_template("doctor/edit_profile.html", doctor=doctor)


@main.route("/patient/edit_profile", methods=["GET", "POST"])
@login_required
def patient_edit_profile():
    if current_user.is_doctor:
        return redirect(url_for("main.doctor_dashboard"))
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if request.method == "POST":
        current_user.username = request.form.get("username")
        current_user.email = request.form.get("email")
        current_user.age = request.form.get("age")
        current_user.location = request.form.get("location")
        if request.form.get("password"):
            current_user.set_password(request.form.get("password"))
        patient.insurance_provider = request.form.get("insurance_provider")
        patient.insurance_policy_number = request.form.get("insurance_policy_number")
        db.session.commit()
        flash("Profile updated successfully", "success")
        return redirect(url_for("main.patient_dashboard"))
    return render_template("patient/edit_profile.html", patient=patient)


@main.route("/patient/generate_widget_url")
@login_required
def generate_widget_url():
    if current_user.is_doctor:
        return redirect(url_for("main.doctor_dashboard"))
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    widget_url = generate_widget_session(str(patient.id))
    return jsonify({"widget_url": widget_url})


@main.route("/consumeTerraWebhook", methods=["POST"])
def consume_terra_webhook():
    body = request.get_json()
    _LOGGER.info(
        "Received webhook for user %s of type %s",
        body.get("user", {}).get("user_id"),
        body["type"]
    )
    verified = terra.check_terra_signature(request.get_data().decode("utf-8"), request.headers.get('terra-signature', ''))
    
    if verified:
        try:
            # Store the webhook data
            webhook_data = TerraWebhookData(
                patient_id=body.get("user", {}).get("user_id"),
                webhook_type=body["type"],
                timestamp=datetime.utcnow(),
                data=json.dumps(body)
            )
            db.session.add(webhook_data)
            db.session.commit()
            
            # Process the data (you can implement this function based on your needs)
            process_terra_data(webhook_data)
            
            return Response(status=200)
        except Exception as e:
            _LOGGER.error(f"Error processing webhook: {str(e)}")
            db.session.rollback()
            return Response(status=500)
    else:
        return Response(status=403)

def process_terra_data(webhook_data):
    # Implement data processing logic here
    # This function should handle different types of data (sleep, activity, etc.)
    # and update the corresponding models (Sleep, Activity, HeartRate, etc.)
    pass

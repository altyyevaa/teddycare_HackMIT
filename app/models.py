from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_doctor = db.Column(db.Boolean, default=False)
    age = db.Column(db.Integer)
    location = db.Column(db.String(200))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False
    )
    user = db.relationship("User", backref=db.backref("patient", uselist=False))
    terra_user_id = db.Column(db.String(100), unique=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"))
    insurance_provider = db.Column(db.String(100))
    insurance_policy_number = db.Column(db.String(100))

    # Add other patient-specific fields


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False
    )
    user = db.relationship("User", backref=db.backref("doctor", uselist=False))
    specialization = db.Column(db.String(100))
    bio = db.Column(db.Text)
    office_address = db.Column(db.String(200))
    phone_number = db.Column(db.String(20))
    patients = db.relationship("Patient", backref="doctor", lazy="dynamic")
    license_number = db.Column(db.String(100))
    education = db.Column(db.Text)
    years_of_experience = db.Column(db.Integer)

    # Add other doctor-specific fields


# New models for Terra data


class TerraWebhookData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(100), nullable=False)  # Changed to String to match Terra user_id
    webhook_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data = db.Column(db.Text, nullable=False)  # Store JSON as text


class Sleep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer)  # in minutes
    efficiency = db.Column(db.Float)
    deep_sleep = db.Column(db.Integer)  # in minutes
    light_sleep = db.Column(db.Integer)  # in minutes
    rem_sleep = db.Column(db.Integer)  # in minutes


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    steps = db.Column(db.Integer)
    calories_burned = db.Column(db.Float)
    active_minutes = db.Column(db.Integer)


class HeartRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    bpm = db.Column(db.Integer, nullable=False)


# Add more models for other types of data as needed

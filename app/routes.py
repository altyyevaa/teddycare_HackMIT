from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Patient, Doctor
from . import db
from .terra_integration import get_user_trends
from .llm_chat import get_llm_response

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.is_doctor:
                return redirect(url_for('main.doctor_dashboard'))
            else:
                return redirect(url_for('main.patient_dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if not current_user.is_doctor:
        return redirect(url_for('main.patient_dashboard'))
    patients = Patient.query.all()
    return render_template('doctor/dashboard.html', patients=patients)

@main.route('/doctor/patient/<int:patient_id>')
@login_required
def patient_info(patient_id):
    if not current_user.is_doctor:
        return redirect(url_for('main.patient_dashboard'))
    patient = Patient.query.get_or_404(patient_id)
    trends = get_user_trends(patient.terra_user_id)
    return render_template('doctor/patient_info.html', patient=patient, trends=trends)

@main.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if current_user.is_doctor:
        return redirect(url_for('main.doctor_dashboard'))
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    trends = get_user_trends(patient.terra_user_id)
    return render_template('patient/dashboard.html', patient=patient, trends=trends)

@main.route('/patient/chat', methods=['GET', 'POST'])
@login_required
def patient_chat():
    if current_user.is_doctor:
        return redirect(url_for('main.doctor_dashboard'))
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        response = get_llm_response(user_input)
        return render_template('patient/chat.html', response=response)
    return render_template('patient/chat.html')
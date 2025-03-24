from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from forms import AppointmentForm, LoginForm, RegisterForm
import datetime
from sqlalchemy import Time
from fpdf import FPDF
import os  

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "role_choice"

# Ensure the directory for receipts exists
RECEIPT_DIR = "static/receipts"
if not os.path.exists(RECEIPT_DIR):
    os.makedirs(RECEIPT_DIR)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'doctor' or 'patient'

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    doctor = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(Time, nullable=False)  

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def role_choice():
    return render_template("role_choice.html")

@app.route('/doctor_choice')
def doctor_choice():
    return render_template("doctor_choice.html")

@app.route('/patient_choice')
def patient_choice():
    return render_template("patient_choice.html")

@app.route('/doctor_register', methods=['GET', 'POST'])
def doctor_register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists. Choose a different one.", "danger")
        else:
            new_user = User(username=form.username.data, password=form.password.data, role="doctor")
            db.session.add(new_user)
            db.session.commit()
            flash("Doctor registered successfully! Please log in.", "success")
            return redirect(url_for('doctor_login'))
    return render_template('doctor_register.html', form=form)

@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, role="doctor").first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('doctor_dashboard'))
        flash("Invalid username or password", "danger")
    return render_template('doctor_login.html', form=form)

@app.route('/patient_register', methods=['GET', 'POST'])
def patient_register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists. Choose a different one.", "danger")
        else:
            new_user = User(username=form.username.data, password=form.password.data, role="patient")
            db.session.add(new_user)
            db.session.commit()
            flash("Patient registered successfully! Please log in.", "success")
            return redirect(url_for('patient_login'))
    return render_template('patient_register.html', form=form)

@app.route('/patient_login', methods=['GET', 'POST'])
def patient_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, role="patient").first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('home'))
        flash("Invalid username or password", "danger")
    return render_template('patient_login.html', form=form)

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if current_user.role != "patient":
        flash("Only patients can book appointments!", "danger")
        return redirect(url_for('logout'))

    form = AppointmentForm()
    doctors = User.query.filter_by(role="doctor").all()
    form.doctor.choices = [(doctor.username, doctor.username) for doctor in doctors]

    if form.validate_on_submit():
        appointment = Appointment(
            patient_name=current_user.username,
            doctor=form.doctor.data,
            date=form.date.data,
            time=form.time.data
        )
        db.session.add(appointment)
        db.session.commit()
        session['token_number'] = f"{form.doctor.data}-{appointment.id}"
        flash(f"✅ Appointment confirmed! Token: {session['token_number']}", "success")

    return render_template("index.html", form=form, doctors=doctors, token_number=session.get('token_number'))

@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('role_choice'))

@app.route('/download_receipt/<token_number>')
@login_required
def download_receipt(token_number):
    try:
        doctor_name, appointment_id = token_number.split('-')
        appointment = Appointment.query.filter_by(id=appointment_id, doctor=doctor_name).first()

        if not appointment or appointment.patient_name != current_user.username:
            flash("Invalid token number or unauthorized access!", "danger")
            return redirect(url_for('home'))

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16)
        pdf.cell(200, 10, txt="Appointment Confirmation", ln=True, align="C")

        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Patient: {appointment.patient_name}", ln=True)
        pdf.cell(200, 10, txt=f"Doctor: {appointment.doctor}", ln=True)
        pdf.cell(200, 10, txt=f"Date: {appointment.date}", ln=True)
        pdf.cell(200, 10, txt=f"Time: {appointment.time.strftime('%I:%M %p')}", ln=True)
        pdf.cell(200, 10, txt=f"Token Number: {token_number}", ln=True)

        receipt_path = f"{RECEIPT_DIR}/receipt_{token_number}.pdf"
        pdf.output(receipt_path)

        return send_file(receipt_path, as_attachment=True)

    except ValueError:
        flash("Invalid token format.", "danger")
        return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

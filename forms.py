from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, TimeField, SelectField
from wtforms.validators import DataRequired

# Patient Appointment Form
class AppointmentForm(FlaskForm):
    patient_name = StringField('Patient Name', validators=[DataRequired()])
    doctor = SelectField('Doctor Name', choices=[], validators=[DataRequired()])  # Dropdown for doctors
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    submit = SubmitField('Book Appointment')

# Doctor Login & Registration Form
class DoctorForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit_login = SubmitField('Login')
    submit_register = SubmitField('Register')

# Patient Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Patient Registration Form
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

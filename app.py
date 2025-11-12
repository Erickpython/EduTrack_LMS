import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import CSRFProtect

# ======= Flask APP CONFIGURATION =======
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or os.urandom(24)

# ======= DATABASE CONFIGURATION =======
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database/lms.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ======= INITIALIZE DATABASE =======
db = SQLAlchemy(app)
# Enable CSRF protection (templates can use {{ csrf_token() }})
csrf = CSRFProtect(app)

# ======= USER MODEL =======
class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grades.id'), nullable=False)
    grade = db.relationship('Grade', backref=db.backref('students', lazy=True))

# ========== CREATE DATABASE TABLES ==========
with app.app_context():
    db.create_all()


# ======= ROUTES =======
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Basic input extraction and trimming
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        grade = request.form.get('grade', '').strip()

        # Manual input validation
        errors = []
        if not name:
            errors.append('Name is required.')
        if not email:
            errors.append('Email is required.')
        else:
            import re
            email_re = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
            if not re.match(email_re, email):
                errors.append('Enter a valid email address.')
        if not password:
            errors.append('Password is required.')
        else:
            if len(password) < 8:
                errors.append('Password must be at least 8 characters long.')
            if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
                errors.append('Password must contain both letters and numbers.')

        # Validate grade selection
        try:
            grade_id = int(grade)
        except (TypeError, ValueError):
            grade_id = None
            errors.append('Please select a valid grade.')
        else:
            if not Grade.query.get(grade_id):
                errors.append('Selected grade does not exist.')

        # If any validation errors, show them and re-render with grades
        if errors:
            for e in errors:
                flash(e, 'danger')
            grades = Grade.query.all()
            return render_template('register.html', grades=grades)

        # check if user already exists
        existing_user = Student.query.filter_by(email=email).first()
        if existing_user:
            flash('User already exists. Please log in.', 'danger')
            return redirect(url_for('login'))

        # Hash the password using a secure method
        hashed_pw = generate_password_hash(password)
        try:
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            app.logger.error('Database error creating user: %s', exc)
            flash('An internal error occurred; please try again later.', 'danger')
            grades = Grade.query.all()
            return render_template('register.html', grades=grades)

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    # GET: load grades and render form
    grades = Grade.query.all()
    return render_template('register.html', grades=grades)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        student = Student.query.filter_by(email=email).first()
        if student and check_password_hash(student.password, password):
            session['student_id'] = student.id
            flash(f'Login successful! Welcome back, {student.name}', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', name=session['student_name'])

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# ======= RUN THE APP =======
if __name__ == '__main__':
    # Read debug mode from environment variable with safe default of False
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.run(debug=debug_mode)
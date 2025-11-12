import os, re
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
csrf = CSRFProtect(app)   # removing csfr



# ======= USER MODEL =======
class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# student model
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)

    grade_id = db.Column(db.Integer, db.ForeignKey('grades.id'), nullable=False)
    current_grade_id = db.Column(db.Integer, db.ForeignKey('grades.id'))
    unlocked_grade_id = db.Column(db.Integer, db.ForeignKey('grades.id'))

    grade = db.relationship('Grade', foreign_keys=[grade_id], backref="registered_students")
    current_grade = db.relationship('Grade', foreign_keys=[current_grade_id], backref="current_students")
    unlocked_grade = db.relationship('Grade', foreign_keys=[unlocked_grade_id], backref="unlocked_students")

    def __repr__(self):
        return f'<Student {self.name}, Email: {self.email}, Grade ID: {self.grade_id}>'
    
# subject model 
class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grades.id'), nullable=False)
    grade = db.relationship('Grade', backref=db.backref("subjects", lazy=True))

    def __repr__(self):
        return f'<Subject {self.name}, Grade ID: {self.grade_id}>'


# lessons model
class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_path = db.Column(db.String(300))
    notes_path = db.Column(db.String(300))
    order = db.Column(db.Integer, nullable=False)

    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    subject = db.relationship('Subject', backref=db.backref("lessons", lazy=True))

    is_locked = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Lesson {self.title}, Subject ID: {self.subject_id}>'
    
# Progress model
class Progress(db.Model):
    __tablename__ = 'progress'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    
    completed = db.Column(db.Boolean, default=False)
    score = db.Column(db.Float, default= 0.0)
    unlocked = db.Column(db.Boolean, default=False)

    student = db.relationship('Student', backref=db.backref("progress_records", lazy=True))
    lesson = db.relationship('Lesson', backref=db.backref("progress_records", lazy=True))

    def __repr__(self):
        return f'<Progress Student ID: {self.student_id}, Lesson ID: {self.lesson_id}, Completed: {self.completed}>'



# ========== CREATE DATABASE TABLES ==========
with app.app_context():
    db.create_all()

# default grades
    if not Grade.query.first():
        for i in range (1, 10):
            grade = Grade(name=f'Grade {i}')
            db.session.add(grade)
        db.session.commit()

# populate  subjects in  each grade
    if not Subject.query.first():
        grades = Grade.query.all()
        default_subjects = ['Numeracy_MATHS', 'Literacy_ENG', 'Computer Studies']
        for grade in grades:
            for subject_name in default_subjects:
                subject = Subject(name=subject_name, grade_id=grade.id)
                db.session.add(subject)
        db.session.commit()

# populate lessons for each subject
    if not Lesson.query.first():
        subjects = Subject.query.all()
        for subject in subjects:
            for i in range (1, 21):
                db.session.add(Lesson(
                    title=f'Lesson {i} - {subject.name}',
                    description=f'Description for Lesson {i} of {subject.name}',
                    order=i,
                    subject_id=subject.id,
                    is_locked=True if i > 1 else False  # Unlock only the first lesson
                ))
        db.session.commit()

        

# ======= ROUTES =======
@app.route('/')
def index():
    return render_template('index.html')

#register
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
        elif not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            errors.append('Enter a valid email address.')
        if not password:
            errors.append('Password is required.')
        elif len(password) < 8 or not (any(c.isalpha() for c in password) and any(c.isdigit() for c in password)):
            errors.append('Password must be at least 8 characters long and contain both letters and numbers.')

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
        new_student = Student(name=name, email=email, password=hashed_pw, grade_id=grade_id)
        db.session.add(new_student)
        try:
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            app.logger.error('Database error creating user: %s', exc)
            flash('An internal error occurred; please try again later.', 'danger')
            grades = Grade.query.all()
            return render_template('register.html', grades=grades)
        
        lessons = Lesson.query.join(Subject).join(Grade).filter(Grade.id <= grade_id).all()
        for lesson in lessons:
            progress = Progress(student_id=new_student.id, lesson_id=lesson.id, completed=False, unlocked=(lesson.order == 1))
            db.session.add(progress)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    # GET: load grades and render form
    grades = Grade.query.all()
    return render_template('register.html', grades=grades)

#login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        student = Student.query.filter_by(email=email).first()
        if student and check_password_hash(student.password, password):
            session['student_id'] = student.id
            session['student_name'] = student.name
            flash(f'Login successful! Welcome back, {student.name}', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    student = Student.query.get(session['student_id'])

    #getting grades 
    accessible_grades = Grade.query.filter(Grade.id <= student.grade_id).all()

    # getting subjects 
    grades_data = []
    for grade in accessible_grades:
        subjects = Subject.query.filter_by(grade_id=grade.id).all()
        grades_data.append(
            {
                'grade': grade,
                'subjects': subjects
            }
        )

    return render_template('dashboard.html', student=student, grades_data=grades_data)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))



@app.route('/subject/<int:subject_id>')
def subject_lessons(subject_id):
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('login'))
    

    subject = Subject.query.get(subject_id)
    lessons = Lesson.query.filter_by(subject_id=subject_id).order_by(Lesson.order).all()
    

    lesson_progress = []
    for lesson in lessons:
        progress = Progress.query.filter_by(student_id=student_id, lesson_id=lesson.id).first()
        lesson_progress.append((lesson, progress))

    return render_template('subject_lessons.html', subject=subject, lesson_progress=lesson_progress)


# ======= RUN THE APP =======
if __name__ == '__main__':
    # Read debug mode from environment variable with safe default of False
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.run(debug=debug_mode)


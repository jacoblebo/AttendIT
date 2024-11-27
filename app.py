from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import os
from flask_wtf import CSRFProtect
import re # we love regex
from datetime import datetime
csrf = CSRFProtect()
import random
import string
import pandas as pd
import uuid

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
csrf.init_app(app)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///AttendIT.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Attendance(db.Model):
    __tablename__ = 'Attendance'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    session_id = db.Column(db.Integer, db.ForeignKey('ClassSessions.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    status = db.Column(db.Integer)

class Class(db.Model):
    __tablename__ = 'Classes'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    professor_id = db.Column(db.Integer, nullable=False)
    join_code = db.Column(db.String(5), nullable=False, unique=True)

class Enrollment(db.Model):
    __tablename__ = 'Enrollments'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    student_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('Classes.id'), nullable=False)

class ClassSession(db.Model):
    __tablename__ = 'ClassSessions'
    id = db.Column(db.String, primary_key=True)
    class_id = db.Column(db.String, db.ForeignKey('Classes.id'), nullable=False)
    session_start_date = db.Column(db.String, nullable=False)
    session_end_date = db.Column(db.String, nullable=False)
    bypass_code = db.Column(db.String, nullable=False)

db.init_app(app)

with app.app_context():
    if not os.path.exists('AttendIT.db'):
        db.create_all()
        # Create a professor user account if it doesn't exist
        admin_email = 'admin@uncc.edu'
        admin_password = '123'
        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            admin_user = User(
            id=str(uuid.uuid4()),
            firstName='Admin',
            lastName='User',
            email=admin_email,
            password=bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            role=1  # Role 1 for professor
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created with email: ", admin_email)
        test_student_email = 'test@uncc.edu'
        test_student_password = '123'
        existing_student = User.query.filter_by(email=test_student_email).first()
        if not existing_student:
            test_student = User(
            id=str(uuid.uuid4()),
            firstName='Test',
            lastName='Student',
            email=test_student_email,
            password=bcrypt.hashpw(test_student_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            role=0  # Role 0 for student
            )
            db.session.add(test_student)
            db.session.commit()
            print("Test student created with email: ", test_student_email)
    else:
        print("Database already exists, happy bug hunting!")

@app.before_request
def method_override():
    if request.method == 'POST' and '_method' in request.form:
        method = request.form['_method'].upper()
        if method in ['PUT', 'DELETE']:
            request.environ['REQUEST_METHOD'] = method

@app.route('/', methods=['GET'])
def index():
    print("Current time:", datetime.now())
    #if the user is logged in, send them to the correct dashboard, else send them to the login page
    if 'user' in session:
        if session['user']['role'] == 0:
            return redirect(url_for('student_dashboard'))
        elif session['user']['role'] == 1:
            return redirect(url_for('instructor_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    print("Form data received:", request.form)

    email = request.form['email']
    password = request.form['password']

    # Check if the email is from the correct domain
    if not re.match(r'^[\w\.-]+@(charlotte\.edu|uncc\.edu)$', email):
        flash('Email must be from @charlotte.edu or @uncc.edu domains', 'error')
        return redirect(url_for('login'))

    # Find the user in the database
    user = User.query.filter_by(email=email).first()

    if user:
        # Check if the password is correct
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session['user'] = {
                'id': user.id,
                'firstName': user.firstName,
                'lastName': user.lastName,
                'email': user.email,
                'role': user.role
            }
            if user.role == 0:
                return redirect(url_for('student_dashboard'))
            elif user.role == 1:
                return redirect(url_for('instructor_dashboard'))
        else:
            flash('Incorrect password', 'error')
            return redirect(url_for('login'))
    else:
        flash('Email not found', 'error')
        return redirect(url_for('login'))
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        role = 0 # Default role is student

        # Validate email domain
        if not re.match(r'^[\w\.-]+@(charlotte\.edu|uncc\.edu)$', email):
            flash('Email must be from @charlotte.edu or @uncc.edu domains', 'error')
            return redirect(url_for('register'))

        # Check if the email is already in use
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already in use', 'error')
            return redirect(url_for('register'))

        # Create new user without hashing the password
        new_user = User(
            id=str(uuid.uuid4()),
            firstName=first_name,
            lastName=last_name,
            email=email,
            password= bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), 
            role=role
        )

        print(f"New user: {new_user}")

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')

# Student Dashboard
@app.route('/student_dashboard', methods=['GET'])
def student_dashboard():
    if 'user' not in session or session['user']['role'] != 0:
        return redirect(url_for('login'))

    student_id = session['user']['id']
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    courses = [Class.query.get(enrollment.class_id) for enrollment in enrollments]

    # Sort courses by the next session date, handling cases where no session exists
    def get_next_session_start_date(course):
        next_session = ClassSession.query.filter_by(class_id=course.id).order_by(ClassSession.session_start_date).first()
        return next_session.session_start_date if next_session else "9999-12-31 23:59:59"

    courses.sort(key=get_next_session_start_date)

    return render_template('student_dashboard.html', user=session['user'], courses=courses)

@app.route('/student_course_info/<string:course_id>', methods=['GET'])
def student_course_info(course_id):
    if 'user' not in session or session['user']['role'] != 0:
        return jsonify({'error': 'Unauthorized'}), 403

    course = Class.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    next_session = ClassSession.query.filter_by(class_id=course_id).order_by(ClassSession.session_start_date).first()
    next_session_info = f"{next_session.session_start_date} to {next_session.session_end_date}" if next_session else "No upcoming sessions"

    course_info = {
        'name': course.name,
        'next_session': next_session_info
    }
    return jsonify(course_info)

@app.route('/instructor_dashboard', methods=['GET'])
def instructor_dashboard():
    if 'user' not in session or session['user']['role'] != 1:
        return redirect(url_for('login'))

    professor_id = session['user']['id']
    courses = Class.query.filter_by(professor_id=professor_id).all()

    # Add additional data for each course
    for course in courses:
        course.enrollment = Enrollment.query.filter_by(class_id=course.id).count()
        class_sessions = ClassSession.query.filter_by(class_id=course.id).order_by(ClassSession.session_start_date).all()
        course.sessions = []
        for class_session in class_sessions:
            attendees = Attendance.query.filter_by(session_id=class_session.id).count()
            percent_present = (attendees / course.enrollment) * 100 if course.enrollment > 0 else 0
            start_datetime = datetime.strptime(class_session.session_start_date, "%Y-%m-%d %H:%M:%S")
            end_datetime = datetime.strptime(class_session.session_end_date, "%Y-%m-%d %H:%M:%S")
            if start_datetime.date() == end_datetime.date():
                session_date = f"{start_datetime.strftime('%I:%M %p')} - {end_datetime.strftime('%I:%M %p %m/%d/%y')}"
            else:
                session_date = f"{start_datetime.strftime('%I:%M %p %m/%d/%y')} - {end_datetime.strftime('%I:%M %p %m/%d/%y')}"
            course.sessions.append({
                'session_date': session_date,
                'bypass_code': class_session.bypass_code,
                'attendees': attendees,
                'percent_present': percent_present
            })
        
        # Find the index of the next/current session
        now = datetime.now()
        next_session_index = next((i for i, s in enumerate(class_sessions) if datetime.strptime(s.session_start_date, "%Y-%m-%d %H:%M:%S") >= now), len(class_sessions))

        # Select the next/current session, the 3 after that, and the 4 before that
        start_index = max(0, next_session_index - 4)
        end_index = min(len(class_sessions), next_session_index + 4)
        course.recent_sessions = course.sessions[start_index:end_index]

    return render_template('instructor_dashboard.html', user=session['user'], courses=courses)

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Error Page
@app.route('/error', methods=['GET'])
def error():
    return render_template('error.html')

def generate_join_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

def generate_unique_join_code():
    while True:
        join_code = generate_join_code()
        existing_code = Class.query.filter_by(join_code=join_code).first()
        if not existing_code:
            return join_code

@app.route('/create_course', methods=['POST'])
def create_course():
    if 'user' not in session or session['user']['role'] != 1:
        return redirect(url_for('login'))

    course_name = request.form['course_name']
    professor_id = session['user']['id']

    existing_course = Class.query.filter_by(name=course_name, professor_id=professor_id).first()
    if existing_course:
        flash('Course with this name already exists', 'error')
        return redirect(url_for('instructor_dashboard'))

    join_code = generate_unique_join_code()

    new_course = Class(
        id=str(uuid.uuid4()),
        name=course_name,
        professor_id=professor_id,
        join_code=join_code
    )
    print(f"New course: name={new_course.name}, professor_id={new_course.professor_id}, join_code={new_course.join_code}")
    db.session.add(new_course)
    db.session.commit()
    flash('Course created successfully', 'success')
    return redirect(url_for('instructor_dashboard'))

@app.route('/course_info/<string:course_id>', methods=['GET'])
def course_info(course_id):
    print(f"Fetching course info for course_id: {course_id}")
    course = Class.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    enrollment_count = Enrollment.query.filter_by(class_id=course_id).count()
    print(f"Enrollment count for course_id {course_id}: {enrollment_count}")

    next_session = ClassSession.query.filter_by(class_id=course_id).order_by(ClassSession.session_start_date).first()
    print(f"Next session for course_id {course_id}: {next_session}")

    next_session_info = {
        'start_date': next_session.session_start_date,
        'end_date': next_session.session_end_date,
        'bypass_code': next_session.bypass_code
    } if next_session else None

    course_info = {
        'name': course.name,
        'join_code': course.join_code,
        'enrollment': enrollment_count,
        'next_session': next_session_info
    }
    return jsonify(course_info)

@app.route('/create_session', methods=['POST'])
def create_session():
    if 'user' not in session or session['user']['role'] != 1:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    class_id = request.form['course_id']
    session_start_date = request.form['session_start_date']
    session_start_time = request.form['session_start_time']
    session_end_time = request.form['session_end_time']
    bypass_code = generate_join_code()
    
    # Combine date and time strings and convert to datetime objects
    session_start_datetime = datetime.strptime(f"{session_start_date} {session_start_time}", "%Y-%m-%d %H:%M")
    session_end_datetime = datetime.strptime(f"{session_start_date} {session_end_time}", "%Y-%m-%d %H:%M")
    
    # Check if the session start date and time are in the future
    if session_start_datetime <= datetime.now():
        flash('Session start date and time must be in the future', 'error')
        return redirect(url_for('instructor_dashboard'))
    
    # Check if the session end date and time are after the session start date and time
    if session_end_datetime <= session_start_datetime:
        flash('Session end date and time must be after the start date and time', 'error')
        return redirect(url_for('instructor_dashboard'))
    
    print(f"Creating session for class_id={class_id}, session_start_date={session_start_datetime}, session_end_date={session_end_datetime}, bypass_code={bypass_code}")
    
    new_class_session = ClassSession(
        id=str(uuid.uuid4()),
        class_id=class_id,
        session_start_date=session_start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        session_end_date=session_end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        bypass_code=bypass_code
    )
    
    db.session.add(new_class_session)
    db.session.commit()
    flash('Session created successfully', 'success')
    return redirect(url_for('instructor_dashboard'))

@app.route('/edit_session/<string:session_id>', methods=['POST'])
def edit_session(session_id):
    if 'user' not in session or session['user']['role'] != 1:
        flash('Unauthorized', 'error')
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    session_record = ClassSession.query.get(session_id)
    if not session_record:
        flash('Session not found', 'error')
        return jsonify({'success': False, 'message': 'Session not found'}), 404

    data = request.get_json()
    new_start_date = data['start_date']
    new_end_date = data['end_date']
    session_record.session_start_date = new_start_date
    session_record.session_end_date = new_end_date
    db.session.commit()
    flash('Session updated successfully', 'success')
    return jsonify({'success': True, 'message': 'Session updated successfully'})

@app.route('/download_attendance/<string:session_id>', methods=['GET'])
def download_attendance(session_id):
    if 'user' not in session or session['user']['role'] != 1:
        flash('Unauthorized', 'error')
        return redirect(url_for('login'))

    session_record = ClassSession.query.get(session_id)
    if not session_record:
        flash('Session not found', 'error')
        return redirect(url_for('instructor_dashboard'))

    attendance_records = Attendance.query.filter_by(session_id=session_id).all()
    data = [{'Student ID': record.student_id, 'Status': record.status} for record in attendance_records]
    
    # Create a DataFrame
    df = pd.DataFrame(data)
    
    # Generate CSV data
    csv_data = df.to_csv(index=False)
    
    # Format the file name
    session_start_datetime = datetime.strptime(session_record.session_start_date, "%Y-%m-%d %H:%M:%S")
    file_name = f"attendance_{session_start_datetime.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = f"attachment; filename={file_name}"
    response.headers["Content-Type"] = "text/csv"
    return response

@app.route('/delete_session/<string:session_id>', methods=['DELETE'])
def delete_session(session_id):
    if 'user' not in session or session['user']['role'] != 1:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    session_record = ClassSession.query.get(session_id)
    if not session_record:
        return jsonify({'success': False, 'message': 'Session not found'}), 404

    Attendance.query.filter_by(session_id=session_id).delete()
    db.session.delete(session_record)
    db.session.commit()
    flash('Session deleted successfully', 'success')
    return jsonify({'success': True, 'message': 'Session deleted successfully'})

@app.route('/edit_course', methods=['POST'])
def edit_course():
    if 'user' not in session or session['user']['role'] != 1:
        return redirect(url_for('login'))
    print("Form data received:", request.form)
    course_id = request.form['course-id']
    new_course_name = request.form['course_name']

    course = Class.query.get(course_id)
    if not course:
        flash('Course not found', 'error')
        return redirect(url_for('instructor_dashboard'))

    course.name = new_course_name
    db.session.commit()

    flash('Course updated successfully', 'success')
    return redirect(url_for('instructor_dashboard'))

@app.route('/delete_class/<string:class_id>', methods=['DELETE'])
def delete_class(class_id):
    if 'user' not in session or session['user']['role'] != 1:
        flash('Unauthorized', 'error')
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    course = Class.query.get(class_id)
    if not course:
        flash('Course not found', 'error')
        return jsonify({'success': False, 'message': 'Course not found'}), 404

    # Delete associated records
    ClassSession.query.filter_by(class_id=class_id).delete()
    Enrollment.query.filter_by(class_id=class_id).delete()
    Attendance.query.filter(Attendance.session_id.in_(
        db.session.query(ClassSession.id).filter_by(class_id=class_id)
    )).delete()

    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully', 'success')
    return jsonify({'success': True, 'message': 'Course deleted successfully'})

#student methods

@app.route('/enroll_course', methods=['POST'])
def enroll_course():
    if 'user' not in session or session['user']['role'] != 0:
        return redirect(url_for('login'))

    join_code = request.form['join_code']
    student_id = session['user']['id']

    course = Class.query.filter_by(join_code=join_code).first()
    if not course:
        flash('Invalid join code', 'error')
        return redirect(url_for('student_dashboard'))

    existing_enrollment = Enrollment.query.filter_by(student_id=student_id, class_id=course.id).first()
    if existing_enrollment:
        flash('You are already enrolled in this course', 'error')
        return redirect(url_for('student_dashboard'))

    new_enrollment = Enrollment(student_id=student_id, class_id=course.id)
    db.session.add(new_enrollment)
    db.session.commit()
    flash('Enrolled in course successfully', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/mark_attendance/<string:course_id>', methods=['POST'])
def mark_attendance(course_id):
    if 'user' not in session or session['user']['role'] != 0:
        return jsonify({'success': False, 'message': 'Unauthorized'})

    student_id = session['user']['id']
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = request.get_json()
    bypass_code = data.get('bypass_code')

    session_record = ClassSession.query.filter_by(class_id=course_id).filter(
        ClassSession.session_start_date <= current_time,
        ClassSession.session_end_date >= current_time
    ).first()

    if not session_record:
        return jsonify({'success': False, 'message': "That class isn't happening right now"})

    if session_record.bypass_code != bypass_code:
        return jsonify({'success': False, 'message': 'Invalid bypass code'})

    existing_attendance = Attendance.query.filter_by(student_id=student_id, session_id=session_record.id).first()
    if existing_attendance:
        return jsonify({'success': False, 'message': 'Attendance already marked'})

    new_attendance = Attendance(student_id=student_id, session_id=session_record.id, status=1)
    db.session.add(new_attendance)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Attendance marked successfully'})

if __name__ == "__main__":
    app.run(debug=True)
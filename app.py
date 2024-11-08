from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import os
from flask_wtf import CSRFProtect
import re # we love regex
from datetime import datetime
csrf = CSRFProtect()
import random
import string


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
csrf.init_app(app)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///AttendIT.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Attendance(db.Model):
    __tablename__ = 'Attendance'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('Sessions.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    status = db.Column(db.Integer)

class Class(db.Model):
    __tablename__ = 'Classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    professor_id = db.Column(db.Integer, nullable=False)
    join_code = db.Column(db.String(5), nullable=False, unique=True)

class Enrollment(db.Model):
    __tablename__ = 'Enrollments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('Classes.id'), nullable=False)

class Session(db.Model):
    __tablename__ = 'Sessions'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('Classes.id'))
    session_start_date = db.Column(db.String(50))
    session_end_date = db.Column(db.String(50))
    bypass_code = db.Column(db.String(50))

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
            firstName='Admin',
            lastName='User',
            email=admin_email,
            password=bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            role=1  # Role 1 for professor
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created with email: ", admin_email)
    else:
        print("Database already exists")

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
            firstName=first_name,
            lastName=last_name,
            email=email,
            password= bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), 
            role=role
        )

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
    return render_template('student_dashboard.html', user=session['user'])

# Instructor Dashboard
@app.route('/instructor_dashboard', methods=['GET'])
def instructor_dashboard():
    if 'user' not in session or session['user']['role'] != 1:
        return redirect(url_for('login'))

    professor_id = session['user']['id']
    courses = Class.query.filter_by(professor_id=professor_id).all()
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
        name=course_name,
        professor_id=professor_id,
        join_code=join_code
    )
    db.session.add(new_course)
    db.session.commit()
    flash('Course created successfully', 'success')
    return redirect(url_for('instructor_dashboard'))

@app.route('/course_info/<int:course_id>', methods=['GET'])
def course_info(course_id):
    course = Class.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    enrollment_count = Enrollment.query.filter_by(class_id=course_id).count()

    course_info = {
        'name': course.name,
        'join_code': course.join_code,
        'enrollment': enrollment_count
    }
    return jsonify(course_info)

if __name__ == "__main__":
    app.run(debug=True)

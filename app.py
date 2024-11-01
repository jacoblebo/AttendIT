from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import os
import re # we love regex

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.Integer, nullable=False)

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
    latitude = db.Column(db.Integer, nullable=False)
    longitude = db.Column(db.Integer, nullable=False)
    no_location = db.Column(db.Integer, nullable=False)

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

# Home/Login Route
@app.route('/', methods=['POST', 'GET'])
def login():
    # Check if already logged in
    if 'user' in session:
        if session['user']['role'] == 0:
            return redirect('/student_dashboard')
        elif session['user']['role'] == 1:
            return redirect('/instructor_dashboard')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        # Authenticate user
        users = User.query.all()
        user = users.get(email)
        if user and bcrypt.checkpw(password, user['password']):
            # Set user info in session
            session['user'] = {
                'firstName': user['firstName'],
                'lastName': user['lastName'],
                'email': user['email'],
                'role': user['role']
            }
            # Redirect based on role
            if user['role'] == 0:
                return redirect('/student_dashboard')
            elif user['role'] == 1:
                return redirect('/instructor_dashboard')
        else:
            # Authentication failed, redirect to error page
            flash('Invalid email or password', 'error')
            return redirect(url_for('error'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', type=int)

        # Validate email domain
        if not re.match(r'^[\w\.-]+@(charlotte\.edu|uncc\.edu)$', email):
            flash('Email must be from @charlotte.edu or @uncc.edu domains', 'error')
            return redirect(url_for('register'))

        # Check if the email is already in use
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already in use', 'error')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create new user
        new_user = User(
            firstName=first_name,
            lastName=last_name,
            email=email,
            password=hashed_password,
            role=role
        )

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Student Dashboard
@app.route('/student_dashboard', methods=['POST', 'GET'])
def student_dashboard():
    if 'user' not in session or session['user']['role'] != 0:
        return redirect(url_for('login'))
    return render_template('student_dashboard.html', user=session['user'])

# Instructor Dashboard
@app.route('/instructor_dashboard', methods=['POST', 'GET'])
def instructor_dashboard():
    if 'user' not in session or session['user']['role'] != 1:
        return redirect(url_for('login'))
    return render_template('instructor_dashboard.html', user=session['user'])

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# Error Page
@app.route('/error', methods=['GET'])
def error():
    return render_template('error.html')

if __name__ == "__main__":
    app.run(debug=True)

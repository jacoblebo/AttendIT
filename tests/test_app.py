import os
import sys
import pytest
from flask import session
from flask_wtf import CSRFProtect 
csrf = CSRFProtect()
import uuid
import bcrypt
from datetime import datetime, timedelta

# Add the directory containing app.py to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, User, Class, Enrollment, ClassSession, Attendance

app.secret_key = os.getenv('SECRET_KEY')

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection in tests
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

        db.drop_all()

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_login(client):
    # Create a test user
    test_user = User(
        id=str(uuid.uuid4()),
        firstName='Test',
        lastName='User',
        email='test@uncc.edu',
        password=bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        role=0
    )
    with app.app_context():
        db.session.add(test_user)
        db.session.commit()

    response = client.post('/login', data={
        'email': 'test@uncc.edu',
        'password': 'password'
    }, follow_redirects=True)
    print(response.data)  # Debugging information
    assert response.status_code == 200
    assert b'Student Dashboard' in response.data

def test_register(client):
    response = client.post('/register', data={
        'firstName': 'New',
        'lastName': 'User',
        'email': 'new@uncc.edu',
        'password': 'password'
    }, follow_redirects=True)
    print(response.data)  # Debugging information
    assert response.status_code == 200
    assert b'Registration successful' in response.data

def test_student_dashboard(client):
    with client.session_transaction() as sess:
        sess['user'] = {'id': 1, 'role': 0}
    response = client.get('/student_dashboard')
    assert response.status_code == 200

def test_instructor_dashboard(client):
    with client.session_transaction() as sess:
        sess['user'] = {'id': 1, 'role': 1}
    response = client.get('/instructor_dashboard')
    assert response.status_code == 200

def test_logout(client):
    with client.session_transaction() as sess:
        sess['user'] = {'id': 1, 'role': 0}
    response = client.get('/logout', follow_redirects=True)
    print(response.data)  # Debugging information
    assert response.status_code == 200
    assert b'You have been logged out' in response.data

def test_create_course(client):
    with client.session_transaction() as sess:
        sess['user'] = {'id': 1, 'role': 1}
    response = client.post('/create_course', data={
        'course_name': 'Test Course'
    }, follow_redirects=True)
    print(response.data)  # Debugging information
    assert response.status_code == 200
    assert b'Course created successfully' in response.data

def test_enroll_course(client):
    # Create a test course
    test_course = Class(
        id=str(uuid.uuid4()),
        name='Test Course',
        professor_id=1,
        join_code='ABCDE'
    )
    db.session.add(test_course)
    db.session.commit()

    with client.session_transaction() as sess:
        sess['user'] = {'id': 1, 'role': 0}
    response = client.post('/enroll_course', data={
        'join_code': 'ABCDE'
    }, follow_redirects=True)
    print(response.data)  # Debugging information
    assert response.status_code == 200
    assert b'Enrolled in course successfully' in response.data

def test_mark_attendance(client):
    # Create a test session
    now = datetime.now()
    test_session = ClassSession(
        id=str(uuid.uuid4()),
        class_id=1,
        session_start_date=now.strftime('%Y-%m-%d %H:%M:%S'),
        session_end_date=(now + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
        bypass_code='12345'
    )
    with app.app_context():
        db.session.add(test_session)
        db.session.commit()

    with client.session_transaction() as sess:
        sess['user'] = {'id': 1, 'role': 0}
    response = client.post('/mark_attendance/1', json={
        'bypass_code': '12345'
    })
    print(response.data)  # Debugging information
    assert response.status_code == 200
    assert b'Attendance marked successfully' in response.data

def test_edit_session(client):
    # Create a test session
    session_id = str(uuid.uuid4())
    test_session = ClassSession(
        id=session_id,
        class_id='1',
        session_start_date='2023-01-01 00:00:00',
        session_end_date='2023-12-31 23:59:59',
        bypass_code='12345'
    )
    with app.app_context():
        db.session.add(test_session)
        db.session.commit()

    with client.session_transaction() as sess:
        sess['user'] = {'id': 1, 'role': 1}
    response = client.post(f'/edit_session/{session_id}', data={
        'start_date': '2023-01-02T00:00',
        'end_date': '2023-12-30T23:59'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Session updated successfully' in response.data

def test_delete_session(client):
    # Create a test session
    session_id = str(uuid.uuid4())
    test_session = ClassSession(
        id=session_id,
        class_id='1',
        session_start_date='2023-01-01 00:00:00',
        session_end_date='2023-12-31 23:59:59',
        bypass_code='12345'
    )
    with app.app_context():
        db.session.add(test_session)
        db.session.commit()

    with client.session_transaction() as sess:
        sess['user'] = {'id': 1, 'role': 1}
    response = client.delete(f'/delete_session/{session_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Session deleted successfully' in response.data

def test_view_enrollment(client):
    # Create a test course and enrollment
    test_course = Class(
        id=str(uuid.uuid4()),
        name='Test Course',
        professor_id=1,
        join_code='ABCDE'
    )
    test_user = User(
        id=str(uuid.uuid4()),
        firstName='Test',
        lastName='User',
        email='test@uncc.edu',
        password='password',
        role=0
    )
    test_enrollment = Enrollment(
        id=str(uuid.uuid4()),
        student_id=test_user.id,
        class_id=test_course.id
    )
    db.session.add(test_course)
    db.session.add(test_user)
    db.session.add(test_enrollment)
    db.session.commit()

    with client.session_transaction() as sess:
        sess['user'] = {'id': 1, 'role': 1}
    response = client.get(f'/view_enrollment/{test_course.id}')
    assert response.status_code == 200
    assert b'Test' in response.data

def test_download_attendance(client):
    # Create a test session and attendance
    test_session = ClassSession(
        id=str(uuid.uuid4()),
        class_id='1',
        session_start_date='2023-01-01 00:00:00',
        session_end_date='2023-12-31 23:59:59',
        bypass_code='12345'
    )
    test_user = User(
        id=str(uuid.uuid4()),
        firstName='Test',
        lastName='User',
        email='test@uncc.edu',
        password='password',
        role=0
    )
    test_attendance = Attendance(
        id=str(uuid.uuid4()),
        session_id=test_session.id,
        student_id=test_user.id,
        status=1
    )
    db.session.add(test_session)
    db.session.add(test_user)
    db.session.add(test_attendance)
    db.session.commit()

    with client.session_transaction() as sess:
        sess['user'] = {'id': 1, 'role': 1}
    response = client.get(f'/download_attendance/{test_session.id}')
    assert response.status_code == 200
    assert b'Test User' in response.data

def test_course_info(client):
    # Create a test course and session
    course_id = str(uuid.uuid4())
    test_course = Class(
        id=course_id,
        name='Test Course',
        professor_id=1,
        join_code='ABCDE'
    )
    test_session = ClassSession(
        id=str(uuid.uuid4()),
        class_id=course_id,
        session_start_date='2023-01-01 00:00:00',
        session_end_date='2023-12-31 23:59:59',
        bypass_code='12345'
    )
    with app.app_context():
        db.session.add(test_course)
        db.session.add(test_session)
        db.session.commit()

    with client.session_transaction() as sess:
        sess['user'] = {'id': 1, 'role': 1}
    response = client.get(f'/course_info/{course_id}')
    assert response.status_code == 200
    assert b'Test Course' in response.data

def test_course_info(client):
    # Create a test course and session
    test_course = Class(
        id=str(uuid.uuid4()),
        name='Test Course',
        professor_id=1,
        join_code='ABCDE'
    )
    test_session = ClassSession(
        id=str(uuid.uuid4()),
        class_id=test_course.id,
        session_start_date='2023-01-01 00:00:00',
        session_end_date='2023-12-31 23:59:59',
        bypass_code='12345'
    )
    db.session.add(test_course)
    db.session.add(test_session)
    db.session.commit()

    with client.session_transaction() as sess:
        sess['user'] = {'id': 1, 'role': 1}
    response = client.get(f'/course_info/{test_course.id}')
    assert response.status_code == 200
    assert b'Test Course' in response.data
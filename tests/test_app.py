import os
import sys
import pytest
from flask import session

# Add the directory containing app.py to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, User, Class, Enrollment, Session, Attendance

@pytest.fixture
def client():
    app.config['TESTING'] = True
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
        firstName='Test',
        lastName='User',
        email='test@uncc.edu',
        password='password',
        role=0
    )
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
    test_session = Session(
        class_id=1,
        session_start_date='2023-01-01 00:00:00',
        session_end_date='2023-12-31 23:59:59',
        bypass_code='12345'
    )
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
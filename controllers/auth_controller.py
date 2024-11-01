from flask import Blueprint, render_template

auth = Blueprint('auth', __name__)


@auth.route("/student_dashboard")
def student_dashboard():
    return render_template('student_dashboard.html')

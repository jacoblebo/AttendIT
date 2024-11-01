from flask import Flask, render_template, request, redirect, session
from controllers import main_controller, auth_controller

app = Flask(__name__)


# Home Route
@app.route('/', methods=['POST', 'GET'])
def login():
    # If the user is logged in, display dashboard
    # else, display login page
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"Username: {username}")
        print(f"Password: {password}")
        return redirect('/')
    else:
        return render_template('login.html')


@app.route('/student_dashboard', methods=['POST', 'GET'])
def student_dashboard():
    return render_template('student_dashboard.html')


if __name__ == "__main__":
    app.run(debug=True)

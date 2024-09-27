from flask import Flask, render_template, request
from controllers import main_controller, auth_controller

app = Flask(__name__)


# @app.route("/")
# def home():
#     return render_template('home.html')

# @app.route("/login")
# def login():
#     return render_template('login.html')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"Username: {username}")
        print(f"Password: {password}")
        
    
    return render_template('login.html')



if __name__ == "__main__":
    app.run(debug=True)
from flask import Blueprint, render_template

main = Blueprint('main', __name__)


@main.route("/")
def login():
    return render_template('login.html')

from flask_sqlalchemy import SQLAlchemy

# Database logic for user
#Figure out UNCC Auth
db = SQLAlchemy()

class User(db.Model):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    
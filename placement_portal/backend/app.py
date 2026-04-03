from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from backend.config import Config
 


db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from backend.models import user, company, student, job, application, placement 

    with app.app_context():
        db.create_all()
        create_admin()

    return app


def create_admin():
    from backend.models.user import User
    admin = User.query.filter_by(email = "admin@gmail.com").first()

    if not admin:
        admin = User(
            name = "Admin",
            email = "admin@gmail.com",
            password = "admin123",
            role = "admin",
            is_approved = True
        )
        db.session.add(admin)
        db.session.commit()
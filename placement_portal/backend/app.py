from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_caching import Cache
from backend.config import Config
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()
cache = Cache()

@login_manager.unauthorized_handler
def unauthorized():
    from flask import jsonify
    return jsonify({"message": "Unauthorized. Please log in."}), 401


@login_manager.user_loader
def load_user(user_id):
    from backend.models.user import User
    return User.query.get(int(user_id))


import os

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 60  # 1 min
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    cache.init_app(app)

    CORS(app, supports_credentials=True)

    db.init_app(app)
    login_manager.init_app(app)

    from backend.models import user, company, student, job, application, placement

    with app.app_context():
        db.create_all()
        create_admin()

    from backend.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')

    from backend.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    from backend.routes.company import company_bp
    app.register_blueprint(company_bp, url_prefix='/api/company')

    from backend.routes.student import student_bp
    app.register_blueprint(student_bp, url_prefix='/api/student')


    return app


def create_admin():
    from backend.models.user import User
    admin = User.query.filter_by(email="admin@gmail.com").first()

    if not admin:
        admin = User(
            name="Admin",
            email="admin@gmail.com",
            password=generate_password_hash("admin123"),
            role="admin",
            is_approved=True
        )
        db.session.add(admin)
        db.session.commit()

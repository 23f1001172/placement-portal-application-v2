from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from backend.models.user import User
from backend.models.student import Student
from backend.models.company import Company
from backend.app import db
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    password = generate_password_hash(data.get('password'))
    role = data.get('role')

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    user = User(
        name=name,
        email=email,
        password=password,
        role=role,
        is_approved=False
    )

    db.session.add(user)
    db.session.commit()

    if role == "student":
        student = Student(user_id=user.id)
        db.session.add(student)

    elif role == "company":
        company = Company(user_id=user.id)
        db.session.add(company)

    db.session.commit()

    return jsonify({"message": "Registered successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not registered please register first"}), 404

    if not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    if user.is_blacklisted:
        return jsonify({"message": "User is blacklisted"}), 403

    if user.is_rejected:
        return jsonify({"message": "Your registration has been rejected by the admin"}), 403

    if not user.is_approved and user.role != "admin":
        return jsonify({"message": "Account not approved by admin"}), 403


    login_user(user)

    return jsonify({
        "message": "Login successful",
        "role": user.role
    })

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"})


@auth_bp.route('/me')
@login_required
def me():
    return jsonify({
        "id": current_user.id,
        "name": current_user.name,
        "role": current_user.role
    })

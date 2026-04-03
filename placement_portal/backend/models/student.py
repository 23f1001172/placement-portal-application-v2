from backend.app import db

class Student(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    student_roll_number = db.Column(db.String(20))
    student_department = db.Column(db.String(100))

    student_education = db.Column(db.Text)
    student_skills = db.Column(db.Text)
    student_resume = db.Column(db.String(200)) # Path to resume file

    applications = db.relationship('Application', backref = 'student', lazy = True)
    placements = db.relationship('Placement', backref = 'student', lazy = True) 
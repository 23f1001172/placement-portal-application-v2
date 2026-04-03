from backend.app import db

class Placement(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable = False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable = False)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable = False)

    position = db.Column(db.String(100))
    salary = db.Column(db.String(50))
    placement_date = db.Column(db.DateTime)
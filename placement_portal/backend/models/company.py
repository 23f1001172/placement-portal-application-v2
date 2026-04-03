from backend.app import db

class Company(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    company_name = db.Column(db.String(100), unique = True)
    company_description = db.Column(db.Text)
    company_website = db.Column(db.String(200))
    company_industry = db.Column(db.String(100))
    company_location = db.Column(db.String(100))
    company_email = db.Column(db.String(100))

    jobs = db.relationship('Job', backref = 'company', lazy = True)
    placements = db.relationship('Placement', backref='company', lazy=True)

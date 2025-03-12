from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get(user_id):
        return User.query.get(int(user_id))

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(6), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    active = db.Column(db.String(20), nullable=False, default='not_started')
    questions = db.relationship('Question', backref='exam', lazy=True, cascade="all, delete-orphan")
    scores = db.relationship('Score', backref='exam', lazy=True, cascade="all, delete-orphan")

    def __init__(self, name, created_by):
        self.name = name
        self.created_by = created_by
        self.code = self.generate_unique_code()

    def generate_unique_code(self):
        import random
        import string
        code = ''.join(random.choices(string.digits, k=6))
        while Exam.query.filter_by(code=code).first():
            code = ''.join(random.choices(string.digits, k=6))
        return code

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    question_text = db.Column(db.String(200), nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    option_c = db.Column(db.String(100), nullable=False)
    option_d = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    points = db.Column(db.Integer, nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)

    @staticmethod
    def update_score(exam_id, student_id, points):
        score_entry = Score.query.filter_by(exam_id=exam_id, student_id=student_id).first()
        if score_entry:
            score_entry.score += points
        else:
            score_entry = Score(exam_id=exam_id, student_id=student_id, score=points)
            db.session.add(score_entry)
        db.session.commit()


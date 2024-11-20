from datetime import datetime
from apps.app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from flask import session


# 生徒用
class Student(db.Model, UserMixin):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True)
    email = db.Column(db.String, unique=True, index=True)
    student_number = db.Column(db.String(7), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def password(self):
        raise AttributeError("読み取り不可")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_duplicate_email(self):
        return Student.query.filter_by(email=self.email).first() is not None


# 教師用
class Teacher(db.Model, UserMixin):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    teachername = db.Column(db.String, index=True)
    email = db.Column(db.String, unique=True, index=True)
    password_hash = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def password(self):
        raise AttributeError("読み取り不可")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_duplicate_email(self):
        return Teacher.query.filter_by(email=self.email).first() is not None


@login_manager.user_loader
def load_user(user_id):
    user_type = session.get('user_type')
    if user_type == 'teacher':
        return Teacher.query.get(user_id)
    elif user_type == 'student':
        return Student.query.get(user_id)
    return None


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    # 画像url
    image = db.Column(db.String, nullable=True)
    # 貸出個数
    quantity = db.Column(db.Integer, nullable=False, default=1)
    available = db.Column(db.Boolean, default=True)  
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    teacher = db.relationship('Teacher', backref=db.backref('items', lazy=True))

    def __repr__(self):
        return f'<Item {self.name}>'


class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    loan_date = db.Column(db.DateTime, default=datetime.now)
    return_date = db.Column(db.DateTime, nullable=True)  # 返却予定日
    returned_at = db.Column(db.DateTime, nullable=True)  # 実際の返却日時
    quantity = db.Column(db.Integer, nullable=False, default=1)  # 借りる数量

    item = db.relationship('Item', backref=db.backref('loans', lazy=True))
    student = db.relationship('Student', backref=db.backref('loans', lazy=True))

    def __repr__(self):
        return f'<Loan: {self.student.username} borrowed {self.item.name} (x{self.quantity}) on {self.loan_date}>'

from extensions import db
from flask_login import UserMixin
from datetime import datetime

class Setting(db.Model):
   
    id = db.Column(db.Integer, primary_key=True)
    lms_name = db.Column(db.String(100), default="SZABIT ZABTech iTv")
    lms_logo = db.Column(db.String(100), default="logo.png")
    
    # Dynamic Pages Fields
    about_content = db.Column(db.Text, default="Benazir Bhutto Shaheed Human Resource Research & Development Board (BBSHRRDB) was established to empower the youth of Sindh with technical expertise.")
    training_content = db.Column(db.Text, default="We offer advanced high-tech certifications including Full-Stack Development, AI, Robotics, and IoT automation mapping workflows.")
    research_content = db.Column(db.Text, default="Our research division focuses on human capital optimization metrics and industrial career alignment statistics logs.")
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False) # admin, instructor, staff, student
    is_approved = db.Column(db.Boolean, default=False) # False by default for self-registered students

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    instructor = db.relationship('User', backref='courses_taught')

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    student = db.relationship('User', backref='enrollments')
    course = db.relationship('Course', backref='enrolled_students')

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    file_path = db.Column(db.String(255), nullable=True) # PDF/Notes
    video_link = db.Column(db.String(255), nullable=True)
    
    course = db.relationship('Course', backref='materials')

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    course = db.relationship('Course', backref='assignments')

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    assignment = db.relationship('Assignment', backref='submissions')
    student = db.relationship('User', backref='submissions')
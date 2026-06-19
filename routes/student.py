import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from extensions import db
from models import Course, Enrollment, Assignment, Submission
from flask_login import current_user
from routes import role_required
from werkzeug.utils import secure_filename

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@role_required('student')
def dashboard():
    enrolled_ids = [e.course_id for e in current_user.enrollments]
    my_courses = Course.query.filter(Course.id.in_(enrolled_ids)).all() if enrolled_ids else []
    available_courses = Course.query.filter(~Course.id.in_(enrolled_ids)).all() if enrolled_ids else Course.query.all()

    return render_template('student_dashboard.html', my_courses=my_courses, available_courses=available_courses)

@student_bp.route('/course/enroll/<int:course_id>')
@role_required('student')
def enroll(course_id):
    existing = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if not existing:
        new_enrollment = Enrollment(student_id=current_user.id, course_id=course_id)
        db.session.add(new_enrollment)
        db.session.commit()
        flash('Enrolled into course module successfully.', 'success')
    return redirect(url_for('student.dashboard'))

@student_bp.route('/assignment/submit/<int:assignment_id>', methods=['POST'])
@role_required('student')
def submit_assignment(assignment_id):
    file = request.files.get('submission_file')
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        dest = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(dest)

        sub = Submission(assignment_id=assignment_id, student_id=current_user.id, file_path=filename)
        db.session.add(sub)
        db.session.commit()
        flash('Assignment response uploaded accurately.', 'success')
    return redirect(url_for('student.dashboard'))
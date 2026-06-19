from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Course, Material, Assignment, Enrollment
from flask_login import current_user
from routes import role_required

instructor_bp = Blueprint('instructor', __name__)

@instructor_bp.route('/dashboard')
@role_required('instructor')
def dashboard():
    my_courses = Course.query.filter_by(instructor_id=current_user.id).all()
    return render_template('instructor_dashboard.html', courses=my_courses)

@instructor_bp.route('/course/<int:course_id>/manage', methods=['GET', 'POST'])
@role_required('instructor')
def manage_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id:
        return "Access Forbidden", 403

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'upload_material':
            title = request.form.get('title')
            link = request.form.get('video_link')
            mat = Material(course_id=course.id, title=title, video_link=link)
            db.session.add(mat)
        elif action == 'create_assignment':
            title = request.form.get('title')
            desc = request.form.get('description')
            assign = Assignment(course_id=course.id, title=title, description=desc)
            db.session.add(assign)
        db.session.commit()
        flash('Content structure updated!', 'success')
        return redirect(url_for('instructor.manage_course', course_id=course.id))

    students = Enrollment.query.filter_by(course_id=course.id).all()
    return render_template('instructor_dashboard.html', course=course, managed_students=students, single_view=True)
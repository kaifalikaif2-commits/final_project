from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import User, Course, Material
from routes import role_required

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/dashboard')
@role_required('staff')
def dashboard():
    all_students = User.query.filter_by(role='student').all()
    all_courses = Course.query.all()
    return render_template('staff_dashboard.html', students=all_students, courses=all_courses)

@staff_bp.route('/course/<int:course_id>/add-material', methods=['POST'])
@role_required('staff')
def staff_add_material(course_id):
    title = request.form.get('title')
    link = request.form.get('video_link')
    mat = Material(course_id=course_id, title=title, video_link=link)
    db.session.add(mat)
    db.session.commit()
    flash('Staff assistant uploaded supplemental course framework.', 'success')
    return redirect(url_for('staff.dashboard'))
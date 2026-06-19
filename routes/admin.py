import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from extensions import db
from models import User, Course, Setting
from routes import role_required
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@role_required('admin')
def dashboard():
    students_count = User.query.filter_by(role='student').count()
    instructors_count = User.query.filter_by(role='instructor').count()
    staff_count = User.query.filter_by(role='staff').count()
    courses_count = Course.query.count()

    pending_students = User.query.filter_by(role='student', is_approved=False).all()
    all_users = User.query.all()
    all_courses = Course.query.all()
    all_instructors = User.query.filter_by(role='instructor', is_approved=True).all()
    
    # CMS Settings fetch kar rahe hain templates par display ke liye
    sys_settings = Setting.query.first()

    return render_template('admin_dashboard.html', 
                           s_count=students_count, i_count=instructors_count, 
                           st_count=staff_count, c_count=courses_count,
                           pending_students=pending_students, users=all_users, 
                           courses=all_courses, instructors=all_instructors,
                           sys_settings=sys_settings)

@admin_bp.route('/user/create', methods=['POST'])
@role_required('admin')
def create_user():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    if User.query.filter_by(email=email).first():
        flash('User email exists.', 'danger')
    else:
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        user = User(name=name, email=email, password=hashed_pw, role=role, is_approved=True)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created successfully for {name} ({role})!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/approve/<int:user_id>')
@role_required('admin')
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    flash(f'User {user.name} approved successfully.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/delete/<int:user_id>')
@role_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User profile removed completely.', 'success')
    return redirect(url_for('admin.dashboard'))

# ==========================================
# USER EDIT/UPDATE ROUTE (CRUD)
# ==========================================
@admin_bp.route('/user/edit/<int:user_id>', methods=['POST'])
@role_required('admin')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    user.name = request.form.get('name')
    user.email = request.form.get('email')
    user.role = request.form.get('role')
    
    password = request.form.get('password')
    if password and password.strip() != "":
        user.password = generate_password_hash(password, method='pbkdf2:sha256')
        
    db.session.commit()
    flash(f"User profile for '{user.name}' updated successfully.", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/course/create', methods=['POST'])
@role_required('admin')
def create_course():
    title = request.form.get('title')
    desc = request.form.get('description')
    category = request.form.get('category')
    inst_id = request.form.get('instructor_id') or None

    new_course = Course(title=title, description=desc, category=category, instructor_id=inst_id)
    db.session.add(new_course)
    db.session.commit()
    flash('New course profile generated.', 'success')
    return redirect(url_for('admin.dashboard'))

# ============================================
# COURSE EDIT/UPDATE ROUTE (CRUD)
# ============================================
@admin_bp.route('/course/edit/<int:course_id>', methods=['POST'])
@role_required('admin')
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    course.title = request.form.get('title')
    course.category = request.form.get('category')
    course.description = request.form.get('description')
    
    inst_id = request.form.get('instructor_id')
    course.instructor_id = int(inst_id) if inst_id else None
    
    db.session.commit()
    flash(f"Course profile '{course.title}' updated successfully.", "success")
    return redirect(url_for('admin.dashboard'))

# ============================================
# NEW ADDITION: COURSE DELETE ROUTE (CRUD)
# ============================================
@admin_bp.route('/course/delete/<int:course_id>')
@role_required('admin')
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    course_title = course.title
    
    db.session.delete(course)
    db.session.commit()
    
    flash(f"Course '{course_title}' has been deleted successfully from the registry.", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/settings/update', methods=['POST'])
@role_required('admin')
def update_settings():
    settings = Setting.query.first()
    if not settings:
        settings = Setting()
        db.session.add(settings)

    lms_name = request.form.get('lms_name')
    file = request.files.get('lms_logo')
    
    about_content = request.form.get('about_content')
    training_content = request.form.get('training_content')
    research_content = request.form.get('research_content')

    if lms_name:
        settings.lms_name = lms_name

    if about_content is not None:
        settings.about_content = about_content
    if training_content is not None:
        settings.training_content = training_content
    if research_content is not None:
        settings.research_content = research_content

    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        settings.lms_logo = filename

    db.session.commit()
    flash('LMS settings and pages content updated successfully.', 'success')
    return redirect(url_for('admin.dashboard'))
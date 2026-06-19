from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if not user.is_approved:
                flash('Your account registration is pending admin approval.', 'warning')
                return redirect(url_for('auth.login'))
            
            login_user(user)
            if user.role == 'admin': return redirect(url_for('admin.dashboard'))
            elif user.role == 'instructor': return redirect(url_for('instructor.dashboard'))
            elif user.role == 'staff': return redirect(url_for('staff.dashboard'))
            elif user.role == 'student': return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid login credentials.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        # Student registration defaults to pending (is_approved=False)
        new_student = User(name=name, email=email, password=hashed_pw, role='student', is_approved=False)
        db.session.add(new_student)
        db.session.commit()
        
        flash('Registration submitted! Please wait for system admin authorization.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))

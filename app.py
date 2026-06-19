import os
from flask import Flask, render_template
from config import Config
from extensions import db, login_manager
from models import User, Setting
from werkzeug.security import generate_password_hash

# Import Blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.instructor import instructor_bp
from routes.staff import staff_bp
from routes.student import student_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure Upload Dir Exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # This works without importing anything extra!
    @app.context_processor
    def inject_settings():
        settings = Setting.query.first()
        if not settings:
            settings = Setting(lms_name="SZABIST ZABTech LMS", lms_logo="logo.png")
        return dict(sys_settings=settings)

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(instructor_bp, url_prefix='/instructor')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(student_bp, url_prefix='/student')

    @app.route('/')
    def index():
        return render_template('index.html')
    @app.route('/about')
    def about():
        from models import Setting
        settings = Setting.query.first()
        return render_template('about.html', content=settings.about_content if settings else "")    
    @app.route('/programs')
    def programs():
        from models import Setting
        settings = Setting.query.first()
        return render_template('programs.html', content=settings.training_content if settings else "")
    @app.route('/research')
    def research():
        from models import Setting
        settings = Setting.query.first()
        return render_template('research.html', content=settings.research_content if settings else "")

    @app.route('/contact')
    def contact():
        return render_template('contact.html')



    # Create Database and default setups
    with app.app_context():
        db.create_all()
        # Seed system configurations if empty
        if not Setting.query.first():
            db.session.add(Setting(lms_name="SZABIST ZABTech LMS"))
        
        # Seed default Admin account if missing
        if not User.query.filter_by(role='admin').first():
            hashed_pw = generate_password_hash('sawerachan@1122', method='pbkdf2:sha256')
            admin_user = User(name='System Admin', email='admin@zabtech.com', password=hashed_pw, role='admin', is_approved=True)
            db.session.add(admin_user)
        db.session.commit()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
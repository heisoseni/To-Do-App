from flask import Flask, flash, redirect, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import re
from urllib.parse import urlparse
from datetime import timedelta

db = SQLAlchemy()
login_manager = LoginManager()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    def __repr__(self):
        return f'<User {self.username}>'


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

    def __repr__(self):
        return f'<Task {self.title}>'



def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'getsugatensho'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days = 15)


    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'


    @app.route("/health/db")
    def health_db():
        try:
            db.session.execute(text('SELECT 1'))
            return {"message": "Database is healthy"}, 200
        except Exception as e:
            return {"message": f"Database is not healthy: {str(e)}"}, 500

    with app.app_context():
        db.create_all()


    def is_safe_local_path(target: str) -> bool:
        if not target:
            return False
        parts = urlparse(target)
        return parts.scheme == "" and parts.netloc == "" and target.startswith("/")


    @app.route('/')
    def index():
        return render_template('index.html')

    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.id.desc()).all()
        return render_template('dashboard.html', tasks=tasks)


    @app.route('/add_task', methods=['POST'])
    @login_required
    def add_task():
        title = (request.form.get('title') or '').strip()

        if not title:
            flash('Task title cannot be empty.', 'error')
            return redirect(url_for('dashboard'))

        new_task = Task(title=title, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()

        flash('Task added successfully!', 'success')
        return redirect(url_for('dashboard'))


    @app.route('/complete_task/<int:task_id>')
    @login_required
    def complete_task(task_id):
        task = Task.query.get_or_404(task_id)

        # Security check: only the owner can modify the task
        if task.user_id != current_user.id:
            flash('You are not allowed to modify this task.', 'error')
            return redirect(url_for('dashboard'))

        task.completed = not task.completed  # Toggle complete status
        db.session.commit()
        return redirect(url_for('dashboard'))


    @app.route('/delete_task/<int:task_id>')
    @login_required
    def delete_task(task_id):
        task = Task.query.get_or_404(task_id)

        # Security check: only the owner can delete the task
        if task.user_id != current_user.id:
            flash('You are not allowed to delete this task.', 'error')
            return redirect(url_for('dashboard'))

        db.session.delete(task)
        db.session.commit()
        flash('Task deleted.', 'success')
        return redirect(url_for('dashboard'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        errors = []

        if request.method == 'POST':
            username = (request.form.get('username') or '').strip()
            email = (request.form.get('email') or '').strip()
            password = request.form.get('password')
            confirm = request.form.get('confirm_password')

            if not (2 <= len(username) <= 80):
                errors.append("Username must be between 2 and 80 characters long.")
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                errors.append("Invalid email address.")
            if not (8 <= len(password) <= 255):
                errors.append("Password must be between 8 and 255 characters long.")
            if password != confirm:
                errors.append("Passwords do not match.")
            if not errors:

                try:
                    pw_hash = generate_password_hash(password)
                    user = User(username=username, email=email, password_hash=pw_hash)
                    db.session.add(user)
                    db.session.commit()

                    flash('Registration successful! Please log in.', 'success')
                    return redirect(url_for('login'))

                except IntegrityError:
                    db.session.rollback()
                    errors.append("Username or email already exists.")
        
        return render_template('register.html', errors=errors)


    @app.route('/login', methods=['GET', 'POST'])
    def login():

        errors = []

        if request.method == 'POST':
            email = (request.form.get('email') or '').strip()
            password = request.form.get('password') or ''

            if not email:
                errors.append("Email is required.")
            if not password:
                errors.append("Password is required.")

            if not errors:
                user = User.query.filter_by(email=email).first()
                if not user or not check_password_hash(user.password_hash, password):
                    errors.append("Invalid email or password.")
                else:                     

                    remember_flag = request.form.get("remember") == "1"
                    login_user(user, remember=remember_flag)
                    flash(f'Login successful!, Welcome {user.username}!', 'success')
                    
                    #urlparse("https://")
                    
                    next_url = request.form.get("next") or request.args.get("next") or ""

                    if is_safe_local_path(next_url):
                        return redirect(next_url)
                    return redirect(url_for('dashboard'))

        return render_template('login.html', errors=errors)


    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'success')
        return redirect(url_for('index'))

    
    @app.route('/change_password', methods = ['GET', 'POST'])
    @login_required
    def change_password():
        errors = []
        
        if request.method == 'POST':
            current_pw = request.form.get("current_password") or ""
            new_pw = request.form.get("new_password") or ""
            confirm_pw = request.form.get("confirm_password") or ""

            if not check_password_hash(current_user.password_hash, current_pw):
                errors.append("Current Password is Incorrect")

            if len(new_pw) < 8:
                errors.append("New Password Needs to be at least 8 Characters")

            if new_pw != confirm_pw:
                errors.append("New Password and Confirmation do not match")

            if not errors:
                current_user.password_hash = generate_password_hash(new_pw)
                db.session.commit()


                flash("Password Changed Successfully", "success")
                return redirect(url_for("dashboard"))

        return render_template('change_password.html', errors=errors)


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug = True)
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(user['id'], user['username'], user['email'], user['role'])
    return None

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM courses WHERE is_published = 1")
    courses = cur.fetchall()
    cur.close()
    return render_template('index.html', courses=courses)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, 'user')",
                       (username, email, password))
            mysql.connection.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Email already exists!', 'danger')
        finally:
            cur.close()
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user and bcrypt.check_password_hash(user['password'], password):
            user_obj = User(user['id'], user['username'], user['email'], user['role'])
            login_user(user_obj)
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        flash('Invalid email or password!', 'danger')
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT c.* FROM courses c 
                   JOIN enrollments e ON c.id = e.course_id 
                   WHERE e.user_id = %s""", (current_user.id,))
    courses = cur.fetchall()
    cur.close()
    return render_template('dashboard.html', courses=courses)

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) as count FROM users")
    users_count = cur.fetchone()
    cur.execute("SELECT COUNT(*) as count FROM courses")
    courses_count = cur.fetchone()
    cur.execute("SELECT COUNT(*) as count FROM enrollments")
    enrollments_count = cur.fetchone()
    cur.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT 5")
    recent_users = cur.fetchall()
    cur.close()
    return render_template('admin/dashboard.html',
                         users_count=users_count['count'],
                         courses_count=courses_count['count'],
                         enrollments_count=enrollments_count['count'],
                         recent_users=recent_users)

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

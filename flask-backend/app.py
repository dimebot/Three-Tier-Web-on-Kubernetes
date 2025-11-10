from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import logging 
import sys
import time
import pymysql
import os

app = Flask(__name__)

db_user = os.getenv("MYSQL_USER")
db_pass = os.getenv("MYSQL_PASSWORD")
db_host = os.getenv("MYSQL_HOST")
db_name = os.getenv("MYSQL_DATABASE")
secretkey = os.getenv("SECRET_KEY")

app.config['SECRET_KEY'] = secretkey

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)  # changed from Text → String(255)
    password = db.Column(db.String(255), nullable=False)


def wait_for_db():
    while True:
        try:
            conn = pymysql.connect(
                host=db_host,
                user=db_user,
                password=db_pass,
                database=db_name
            )
            conn.close()
            print("MySQL is ready!")
            break
        except pymysql.err.OperationalError:
            print("Waiting for MySQL...")
            time.sleep(2)

# Initialize database on module import
wait_for_db()
with app.app_context():
    db.create_all()
    print("Tables created successfully.")

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        # Nginx or a proxy sets this header with the original client IP
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        ip = request.remote_addr  # fallback
    return ip

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Configure logging to both stdout and file
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# File handler
file_handler = logging.FileHandler('logs/flask_app.log')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Stream handler (stdout)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(stream_formatter)

# Add both handlers to logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        ip = get_client_ip()  # get actual IP

        if not user or not check_password_hash(user.password, password):
            logger.warning(f'Failed login attempt for {username} from IP {ip}')
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

        login_user(user)
        logger.info(f'{username} logged in successfully from IP {ip}')
        return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html', username=current_user.username)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
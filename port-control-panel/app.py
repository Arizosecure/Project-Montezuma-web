from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create the database and add a default admin user
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        hashed_password = generate_password_hash('admin', method='sha256')
        new_user = User(username='admin', password=hashed_password, role='admin')
        db.session.add(new_user)
        db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/block_website', methods=['POST'])
@login_required
def block_website():
    if current_user.role != 'admin':
        flash('Unauthorized action')
        return redirect(url_for('index'))
    website = request.form['website']
    subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-p', 'tcp', '-d', website, '--dport', '80', '-j', 'DROP'])
    subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-p', 'tcp', '-d', website, '--dport', '443', '-j', 'DROP'])
    flash(f'Blocked {website}')
    return redirect(url_for('index'))

@app.route('/unblock_website', methods=['POST'])
@login_required
def unblock_website():
    if current_user.role != 'admin':
        flash('Unauthorized action')
        return redirect(url_for('index'))
    website = request.form['website']
    subprocess.run(['sudo', 'iptables', '-D', 'OUTPUT', '-p', 'tcp', '-d', website, '--dport', '80', '-j', 'DROP'])
    subprocess.run(['sudo', 'iptables', '-D', 'OUTPUT', '-p', 'tcp', '-d', website, '--dport', '443', '-j', 'DROP'])
    flash(f'Unblocked {website}')
    return redirect(url_for('index'))

@app.route('/block_port', methods=['POST'])
@login_required
def block_port():
    if current_user.role != 'admin':
        flash('Unauthorized action')
        return redirect(url_for('index'))
    port = request.form['port']
    protocol = request.form['protocol']
    subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-p', protocol, '--dport', port, '-j', 'DROP'])
    flash(f'Blocked port {port}/{protocol}')
    return redirect(url_for('index'))

@app.route('/unblock_port', methods=['POST'])
@login_required
def unblock_port():
    if current_user.role != 'admin':
        flash('Unauthorized action')
        return redirect(url_for('index'))
    port = request.form['port']
    protocol = request.form['protocol']
    subprocess.run(['sudo', 'iptables', '-D', 'INPUT', '-p', protocol, '--dport', port, '-j', 'DROP'])
    flash(f'Unblocked port {port}/{protocol}')
    return redirect(url_for('index'))

@app.route('/update_code', methods=['POST'])
@login_required
def update_code():
    if current_user.role != 'admin':
        flash('Unauthorized action')
        return redirect(url_for('index'))
    secret_key = request.form['secret_key']
    if secret_key != 'your_update_secret_key':
        flash('Invalid secret key')
        return redirect(url_for('index'))
    
    try:
        output = subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, text=True, cwd='/path/to/your/project')
        flash(f'Update successful: {output.stdout}')
    except subprocess.CalledProcessError as e:
        flash(f'Update failed: {e.stderr}')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

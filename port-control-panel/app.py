from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from functools import wraps
import subprocess
import requests
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

from models import User, Log
from forms import LoginForm, DomainForm, PortForm, UpdateForm, UserForm

BLOCKLIST_URL = 'https://raw.githubusercontent.com/your-repo/blocklist/main/domains.txt'
UPDATE_KEY_URL = 'https://raw.githubusercontent.com/your-repo/update-key/main/key.txt'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    domain_form = DomainForm()
    port_form = PortForm()
    update_form = UpdateForm()
    return render_template('index.html', domain_form=domain_form, port_form=port_form, update_form=update_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['logged_in'] = True
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            log_action(f"User {user.username} logged in")
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/block_domain', methods=['POST'])
@login_required
def block_domain():
    form = DomainForm()
    if form.validate_on_submit():
        domain = form.domain.data
        duration = form.duration.data
        expiration = datetime.datetime.now() + datetime.timedelta(minutes=duration)
        subprocess.run(['iptables', '-A', 'OUTPUT', '-p', 'tcp', '--dport', '53', '-m', 'string', '--string', domain, '--algo', 'bm', '-j', 'DROP'])
        log_action(f"Blocked domain: {domain} for {duration} minutes")
        send_email(f"Domain Blocked: {domain}", f"The domain {domain} has been blocked for {duration} minutes.")
        return redirect(url_for('index'))
    return render_template('index.html', domain_form=form)

@app.route('/unblock_domain', methods=['POST'])
@login_required
def unblock_domain():
    form = DomainForm()
    if form.validate_on_submit():
        domain = form.domain.data
        subprocess.run(['iptables', '-D', 'OUTPUT', '-p', 'tcp', '--dport', '53', '-m', 'string', '--string', domain, '--algo', 'bm', '-j', 'DROP'])
        log_action(f"Unblocked domain: {domain}")
        send_email(f"Domain Unblocked: {domain}", f"The domain {domain} has been unblocked.")
        return redirect(url_for('index'))
    return render_template('index.html', domain_form=form)

@app.route('/block_port', methods=['POST'])
@login_required
def block_port():
    form = PortForm()
    if form.validate_on_submit():
        port = form.port.data
        protocol = form.protocol.data
        duration = form.duration.data
        expiration = datetime.datetime.now() + datetime.timedelta(minutes=duration)
        subprocess.run(['iptables', '-A', 'INPUT', '-p', protocol, '--dport', port, '-j', 'DROP'])
        log_action(f"Blocked port: {port}/{protocol} for {duration} minutes")
        send_email(f"Port Blocked: {port}/{protocol}", f"The port {port}/{protocol} has been blocked for {duration} minutes.")
        return redirect(url_for('index'))
    return render_template('index.html', port_form=form)

@app.route('/unblock_port', methods=['POST'])
@login_required
def unblock_port():
    form = PortForm()
    if form.validate_on_submit():
        port = form.port.data
        protocol = form.protocol.data
        subprocess.run(['iptables', '-D', 'INPUT', '-p', protocol, '--dport', port, '-j', 'DROP'])
        log_action(f"Unblocked port: {port}/{protocol}")
        send_email(f"Port Unblocked: {port}/{protocol}", f"The port {port}/{protocol} has been unblocked.")
        return redirect(url_for('index'))
    return render_template('index.html', port_form=form)

@app.route('/update_blocklist', methods=['POST'])
@login_required
def update_blocklist():
    form = UpdateForm()
    if form.validate_on_submit():
        update_key = requests.get(UPDATE_KEY_URL).text.strip()
        provided_key = form.update_key.data
        if update_key == provided_key:
            blocklist = requests.get(BLOCKLIST_URL).text.strip().split('\n')
            with open('/etc/dnsmasq.d/blocked_domains.conf', 'w') as f:
                for domain in blocklist:
                    f.write(f'address=/{domain}/0.0.0.0\n')
            subprocess.run(['systemctl', 'restart', 'dnsmasq'])
            log_action("Updated blocklist")
            send_email("Blocklist Updated", "The blocklist has been updated successfully.")
            flash('Blocklist updated successfully', 'success')
        else:
            flash('Invalid update key', 'danger')
    return redirect(url_for('index'))

@app.route('/manage_users', methods=['GET', 'POST'])
@admin_required
def manage_users():
    form = UserForm()
    users = User.query.all()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        log_action(f"Created user: {form.username.data}")
        send_email("New User Created", f"A new user {form.username.data} has been created.")
        return redirect(url_for('manage_users'))
    return render_template('manage_users.html', form=form, users=users)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    log_action(f"Deleted user: {user.username}")
    send_email("User Deleted", f"The user {user.username} has been deleted.")
    return redirect(url_for('manage_users'))

@app.route('/logs')
@admin_required
def view_logs():
    logs = Log.query.order_by(Log.timestamp.desc()).all()
    return render_template('logs.html', logs=logs)

def log_action(action):
    user_id = session.get('user_id')
    log = Log(user_id=user_id, action=action)
    db.session.add(log)
    db.session.commit()

def send_email(subject, body):
    msg = Message(subject, recipients=[app.config['MAIL_DEFAULT_SENDER']])
    msg.body = body
    mail.send(msg)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

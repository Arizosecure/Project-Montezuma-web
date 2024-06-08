from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_mail import Mail, Message
import os
import subprocess  # For ufw commands (use cautiously)

app = Flask(__name__)

# Securely store blocklist using environment variable
BLOCKLIST_FILE = os.getenv('BLOCKLIST_FILE', 'blocklist.txt')

def read_blocklist():
    with open(BLOCKLIST_FILE, 'r') as f:
        return [line.strip() for line in f.readlines()]

def write_blocklist(domains):
    with open(BLOCKLIST_FILE, 'w') as f:
        f.writelines(domain + '\n' for domain in domains)

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    # Implement methods for password verification, etc. (optional)

login_manager = LoginManager()
login_manager.init_app(app)

# Email configuration
app.config['MAIL_SERVER'] = 'your_smtp_server'  # Replace with your actual SMTP server details
app.config['MAIL_PORT'] = 587  # Adjust for your SMTP server
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'

mail = Mail(app)

@app.route('/')
@login_required
def home():
    blocked_domains = read_blocklist()
    return render_template('home.html', blocked_domains=blocked_domains)

@app.route('/manage_domains')
@login_required
def manage_domains():
    blocked_domains = read_blocklist()
    return render_template('manage_domains.html', blocked_domains=blocked_domains)

# ... other routes for adding, removing, updating blocklist (same logic)

@app.route('/ports')
@login_required
def ports():
    # Get current firewall rules (careful with parsing output)
    output = subprocess.check_output(['ufw', 'status']).decode()
    allowed_ports = []
    for line in output.splitlines():
        if line.startswith('Allow'):
            allowed_ports.append(line.split()[1])  # Extract port number
    return render_template('ports.html', allowed_ports=allowed_ports)

# ... other port management routes (same logic)

@app.route('/users')
@login_required
def users():
    # Implement user management logic (add/remove/edit users)
    return render_template('users.html')

# ... login and logout routes (same logic)

@app.route('/support')
@login_required
def support():
    return render_template('support.html')

@app.route('/send_support_email', methods=['POST'])
@login_required
def send_support_email():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if name and email and message:
        msg = Message('Support Request from Domain Blocker', sender=email, recipients=['support@arizosecure.com'])
        msg.body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        try:
            mail.send(msg)
            message = 'Your support request has been sent successfully.'
        except Exception as e:
            message = f'Error sending email: {e}'
    else:
        message = 'Please fill out all fields.'
from git import Repo

def check_for_update():
    repo = Repo('.')  # Initialize the Git repository object

    # Check for remote updates (adjust URL and branch if needed)
    remote = repo.remote('origin')
    remote.update(fetch=True)

    # Compare local commit hash with remote branch head
    current_hash = repo.head.commit.hexsha
    remote_hash = remote.refs.master.commit.hexsha

    return current_hash != remote_hash

if check_for_update():
    message = 'A new update is available!'
else:
    message = 'You are using the latest version.'

    return render_template('support.html', message=message)
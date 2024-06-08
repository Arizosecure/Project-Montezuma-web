from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_mail import Mail, Message
import os
import subprocess  # For ufw commands (use cautiously)
from git import Repo

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Ensure this is securely set in your environment

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

# Mock user database
users = {
    'admin': User(id=1, username='admin', password='password')
}

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None

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
    update_message = check_for_update_message()
    return render_template('home.html', blocked_domains=blocked_domains, update_message=update_message)

@app.route('/manage_domains', methods=['GET', 'POST'])
@login_required
def manage_domains():
    if request.method == 'POST':
        new_domain = request.form.get('domain')
        if new_domain:
            blocked_domains = read_blocklist()
            blocked_domains.append(new_domain)
            write_blocklist(blocked_domains)
            return redirect(url_for('manage_domains'))
    blocked_domains = read_blocklist()
    return render_template('manage_domains.html', blocked_domains=blocked_domains)

@app.route('/remove_domain', methods=['POST'])
@login_required
def remove_domain():
    domain_to_remove = request.form.get('domain')
    blocked_domains = read_blocklist()
    if domain_to_remove in blocked_domains:
        blocked_domains.remove(domain_to_remove)
        write_blocklist(blocked_domains)
    return redirect(url_for('manage_domains'))

@app.route('/ports')
@login_required
def ports():
    output = subprocess.check_output(['ufw', 'status']).decode()
    allowed_ports = [line.split()[1] for line in output.splitlines() if line.startswith('Allow')]
    return render_template('ports.html', allowed_ports=allowed_ports)

@app.route('/users')
@login_required
def users_page():  # Renamed users() to users_page() to avoid name conflict
    return render_template('users.html', users=users.values())

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
            feedback = 'Your support request has been sent successfully.'
        except Exception as e:
            feedback = f'Error sending email: {e}'
    else:
        feedback = 'Please fill out all fields.'
    return render_template('support.html', message=feedback)

def check_for_update():
    repo = Repo('.')  # Initialize the Git repository object
    remote = repo.remote('origin')
    remote.update(fetch=True)
    current_hash = repo.head.commit.hexsha
    remote_hash = remote.refs.master.commit.hexsha
    return current_hash != remote_hash

def check_for_update_message():
    if check_for_update():
        return 'A new update is available!'
    else:
        return 'You are using the latest version.'

if __name__ == "__main__":
    app.run(debug=True)

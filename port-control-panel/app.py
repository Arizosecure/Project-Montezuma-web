from flask import Flask, request, jsonify, session, render_template
import subprocess

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Sample users dictionary for basic authentication
users = {'admin': 'password'}

# Define the command to enable guest network isolation
enable_command = "sudo iptables -A FORWARD -i eth1 -o eth0 -j DROP"

# Define the command to disable guest network isolation
disable_command = "sudo iptables -D FORWARD -i eth1 -o eth0 -j DROP"

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', message=None)
    return render_template('index.html', message=None)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username] == password:
        session['username'] = username
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/allow_port', methods=['GET'])
def allow_port():
    if 'username' not in session:
        return "Unauthorized", 401
    port = request.args.get('port')
    protocol = request.args.get('protocol', 'tcp')  # Default to 'tcp' if not specified
    if not port or not port.isdigit() or not (1 <= int(port) <= 65535):
        return "Invalid port number", 400
    try:
        subprocess.run(['ufw', 'allow', f'{port}/{protocol}'], check=True)
        return f"Port {port}/{protocol} is allowed"
    except subprocess.CalledProcessError:
        return f"Failed to allow port {port}/{protocol}", 500

@app.route('/deny_port', methods=['GET'])
def deny_port():
    if 'username' not in session:
        return "Unauthorized", 401
    port = request.args.get('port')
    protocol = request.args.get('protocol', 'tcp')  # Default to 'tcp' if not specified
    if not port or not port.isdigit() or not (1 <= int(port) <= 65535):
        return "Invalid port number", 400
    try:
        subprocess.run(['ufw', 'deny', f'{port}/{protocol}'], check=True)
        return f"Port {port}/{protocol} is denied"
    except subprocess.CalledProcessError:
        return f"Failed to deny port {port}/{protocol}", 500

@app.route('/get_ufw_rules', methods=['GET'])
def get_ufw_rules():
    if 'username' not in session:
        return "Unauthorized", 401
    try:
        result = subprocess.run(['ufw', 'status', 'verbose'], check=True, stdout=subprocess.PIPE)
        return result.stdout.decode()
    except subprocess.CalledProcessError:
        return "Failed to get UFW rules", 500

@app.route('/guest_network', methods=['POST'])
def guest_network_control():
    if 'username' not in session:
        return "Unauthorized", 401
    switch_status = request.form.get('switch')
    if switch_status == 'on':
        subprocess.run(enable_command.split())
        message = "Guest network isolation enabled."
    else:
        subprocess.run(disable_command.split())
        message = "Guest network isolation disabled."
    return render_template('index.html', message=message)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return "Logged out"

if __name__ == '__main__':
    app.run(debug=True)


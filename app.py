from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
import subprocess
import os
import threading
import time

# Flask app and Socket.IO initialization
template_dir = os.path.abspath('./web/templates')
app = Flask(__name__, template_folder=template_dir)
socketio = SocketIO(app, cors_allowed_origins="*")

# Track ongoing processes and client activity
processes = {}
last_activity = {}
ABANDON_TIMEOUT = 300  # 5 minutes of inactivity

@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html")

@app.errorhandler(500)
def server_error(e):
    return render_template("errors/500.html")

@app.route('/sherlock')
def index():
    return render_template('sherlock-ui/index.html')

@app.route('/sherlock/run', methods=['POST'])
def run_sherlock():
    data = request.json
    username = data.get('username')
    nsfw_option = '--nsfw' if data.get('nsfw') else ''

    if not username:
        return jsonify({"error": "The 'username' field is required"}), 400

    # Command to run Sherlock
    command = f"sherlock {username} {nsfw_option} --print-found"
    print(f"Command executed: {command}")

    # Capture client IP and start the subprocess
    client_ip = request.remote_addr
    process = subprocess.Popen(
        command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Track the process and activity for the client
    processes[client_ip] = process
    last_activity[client_ip] = time.time()


    def stream_logs():
        for line in process.stdout:
            #print(f"Log sent: {line.strip()}")  # Debugging
            socketio.emit('log', {'data': line.strip()}, to=client_ip)
            last_activity[client_ip] = time.time()  # Update last activity

        process.wait()
        print("[Sherlock] Search completed.")
        if client_ip in processes:
            del processes[client_ip]
            del last_activity[client_ip]
        socketio.emit('log_done', {'data': 'Search completed'}, to=client_ip)

    threading.Thread(target=stream_logs).start()
    return redirect(url_for('logs'))

@app.route('/sherlock/logs')
def logs():
    return render_template('sherlock-ui/logs.html')

@socketio.on('connect')
def handle_connect():
    client_ip = request.remote_addr
    join_room(client_ip)  # Associate the client with a room
    print(f'[SocketIO] Client {client_ip} connected.')

@socketio.on('disconnect')
def handle_disconnect():
    client_ip = request.remote_addr
    print(f'[SocketIO] Client {client_ip} disconnected.')

    # Clean up process if the client disconnects
    if client_ip in processes:
        processes[client_ip].kill()
        del processes[client_ip]
        if client_ip in last_activity:
            del last_activity[client_ip]
        print(f'[SocketIO] Process for {client_ip} terminated due to disconnection.')

# Thread to clean up abandoned processes
def cleanup_abandoned_processes():
    while True:
        current_time = time.time()
        to_terminate = []

        for client_ip, last_time in last_activity.items():
            if current_time - last_time > ABANDON_TIMEOUT:
                to_terminate.append(client_ip)

        for client_ip in to_terminate:
            if client_ip in processes:
                print(f'[Sherlock] Terminating abandoned process for {client_ip}.')
                processes[client_ip].kill()
                del processes[client_ip]
                del last_activity[client_ip]

        time.sleep(10)

# Start the cleanup thread
cleanup_thread = threading.Thread(target=cleanup_abandoned_processes, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    import os
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')  # Default: listening on all interfaces
    port = int(os.getenv('FLASK_RUN_PORT', 5000))  # Default: port 5000
    socketio.run(app, host=host, port=port)

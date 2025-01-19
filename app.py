from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import subprocess
import os
import threading

template_dir = os.path.abspath('./web/templates')
app = Flask(__name__, template_folder=template_dir)
socketio = SocketIO(app)

# Dictionnaire pour suivre les processus en cours
processes = {}

@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('errors/500.html'), 500

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
    command = f"python3 sherlock/sherlock.py {username} {nsfw_option} --print-all"
    print(f"Command executed: {command}")

    # Launch the command in a separate thread
    process = subprocess.Popen(
        command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Save the process by session or unique ID
    processes[request.remote_addr] = process

    def stream_logs():
        for line in process.stdout:
            socketio.emit('log', {'data': line}, room=request.remote_addr)
        process.wait()
        del processes[request.remote_addr]  # Clean up when done
        socketio.emit('log_done', {'data': 'Recherche terminée'}, room=request.remote_addr)

    threading.Thread(target=stream_logs).start()
    return redirect(url_for('logs'))

@app.route('/sherlock/logs')
def logs():
    return render_template('sherlock-ui/logs.html')

@socketio.on('connect')
def handle_connect():
    print('[Sherlock] Client connected.')

@socketio.on('disconnect')
def handle_disconnect():
    client_ip = request.remote_addr
    print('[Sherlock] Client disconnected.')

    # Kill the process if it exists
    if client_ip in processes:
        processes[client_ip].kill()
        del processes[client_ip]
        print(f'[Sherlock] Process for {client_ip} terminated.')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=80)

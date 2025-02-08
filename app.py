from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
from flask_socketio import SocketIO, emit, join_room
import subprocess
import os
import threading
import time
import uuid  # Generate unique session IDs

# Get absolute path for templates directory
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, "web/templates")

# Check if Flask sees the template directory
template_path = os.path.join(os.getcwd(), template_dir)
print(f" * Checking template path: {template_path}")
print(" * Templates found:", os.listdir(template_path))

def detect_sherlock_command():
    """Detect whether Sherlock is available as a Python module or a CLI command."""
    try:
        subprocess.run(["python3", "-m", "sherlock", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("[INFO] Using Python module for Sherlock.")
        return "python3 -m sherlock"
    except subprocess.CalledProcessError:
        try:
            subprocess.run(["sherlock", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("[INFO] Using Sherlock CLI command.")
            return "sherlock"
        except subprocess.CalledProcessError:
            print("[ERROR] Sherlock is not installed.")
            return None


app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.urandom(24)  # Secure random secret key
socketio = SocketIO(app, cors_allowed_origins="*")

processes = {}
last_activity = {}
ABANDON_TIMEOUT = 300  # 5 minutes

@app.route('/')
def home(): 
    return redirect(url_for('home_sherlock'))

@app.route('/sherlock-run')
def sherlock_run_failUrl():
    return redirect(url_for('home_sherlock'))

@app.route('/sherlock')
def home_sherlock():
    return render_template('sherlock-ui/index.html')

@app.route('/sherlock/run', methods=['POST'])
def run_sherlock():
    data = request.json
    username = data.get('username')
    nsfw_option = '--nsfw' if data.get('nsfw') else ''

    if not username:
        return jsonify({"error": "The 'username' field is required"}), 400

    # Detect the correct command for Sherlock
    sherlock_command = detect_sherlock_command()
    if not sherlock_command:
        return jsonify({"error": "Sherlock is not installed correctly."}), 500

    # Generate session ID and store username in session
    session_id = str(uuid.uuid4())
    session['id'] = session_id
    session['username'] = username  # Store username for deletion

    # Construct the full command
    output_dir = os.path.join(base_dir, "sherlock_output")  # Inside project folder
    os.makedirs(output_dir, exist_ok=True)  # Ensure the folder exists
    output_file = os.path.join(output_dir, f"{session_id}-{username}.txt")

    command = f"{sherlock_command} {username} {nsfw_option} --print-found --output {output_file}"
    print(f"[SECURE] Executing: {command}")

    process = subprocess.Popen(
        command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Real-time output
    )

    processes[session_id] = process
    last_activity[session_id] = time.time()

    def stream_logs(session_id, process):
        print(f"[DEBUG] Streaming logs for session {session_id}...")

        for line in process.stdout:
            if session_id not in processes:
                print(f"[DEBUG] Stopping log stream for session {session_id} (client disconnected)")
                return

            print(f"[LOG] {line.strip()}")  # Log output for debugging
            socketio.emit("log", {"data": line.strip()}, to=session_id)
            last_activity[session_id] = time.time()

        process.wait()
        print(f"[DEBUG] Sherlock process finished for session {session_id}")

        if session_id in processes:
            del processes[session_id]
            del last_activity[session_id]

        socketio.emit("log_done", {"data": "Search completed"}, to=session_id)

    threading.Thread(target=stream_logs, args=(session_id, process)).start()

    response = jsonify({"message": "Search started"})
    response.set_cookie("session_id", session_id, httponly=True, secure=False, samesite="Lax")
    print(f"Setting Cookie: session_id={session_id}")
    return response

@app.route('/sherlock/run')
def logs():
    session_id = request.cookies.get("session_id")
    print(f"[DEBUG] Retrieved session_id from cookie: {session_id}")  # Debugging

    if not session_id:
        return "Session not found. Please restart the search.", 400

    return render_template('sherlock-ui/run.html', session_id=session_id)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('errors/500.html'), 500

@socketio.on('connect')
def handle_connect():
    session_id = request.cookies.get("session_id")
    if session_id:
        join_room(session_id)
        print(f'[SocketIO] Client <{session_id}> connected.')

@socketio.on('disconnect')
def handle_disconnect():
    session_id = session.get('id')
    username = session.get('username')  # Retrieve the username stored in session

    print(f'[SocketIO] Client {session_id} disconnected.')

    if session_id in processes:
        print(f"[DEBUG] Terminating process for session {session_id} (User left the page)")
        processes[session_id].kill()  # Kill the subprocess
        del processes[session_id]

        # Delete the output file
        output_dir = "/sherlock_output/"
        output_file = os.path.join(output_dir, f"{session_id}-{username}.txt")

        if os.path.exists(output_file):
            try:
                os.remove(output_file)
                print(f"[INFO] Deleted output file: {output_file}")
            except Exception as e:
                print(f"[ERROR] Failed to delete {output_file}: {e}")

    if session_id in last_activity:
        del last_activity[session_id]

if __name__ == '__main__':
    socketio.run(app.run(debug=True), host='0.0.0.0', port=5000)

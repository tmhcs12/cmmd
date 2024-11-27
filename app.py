import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import subprocess

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('execute_command')
def handle_command(command):
    try:
        print(f"Executing command: {command}")  # Debugging print
        # Run command with text=True to avoid byte-to-str conversion issues
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        # Debug prints to log output and errors
        if stdout:
            print(f"Command output: {stdout}")
            emit('command_output', {'output': stdout})
        if stderr:
            print(f"Command error: {stderr}")
            emit('command_output', {'output': stderr})
        if not stdout and not stderr:
            emit('command_output', {'output': "Command executed successfully with no output."})

    except Exception as e:
        print(f"Error executing command: {str(e)}")
        emit('command_output', {'output': f"Error executing command: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    print("Starting server...")
    socketio.run(app, host='127.1.1.1', port=port, debug=True)

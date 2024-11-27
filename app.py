import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import subprocess

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow connections from any origin

# Route to serve the terminal HTML page
@app.route('/')
def index():
    return render_template('index.html')

# SocketIO event to handle commands from the client
@socketio.on('execute_command')
def handle_command(command):
    try:
        # Execute the command in the shell
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Send back the output and error (if any) to the client
        if stdout:
            emit('command_output', {'output': stdout.decode('utf-8')})
        if stderr:
            emit('command_output', {'output': stderr.decode('utf-8')})
    
    except Exception as e:
        emit('command_output', {'output': f"Error executing command: {str(e)}"})

# Main entry point to run the app
if __name__ == "__main__":
    # Use the port from the environment or default to 8000
    port = int(os.environ.get('PORT', 8000))
    # Run the app without specifying 'eventlet' or 'gevent'
    socketio.run(app, host='0.0.0.0', port=port, debug=True)

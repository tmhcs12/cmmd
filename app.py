from flask import Flask, render_template
import paramiko
import os

app = Flask(__name__)

# SSH configuration (ensure these are correct)
ssh_host = 'sgp.domcloud.co'
ssh_port = 22
ssh_user = 'fastscan-promax'
ssh_password = 'Chomulal123'

def run_remote_command():
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the remote server
        print("Connecting to the server...")
        ssh.connect(hostname=ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)
        print("Connected successfully.")
        
        # Command to change directory and run the Python script
        command = 'cd public_html/scan && python fastscan-7to7ff.py'
        print(f"Executing command: {command}")
        
        # Run the command and capture output
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # Read output and errors
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        ssh.close()
        
        # Check if there are any errors
        if error:
            print(f"Error: {error}")
            return f"Error: {error}"
        else:
            print(f"Output: {output}")
            return output

    except Exception as e:
        print(f"Connection Error: {str(e)}")
        return f"Connection Error: {str(e)}"

@app.route('/')
def index():
    # Run the remote command and get the result
    output = run_remote_command()
    return render_template('index.html', output=output)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)

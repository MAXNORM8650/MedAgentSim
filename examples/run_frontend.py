import os
import subprocess

working_dir = os.getcwd()

# Constants
FRONTEND_SCRIPT_PATH = f"{working_dir}\\Simulacra\\environment\\frontend_server"
FRONTEND_SCRIPT_FILE = "manage.py"
DEFAULT_PORT = 8000

def run_frontend_server(port=None):
    port = port or DEFAULT_PORT
    file_name = "Python-Script-Frontend"
    print(f"({file_name}): Running frontend server")

    # Change to the frontend script directory
    frontend_path = os.path.abspath(FRONTEND_SCRIPT_PATH)
    os.chdir(frontend_path)

    print(f"({file_name}): Changed directory to {frontend_path}")

    # Run the server
    try:
        manage_py_path = os.path.join(frontend_path, FRONTEND_SCRIPT_FILE)

        # Form the command
        command = f'python "{manage_py_path}" runserver {port}'
        print(f"({file_name}): Executing command: {command}")

        # Run the command
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Print the output
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        if result.returncode != 0:
            print(f"({file_name}): Failed to run server with return code {result.returncode}")
        else:
            print(f"({file_name}): Server started successfully on port {port}")

    except Exception as e:
        print(f"({file_name}): An error occurred: {e}")

run_frontend_server(port=None)
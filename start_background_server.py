import subprocess
import os
import sys

def start_server_background():
    """Start the banking system server in the background"""
    # Get the path to python executable
    python_exe = sys.executable
    
    # Path to the main.py file
    main_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    
    # Start the server as a detached process
    if os.name == 'nt':  # Windows
        # Use subprocess.CREATE_NEW_CONSOLE to create a new console window that will run in background
        process = subprocess.Popen(
            [python_exe, main_script],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
 
        # Use nohup to run the process in the background
    process = subprocess.Popen(
        f"nohup {python_exe} {main_script} > server.log 2>&1 &",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print(f"Server started in background (PID: {process.pid})")
    return process.pid

if __name__ == "__main__":
    start_server_background()
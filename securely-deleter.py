import psutil
import time

PROCESS_NAME = "Classroom.exe"  # Process to terminate

def kill_process_by_name(process_name):
    """Terminate a process by its name if it exists."""
    for process in psutil.process_iter(attrs=["pid", "name"]):
        if process.info["name"] == process_name:
            try:
                process.terminate()  # Attempt to terminate the process
                print(f"Terminated {process_name} with PID {process.info['pid']}")
            except psutil.NoSuchProcess:
                print("Process no longer exists.")
            except psutil.AccessDenied:
                print("Access denied to terminate process.")
            except Exception as e:
                print(f"Error terminating process: {e}")

# Main loop to keep checking for the process
while True:
    kill_process_by_name(PROCESS_NAME)
    time.sleep(1)  # Adjust frequency as needed (1 second here)

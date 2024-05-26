import subprocess
import signal

def run_inetsim(timeout):
    process = subprocess.Popen("inetsim -whatever", shell=True, executable="/bin/bash")

    try:
        process.wait(40)  # set timeout
    except subprocess.TimeoutExpired:
        process.send_signal(signal.SIGINT)
        print("terminated")

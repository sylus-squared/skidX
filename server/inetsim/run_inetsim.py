import subprocess
import signal
import os

def run_inetsim(timeout, file_hash):
    if not os.path.exists(file_hash): # There should only be ONE analysis file per sample, this is just to make sure
        os.mkdir(file_hash)

    process = subprocess.Popen(f"sudo inetsim --data data --conf inetsim.conf --report-dir {file_hash}", shell=True, executable="/bin/bash")

    try:
        process.wait(40)  # set timeout
    except subprocess.TimeoutExpired:
        process.send_signal(signal.SIGINT)
        print("terminated")

def get_report(file_hash):
    if not os.path.exists("file_hash"):
        print("Analysis has not been completed yet")
        # Throw some error

    
    
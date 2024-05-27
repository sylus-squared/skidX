import subprocess
import signal
import os
import shutil

class AnalysisNotCompleteError(Exception):
    pass # Thrown when the analysis direcory does not exist (Is this really necessary?)

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
    if not os.path.exists(f"analysis/{file_hash}"):
        print("Analysis has not been completed yet")
        raise AnalysisNotCompleteError

    file = os.listdir(f"analysis/{file_hash}")
    source_dir = os.path.join(os.path.dirname(__file__), f"analysis/{file_hash}/{file[0]}")
    dest_dir = os.path.join(os.path.dirname(__file__), '..', "webserver", "data/")

    print("Source dir: " + source_dir)
    print("Dest dir: " + dest_dir)

    try:
        shutil.copy(source_dir, dest_dir)
    except FileNotFoundError:
        print("File does not exist")
    os.rename(dest_dir + file[0], dest_dir + file_hash + ".txt")

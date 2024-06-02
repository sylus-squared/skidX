"""
This is the client to be deployed on the dirty VM used to dnamically analyze java infostealers pretending to be minecraft mods
This uses a combination of inetsym and self written YARA rules :( to dynamically assess minecraft mods to check if they are malicious or not
Thankfully said mods are written by skids so zero fucks have to be given when it comes to VM stealthiness
The following must be implemented for this to work:
DirtyVM (must be windows and be able to run python 3)
Inetsym server (must be accesable from the VM)
reporting webserver (should be the same as inetsym)

This script must do the following:
Download the latest file from the web server when the VM starts (this is the malicious file and means only one file can be analysed at a time)
Execute the downloded file with a headless minecraft instance (forge and fabric)
Analyse the executed file with self written YARA rules
Encrypt the verdict and send it to the server (needs to be encrypted because there is malware running on the system)
"""
# Switched from portablemc due to the lack of openGL on the client sandbox, headlessMC will be used now 

import subprocess
import requests
import socket
import time
import hashlib
import json
import os

sample_name = ""
analysis_time = 0

class TimeError(Exception):
    pass # This error is thrown with the timeout time for the analysis is less than 40s or more than 180s (3m)

def run_client(timeout):
    if timeout < 40: # The time is measured in seconds
        raise TimeError("Timeout time cannot be lower than 40s")
    elif timeout > 190: # This validation is in case the front end validation fails 
        raise TimeError("Timeout cannot exceed 180s (3m)")

    client_process = subprocess.Popen(['java', '-jar', 'headlessmc-launcher-1.9.0.jar', '-instant'])

    try:
        client_process.wait(40)  # set timeout
    except subprocess.TimeoutExpired:
        subprocess.call(["taskkill", "/F", "/T", "/PID", str(client_process.pid)], shell = True) # This is needed because the
        print("terminated")		           													     # openJDK platform binary wont
                                                                                                 # die when the subprocess is killed
def shutdown():
    pass

def receive_file(server_socket, save_path):
    global sample_name
    global analysis_time
    file_name_and_extension = server_socket.recv(1024).decode() # Receive the file name and extension
    file_name, file_extension = os.path.splitext(file_name_and_extension)

    analysis_time = int(server_socket.recv(1024).decode())

    file_path = os.path.join(save_path, file_name + file_extension)
    if not os.path.exists(save_path):
        os.makedirs(save_path, exist_ok=True)

    with open(file_path, 'wb') as file:
        while True:
            data = server_socket.recv(1024)
            if not data:
                break
            file.write(data)

    print(f"File received and saved as {file_path}")
    sample_name = file_name + file_extension

def listen_for_sample():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((client_ip, port))
    server_socket.listen(1)

    print(f"Server listening on {client_ip}:{port}")

    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")
    file_path = "received_file/"

    receive_file(client_socket, file_path)

    client_socket.close()
    server_socket.close()

def send_result(results): # Used to send the result back to the results server (will be empty for the Proof Of Concept)
    files = {results}
    response = requests.post("http://127.0.0.1:5000/result", files=files)
    print(response.text)

with open("config/config.json", 'r') as read_file:
    config = json.load(read_file)

client_ip = config["connection"]["clientIP"]
port = config["connection"]["serverPort"]

while True:
    listen_for_sample()
    destination_dir = os.path.join(os.getenv('APPDATA'), ".minecraft", "mods")
    destination_path = os.path.join(destination_dir, sample_name)
    os.rename(os.path.join("received_file", sample_name), destination_path)
    # This is just so I don't infect my PC by accident while testing and will be removed soon
    input("WARNING, this could potentially detonate actual malware, are you sure you want to continue?(press enter to continue): ")
    run_client(analysis_time)
    send_result("Coming soon")
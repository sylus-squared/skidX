import socket
import hashlib
import os

def send_file(file_path, server_address, server_port, interfaces_ip, analysis_time):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind((interfaces_ip, 0))

    client_socket.connect((server_address, server_port))

    # Calculate the SHA-256 hash of the file
    file_hash = hashlib.sha256()
    with open(file_path, 'rb') as file:
        file_hash.update(file.read())

    _, file_extension = os.path.splitext(file_path)

    file_name = file_hash.hexdigest() + file_extension # Send the SHA-256 hash as the file name
    client_socket.send(file_name.encode())

    client_socket.send(str(analysis_time).encode())

    # Send the file data
    with open(file_path, 'rb') as file:
        data = file.read(1024)
        while data:
            client_socket.send(data)
            data = file.read(1024)

    client_socket.close()

def upload_file(file_path, config, analysis_time):
    interface_ip = config["connection"]["interface_IP"]
    server_ip = config["connection"]["client_IP"]
    server_port = config["connection"]["port"]
    
    send_file(file_path, server_ip, server_port, interface_ip, analysis_time)
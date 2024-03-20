import socket

def send_file(file_path, server_address, server_port, interfaces_ip):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind((interfaces_ip, 0))

    client_socket.connect((server_address, server_port))

    with open(file_path, 'rb') as file:
        data = file.read(1024)
        while data:
            client_socket.send(data)
            data = file.read(1024)

    client_socket.close()

def upload_file(file_path, config):
    file_to_send = file_path.encode()
    
    interface_ip = config["connection"]["interfaceip"]
        
    server_ip = config["connection"]["clientIP"]
    server_port = config["connection"]["port"]

    send_file(file_to_send, server_ip, server_port, interface_ip)

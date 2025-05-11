import yaml
import os
import socket
import threading
import random
import json
import time

"""
load the config
Listen for the client to connect
Register the client
Listen for the webserver to connect on localhost
"""

clients = {}
first_names = [
    "Unstable",
    "Silent",
    "Happy",
    "Fierce",
    "Ancient",
    "Brave",
    "Mysterious",
    "Wild",
    "Noble",
    "Quick",
    "laughing"
]

second_names = [
    "Lama",
    "Tiger",
    "Falcon",
    "Wolf",
    "Eagle",
    "Fox",
    "Panther",
    "Dragon",
    "Lion",
    "Bear",
    "Zebra"
]

with open("config.yml") as stream:
    try:
        config = yaml.safe_load(stream)
        #print(config)
    except yaml.YAMLError as exc:
        print("[ERROR]: Config not loaded, the program will not be able to continue. Caused by: " + exec)

class Client: # Object that contains all information about the client, I will add more to this at some point
    def __init__(self, ID, ip_address, os_type, hostname, analysis_status):
        self.ID = ID
        self.ip_address = ip_address
        self.os_type = os_type
        self.hostname = hostname
        self.analysis_status = analysis_status

    def set_connection(self, connection):
        self.connection = connection
    
    def set_file(self, file_path):
        self.file_path = file_path

def start_analysis(file_path, client_ID):
    client_object = get_client_object(client_ID)
    client_to_scan = client_object.connection

    response = "Scan this file"
    client_to_scan.sendall(response.encode("utf-8"))
    print("Starting analysis: " + file_path + " on client: " + client_ID)
    time.sleep(10) # Test stuff
    print("Ended analysis: " + file_path)

def stop_analysis():
    pass

def load_machinery():
    pass

def register_client(ID, ip_address, os_type, hostname): # Adds the client information to a list
    clients.update({f"{ID}": Client(f"{ID}", f"{ip_address}", f"{os_type}", f"{hostname}", "Waiting")})
    print("Registered client: " + ID + " with an IP address of: " + str(ip_address))
    # At some point this will do more

def handle_client(client_socket, client_address):
    print(f"[CLIENT LISTENER]: [NEW CONNECTION] {client_address} connected.")
    try:
        while True:
            message = client_socket.recv(1024)
            if not message:
                # Client has disconnected
                print(f"[CLIENT LISTENER]: [DISCONNECTED] {client_address} disconnected.")
                break
            text = message.decode("utf-8")
            print(f"[CLIENT LISTENER]: [{client_address}] {text}") # Temporary code for development
    except ConnectionResetError:
        print(f"[CLIENT LISTENER]: [DISCONNECTED] {client_address} forcibly closed the connection.")
    finally:
        client_socket.close()

def listen_client():
    host = config["client_connection"]["client_listen_IP"]
    port = config["client_connection"]["port"]
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"[CLIENT LISTENER]: [STARTED] Server listening for clients on {host}:{port}")
    try:
        registered = False
        while True:
            client_socket, client_address = server.accept()
            for i in clients.values():
                if i.ip_address == client_address[0]:
                    registered = True
                    break

            if not registered:
                while True: # If all combinations are taken this will get stuck, will fix in future
                    first_name = first_names[random.randint(0, 10)]
                    second_name = second_names[random.randint(0, 10)]
                    if first_name + " " + second_name not in clients:
                        break

            register_client(first_name + " " + second_name, client_address[0], "Windows", "Hostname")
            get_client_object(first_name + " " + second_name).set_connection(client_socket)

            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True)
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[CLIENT LISTENER]: [SHUTDOWN] Server is shutting down.")
    finally:
        server.close()

def handle_webserver(client_socket, client_address):
    print(f"[WEBSERVER LISTENER]: [NEW CONNECTION] {client_address} connected.")
    try:
        while True:
            # Read the command from the client
            message = b""
            while True:
                part = client_socket.recv(1024)
                message += part
                if len(part) < 1024:  # Message is over if less than 1024 bytes have been recived
                    break
            if not message:
                print(f"[WEBSERVER LISTENER]: [DISCONNECTED] {client_address} disconnected.")
                break
            
            text = message.decode("utf-8")
            print(f"[WEBSERVER LISTENER]: [{client_address}] Received: {text}")

            parts = text.split(' ', 1) # Split the command from its options
            command = parts[0] # The format for commands is command [Option1 , Option2]
            if len(parts) > 1:
                options_str = parts[1].strip("[]")
            else:
                options_str = ""
            if options_str:
                options = []
                for option in options_str.split(','):
                    options.append(option.strip())
            else:
                options = []

            if command == "get_all_clients": # Todo, clean this up at some point
                response = json.dumps(get_clients())
                client_socket.sendall(response.encode("utf-8"))
            elif command == "get_client_info": # get_client_info ["ID"]
                response = get_client_info(options[0])
                client_socket.sendall(response.encode("utf-8"))
            elif command == "test_connection":
                response = f"Connected successfully to: {config["backend_connection"]["backend_IP"]} on port: {config["backend_connection"]["port"]}"
                client_socket.sendall(response.encode("utf-8"))
            elif command == "start_analysis": # start_analysis ["ID", Analysis time (Minutes), "Game version", "File name"]
                scan_client = options[0]
                analysis_time = options[1]
                game_version = options[2]
                OS = options[3]
                file_name = options[4] if len(options) > 3 else None
                
                if file_name: # Receive the file
                    file_size_bytes = client_socket.recv(8)
                    file_size = int.from_bytes(file_size_bytes, byteorder="big")
                    with open("scanned_files/" + file_name, "wb") as f:
                        bytes_received = 0
                        while bytes_received < file_size:
                            chunk = client_socket.recv(min(4096, file_size - bytes_received))
                            if not chunk:
                                break
                            f.write(chunk)
                            bytes_received += len(chunk)
                    if get_client_object(scan_client) == None or get_client_info[4] != "Waiting":
                        print("[INFO]: Specified client could not be used, selecting a random client")
                        scan_client = choose_client(OS)
                    if scan_client == None:
                        response = "[ERROR]: No clients registered"
                    else:
                        threading.Thread(target=start_analysis, args=("malicious_files/", scan_client,)).start()
                        response = f"Started analysis on: {scan_client} with file: {file_name}"
                else:
                    response = "No file provided for analysis."
                client_socket.sendall(response.encode("utf-8"))
            else:
                print(f"[WEBSERVER LISTENER]: Unknown command: {command}")
                response = f"Unkown command: {command}"
                client_socket.sendall(response.encode("utf-8"))
    except ConnectionResetError:
        print(f"[WEBSERVER LISTENER]: [DISCONNECTED] {client_address} forcibly closed the connection.")
    except Exception as e:
        print(f"[WEBSERVER LISTENER]: [ERROR] {e}")
    finally:
        client_socket.close()

def listen_webserver():
    host = config["backend_connection"]["backend_IP"]
    port = config["backend_connection"]["port"]
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"[WEBSERVER LISTENER]: [STARTED] Server listening for clients on {host}:{port}")
    try:
        while True:
            client_socket, client_address = server.accept()
            client_thread = threading.Thread(target=handle_webserver, args=(client_socket, client_address), daemon=True)
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[WEBSERVER LISTENER]: [SHUTDOWN] Server is shutting down.")
    finally:
        server.close()

def get_client_object(ID): # Gets a client by its ID and returns the client object
    return clients.get(ID) # Might return None

def get_client_info(ID): # Gets a client by its ID and returns all its info
    client = clients.get(ID)
    return [client.ID, client.ip_address, client.os_type, client.hostname, client.analysis_status]

def get_clients():
    return_list = []
    for i in clients.keys():
        return_list.append(i)
    return return_list

def choose_client(os): # Returns the ID of a client for scanning
    for i in get_clients():
        potential_client = get_client_object(i)
        if potential_client.os_type == os and potential_client.analysis_status == "Waiting":
            return potential_client.ID

threading.Thread(target=listen_client).start()
threading.Thread(target=listen_webserver).start()
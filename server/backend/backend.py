import yaml
import os
import socket
import threading
import random

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
    "Quick"
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
    "Bear"
]


class Client: # Object that contains all information about the client, I will add more to this at some point
    def __init__(self, ID, ip_address, os_type, hostname, analysis_status):
        self.ID = ID
        self.ip_address = ip_address
        self.os_type = os_type
        self.hostname = hostname
        self.analysis_status = analysis_status

with open("config.yml") as stream:
    try:
        config = yaml.safe_load(stream)
        #print(config)
    except yaml.YAMLError as exc:
        print(exc)

def start_analysis():
    pass

def stop_analysis():
    pass

def load_machinery():
    pass

def register_client(ID, ip_address, os_type, hostname): # Adds the client information to a list
    clients.update({f"{ID}": Client(f"{ID}", f"{ip_address}", f"{os_type}", f"{hostname}", "Waiting")})
    print("Registered client: " + ID + " with an IP address of: " + str(ip_address))
    # At some point this will do more

def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")
    try:
        while True:
            message = client_socket.recv(1024)
            if not message:
                # Client has disconnected
                print(f"[DISCONNECTED] {client_address} disconnected.")
                break
            text = message.decode('utf-8')
            print(f"[{client_address}] {text}") # Temporary code for development
    except ConnectionResetError:
        print(f"[DISCONNECTED] {client_address} forcibly closed the connection.")
    finally:
        client_socket.close()

def listen_client():
    host = config["client_connection"]["backend_Listen_IP"]
    port = config["client_connection"]["port"]
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"[STARTED] Server listening for clients on {host}:{port}")
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
                    first_name = first_names[random.randint(1, 10)]
                    second_name = second_names[random.randint(1, 10)]
                    if first_name + " " + second_name not in clients:
                        break
                register_client(first_name + " " + second_name, client_address[0], "Windows", "Hostname")

            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True)
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server is shutting down.")
    finally:
        server.close()

def listen_webserver():
    pass

def get_client_object(ID): # Gets a client by its ID and returns the client object
    return clients.get(ID) # Might return None

def get_client_info(ID): # Gets a client by its ID and returns all its info
    client = clients.get(ID)
    return [client.ID, client.ip_address, client.os_type, client.hostname]

def get_clients():
    return_list = []
    for i in clients.keys():
        return_list.append(i)
    return return_list
        

# ----------------------------------------------------------- TESTING CODE, DO NOT COMMIT
listen_client()
print(get_clients())
#register_client("Unstable Lama", "IP_adress", "os_type", "hostname")
#print(get_client_info("Unstable Lama"))
#print(get_client_object("Unstable Lama").hostname)
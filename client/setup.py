import yaml
import requests
import time
import os
from os.path import exists

"""
The config.yml file is structured as follows:
connection:
    serverIP: <serverIP> # Deafult is 127.0.0.1
    serverPort: 12345 # Deafult is 8080
clientConfig:
    IDK yet

An interface IP is not needed here as its assumed the client only has one interface although I might add
it in the furture if needed

This file installs all the packeges needed for the client as well as setting up the related config files
Eventually it will also download all necacery YARA rules from the server (Coming in V1)

List of packages:
pyyaml
more to come
"""
# This will be worked on as packages are needed, but for now its not necacery
data = {
    'connection': {
        'serverIP': "127.0.0.1",  # Default is 127.0.0.1
        'serverPort': 12345  # Default is 12345
    },
    'clientConfig': {
        'idk': 'idk',
    }
}
if exists("config/config.yml"):
    print("Config file already exists")
else:
    with open("config/config.yml", "w") as file:
        yaml.dump(data, file, default_flow_style=False)

url = 'http://localhost:5000/setup'
filename = 'portablemc.exe'
directory = '/setupFiles'

try:
    response = requests.get(url, params={'filename': filename, 'directory': directory})
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print('File downloaded successfully.')
    else:
        print('[ERROR]: ', response.text)
        input("press enter to quit ")
except:
    print("[ERROR]: webserver most likley offline")
    input("Press enter to quit")

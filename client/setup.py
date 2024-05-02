import yaml
import requests

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

data = {
    'connection': {
        'serverIP': "127.0.0.1", # Deafult is 127.0.0.1
        'serverPort': 12345 # Deafult is 127.0.0.1
    },
    'clientConfig': {
        'idk': 'idk',
    }

}
with open("config.yml", "w") as file:
    yaml.dump(data, file, deafult_flow_style=False)


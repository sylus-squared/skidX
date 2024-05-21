import urllib.request
import time
import os
import zipfile
import json

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
None, the client will operate with deafult packages only (fingers crossed)
"""

data = {
    "connection": {
        "serverIP": "127.0.0.1",
        "serverPort": "12345"
    }
}

if os.path.exists("config/config.json"):
    print("Config file already exists")
else:
    os.mkdir("config")
    with open("config/config.json", "w") as write_file:
     json.dump(data, write_file)
    

with open("config/config.json", "r") as read_file:
    config = json.load(read_file)

serverIP = config["connection"]["serverIP"]

files = ["headlessmc-launcher-1.9.0.jar", "HeadlessMC", ".minecraft"]

url = f"http://{serverIP}:5000/setup"
filename = ""

for filename in files:
    url_to_download = url + "/" + filename
    urllib.request.urlretrieve(url_to_download, filename + ".zip")
    try:
        with zipfile.ZipFile(filename + ".zip", 'r') as zip_ref:
            zip_ref.extractall(filename)
    except:
        pass

os.rename(".minecraft", os.getenv('APPDATA') + "\\.minecraft")
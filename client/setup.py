import urllib.request
import time
import os
import zipfile
import json
import random
import ctypes
import shutil
import sys

"""
An interface IP is not needed here as its assumed the client only has one interface although I might add
it in the furture if needed

This file installs all the packeges needed for the client as well as setting up the related config files
Eventually it will also download all necacery YARA rules from the server (Coming in V1)

List of packages:
None, the client will operate with deafult packages only (fingers crossed)
"""
modules_dir = sys.prefix + "/lib/python" + sys.version[:3] + "/site-packages"

input_ip = input("Enter the IP of the analysis server: ")
client_input_ip = input("Enter the IP of the client server (this server): ")
try:
    input_port = int(input("Enter the port of the analysis server: "))
    if input_port < 1 or input_port > 65535:
        print("Invalid port number >:(")
        quit()
except:
    print("The port must be a number >:(")
    quit()

data = {
    "connection": {
        "serverIP": input_ip,
        "clientIP": client_input_ip,
        "serverPort": input_port
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

files = ["headlessmc-launcher-1.9.0.jar", "HeadlessMC", ".minecraft", "requests.zip", "requests.zip", "urllib3.zip", "chardet.zip", "certifi.zip", "idna.zip", "background.png"]
backgrounds = ["background_purple.png", "background_red.png", "background_blue.png", "background_black.png", "background_white.png"]
modules = ["requests.zip", "urllib3.zip", "chardet.zip", "certifi.zip", "idna.zip"]# I don't like repeating code but I subscribe to the principle of EASIER DEBUG!

url = f"http://{serverIP}:5000/setup"
filename = ""

for filename in files:
    print("Downloading: " + filename)
    if filename == "background.png":
        background_filename = backgrounds[random.randint(0,4)]
        url_to_download = url + "/" + background_filename
        urllib.request.urlretrieve(url_to_download, background_filename)
    elif filename == "headlessmc-launcher-1.9.0.jar": # There is probbly a better way to do this
        url_to_download = url + "/" + filename
        urllib.request.urlretrieve(url_to_download, filename)
    else:
        url_to_download = url + "/" + filename
        urllib.request.urlretrieve(url_to_download, filename + ".zip")
        try:
            with zipfile.ZipFile(filename + ".zip", 'r') as zip_ref:
                zip_ref.extractall(filename)
        except:
            pass

for module in modules:
    if not os.path.exists(module):
        url_to_download = url + "/" + module
        urllib.request.urlretrieve(url_to_download, module + ".zip")
        try:
            with zipfile.ZipFile(module + ".zip", 'r') as zip_ref:
                zip_ref.extractall(module)
        except:
            pass

        try:
            shutil.copytree(module, modules_dir)
        except FileExistsError:
            print(f"Module: {module} already exists in destination")

if not os.path.exists(os.getenv('APPDATA') + "\\.minecraft"):
    try:
        shutil.copytree(".minecraft", os.getenv('APPDATA') + "\\.minecraft")
    except FileExistsError:
        print("Minecraft directory already exists")
if os.path.exists("requests"):
    os.rename()
if os.path.exists(os.path.abspath(background_filename)):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(background_filename) , 0)
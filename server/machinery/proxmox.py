""" 
This is the machineary file for proxmox that allows the server to take snapshots and roll back the VM when
an anlysis has been completed. Although this might not be necacery as most minecraft malware leaves no trace
on the system, it is included as a precaution
"""
import json

with open("../webserver/config/config.json", "r") as read_file:
    config = json.load(read_file)

proxmox_URL = f"https://{config["machinery"]["proxmoxIP"]}:8006/api2/json/"
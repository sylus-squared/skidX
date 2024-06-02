""" 
This is the machineary file for proxmox that allows the server to take snapshots and roll back the VM when
an anlysis has been completed. Although this might not be necacery as most minecraft malware leaves no trace
on the system, it is included as a precaution

The username and password are stored as enviroment variables (to avoid having to store them in the config file), create said enviroment variables with the
commands:
export PROXMOX_USERNAME="your_username"
export PROXMOX_PASSWORD="your_password"
I might replace this with a secrets file you have to provide a password on the webserver to access as its still not secure
"""
import json
import requests

with open("../webserver/config/config.json", "r") as read_file:
    config = json.load(read_file)

proxmox_IP = config["machinery"]["proxmox_IP"]
username = os.environ["PROXMOX_USERNAME"]
password = os.environ["PROXMOX_PASSWORD"]
vm_id = config["machinery"]["vm_id"]
snapshot_name = config["machinery"]["snapshot_name"]

def get_ticket(): # Gets a ticket and CSRF token
    url = f"https://{proxmox_IP}:8006/api2/json/access/ticket"
    data = {"username": username, "password": password}
    response = requests.post(url, data=data, verify=False)
    if response.status_code == 200:
        ticket_data = response.json()["data"]
        return ticket_data["ticket"], ticket_data["CSRFPreventionToken"]
    else:
        print(f"Error getting ticket: {response.text}")
        return None, None

def create_snapshot(vm_id, ticket, csrf_token):
    url = f"https://{proxmox_IP}:8006/api2/json/nodes/localhost/qemu/{vm_id}/snapshot"
    data = {"snapname": snapshot_name}
    headers = {
        "Cookie": f"PVEAuthCookie={ticket}",
        "CSRFPreventionToken": csrf_token
    }
    response = requests.post(url, json=data, headers=headers, verify=False)
    if response.status_code == 200:
        print(f"Snapshot created for VM {vm_id} with name {snapshot_name}")
    else:
        print(f"Error creating snapshot for VM {vm_id}: {response.text}")

def revert_to_snapshot(vm_id, ticket, csrf_token):
    url = f"https://{proxmox_IP}:8006/api2/json/nodes/localhost/qemu/{vm_id}/snapshot/{snapshot_name}/rollback"
    headers = {
        "Cookie": f"PVEAuthCookie={ticket}",
        "CSRFPreventionToken": csrf_token
    }
    response = requests.post(url, headers=headers, verify=False)
    if response.status_code == 200:
        print(f"VM {vm_id} reverted to snapshot {snapshot_name}")
    else:
        print(f"Error reverting VM {vm_id} to snapshot {snapshot_name}: {response.text}")

ticket, csrf_token = get_ticket()
create_snapshot(vm_id, ticket, csrf_token)
revert_to_snapshot(vm_id, ticket, csrf_token)
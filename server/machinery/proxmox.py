""" 
This is the machineary file for proxmox that allows the server to take snapshots and roll back the VM when
an anlysis has been completed. Although this might not be necacery as most minecraft malware leaves no trace
on the system, it is included as a precaution

The username and password are stored in a seperate credentials file (to avoid having to store them in the config file)
I might replace this with a secrets file you have to provide a password on the webserver to access as its still not secure
"""
import json
import requests
import os

with open("../webserver/config/config.json", "r") as read_file:
    config = json.load(read_file)

proxmox_IP = config["machinery"]["proxmox_IP"]

with open("creds.txt", 'r') as file:
    lines = file.readlines()

for line in lines:
    if "username" in line:
        username = line.split('=')[1].strip()
    elif "password" in line:
        password = line.split('=')[1].strip()

def get_ticket():
    url = f"https://{proxmox_IP}:8006/api2/json/access/ticket"
    data = {"username": username, "password": password}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=data, headers=headers, verify=False)
    if response.status_code == 200:
        ticket_data = response.json()["data"]
        return ticket_data["ticket"], ticket_data["CSRFPreventionToken"]
    else:
        print(f"Error getting ticket: {response.status_code} - {response.reason}")
        print(response.text)
        return None, None

def get_snapshot_list(vm_id, ticket, csrf_token):
    url = f"https://{proxmox_IP}:8006/api2/json/nodes/localhost/qemu/{vm_id}/snapshot"
    headers = {
        "Cookie": f"PVEAuthCookie={ticket}",
        "CSRFPreventionToken": csrf_token
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Error getting snapshot list for VM {vm_id}: {response.text}")
        return []

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
import requests
import subprocess

"""
This is the client to be deployed on the dirty VM used to dnamically analyze java infostealers pretending to be minecraft mods
This uses a combination of inetsym and self written YARA rules :( to dynamically assess minecraft mods to check if they are malicious or not
Thankfully said mods are written by skids so zero fucks have to be given when it comes to VM stealthiness
The following must be implemented for this to work:
DirtyVM (must be windows and be able to run python 3)
Inetsym server (must be accesable from the VM)
reporting webserver (should be the same as inetsym)

This script must do the following:
Download the latest file from the web server when the VM starts (this is the malicious file and means only one file can be analysed at a time)
Execute the downloded file with a headless minecraft instance (forge and fabric)
Analyse the executed file with self written YARA rules
Encrypt the verdict and send it to the server (needs to be encrypted because there is malware running on the system)
"""
# Switched from due to the lack of openGL on the client sandbox, headlessMC will be used now 
# Will add code for it soon

# skidX
**Important note**
*This project is currently at a very early stage and when done will only be a proof of concept. Because of this I would not recommend using this any time soon. It will most likely be insecure and resource intensive (especially on the sandbox VM).*
# What is it?
skiX is a self hosted malware analysis environment for malicious minecraft mods. There are many other online sandboxes for analysing traditional malware, however, due to the fact that minecraft is a requirement to execute the mod, none of them work with minecraft mods :(

And while there are solutions to tell if a mod is malicious (see [isthisarat](isthisarat.com)) extracting the C2 can be difficult by just looking at the code (especially if its been obfuscated). 

This project aims to change that.

skidX detonates the sample on the sandbox VM and collects network data (and other stuff in the future) using inetsym then displays said data in a nice easy to read format. All the user has to do is upload the file and look at the log.

# Roadmap
### Proof of concept
Flask webserver for uploading files for analysis and viewing the results
Client for the sandbox VM to detonate the malware
Highlighting of potential C2's in the results
Support for automatically reverting the VM to a specified snapshot Proxmox only (potentially)
### V1
YARA rules for identifying different strains of infostealers
Migration of the webserver from flask to something like waitress combined with nginx
Headless client for the sandbox VM
A malicious score out of 100
Support for KVM (potentially)
Nicer looking webserver
### V2
Integration with isthisarat to help with verdicts
Virus total integration for comments and such
Automated writing of mediafire reports based (just the description not actually submitting them)
Geolocation of requests
Script for automatically finding and downloading samples

*There will most likely be a more I have forgotten to add and this list will change a lot*

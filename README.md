![](images/logo.png)
# skidX
**Important note** 
*This project is currently at a very early stage and when done will only be a proof of concept (code coming soon). Because of this I would not recommend using this any time soon. It will most likely be insecure and resource intensive (especially on the sandbox VM).* <br />
# What is it? 
skiX is a self hosted malware analysis environment for malicious minecraft mods. There are many other online sandboxes for analysing traditional malware, however, due to the fact that minecraft is a requirement to execute the mod, none of them work with minecraft mods :( <br />

And while there are solutions to tell if a mod is malicious (see [isthisarat](isthisarat.com)) extracting the C2 can be difficult by just looking at the code (especially if its been obfuscated). <br />

This project aims to change that. <br />

skidX detonates the sample on the sandbox VM and collects network data (and other stuff in the future) using inetsym then displays said data in a nice easy to read format. All the user has to do is upload the file, wait a few mins and look at the log. <br />

# Roadmap 
### Proof of concept 
Flask webserver for uploading files for analysis and viewing the results <br />
Client for the sandbox VM to detonate the malware <br />
Highlighting of potential C2's in the results <br />
Support for automatically reverting the VM to a specified snapshot Proxmox only (potentially) <br />
### V1 
YARA rules for identifying different strains of infostealers <br />
Migration of the webserver from flask to something like waitress combined with nginx <br />
Headless client for the sandbox VM <br />
A malicious score out of 100 <br />
Support for KVM (potentially) <br />
Nicer looking webserver <br />
An API (probbly JSON based) <br/ >
### V2 
Integration with isthisarat to help with verdicts <br />
Virus total integration for comments and such <br />
Automated writing of mediafire reports based (just the description not actually submitting them) <br />
Geolocation of requests <br />
Script for automatically finding and downloading samples <br />

*There will most likely be a more I have forgotten to add and this list will change a lot*

![](images/logo.png)
# skidX
**Important note**<br/>
*This project is currently at a very early stage and is just a proof of concept. Because of this I would not recommend using this any time soon. It will most likely be insecure and resource intensive (especially on the sandbox VM).* <br/>
# What is it? 
skidX is a self hosted malware analysis environment for malicious minecraft mods. There are many other online sandboxes for analysing traditional malware, however, due to the fact that minecraft (and forge/fabric) is a requirement to execute the mod, none of them work with minecraft mods :( <br/>

Some sandboxes that do static code analysis can tell if some minecraft rats are malicious ([hybird analysis](https://www.hybrid-analysis.com/) has been most consistent for me), they do not work well if the sample is obfuscated.

And while there are solutions to tell if a mod is malicious (see [isthisarat](https://isthisarat.com)) extracting the C2 can be difficult by just analysing the code (especially if its been obfuscated). <br/>

This project aims to change that. <br/>

skidX detonates the sample on the sandbox VM and collects network data (and other stuff in the future) using inetsym then displays said data in a nice easy to read format. All the user has to do is upload the file, wait a few mins and look at the log. <br/>
skidX currently uses a modified version of headlessmc, its a brilliant project go check it out [here](https://github.com/3arthqu4ke/headlessmc) <br/>

# Roadmap 
### Proof of concept 
Flask webserver for uploading files for analysis and viewing the results <br/>
Client for the sandbox VM to detonate the malware <br/>
Highlighting of potential C2's in the results <br/>
Headless client for the sandbox VM <br/>
Support for automatically reverting the VM to a specified snapshot for Proxmox <br/>
A que for multiple files, although only will file can run at a time <br/>
Documentation (probbly the bare minimum for the POC) <br/>
HTTPS decryption with polar proxy <br/>
### V1 
YARA rules for identifying different strains of infostealers <br/>
Migration of the webserver from flask to something like waitress combined with nginx <br/>
A malicious score out of 100 <br/>
Support for KVM and nested virtualization (potentially) <br/>
Nicer looking webserver <br/>
An API (probbly JSON based) <br/>
Support for multiple VM's at once<br/>
### V2 
Integration with isthisarat to help with verdicts <br/>
(isthisarat has no api for submissions so this might not happen) <br/>
Virus total integration for comments and such <br/>
Automated writing of mediafire reports (just the description not actually submitting them) <br/>
Geolocation of requests <br/>
Script for automatically finding and downloading samples <br/>

*There will most likely be more I have forgotten to add and this list will change*

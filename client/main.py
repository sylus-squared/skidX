import time
import requests
#import yaml
import subprocess
import minecraft_launcher_lib

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
# THIS IS CURRENTLY TESTING CODE, DO NOT USE IT
def ask_yes_no(text: str) -> bool:
    while True:
        answer = input(text + " [y|n]: ")
        if answer.lower() == "y":
            return True
        elif answer.lower() == "n":
            return False
        else:
            print("Please enter y or n")


def main():
    minecraft_directory = "minecraft_files"
    vanilla_version = "1.8.9" #input("Select the Minecraft version for which you want to install forge: ")
    options = minecraft_launcher_lib.utils.generate_test_options()
    # Find the latest forge version for that Minecraft version
    forge_version = minecraft_launcher_lib.forge.find_forge_version(vanilla_version)
    # Checks if a forge version exists for that version
    if forge_version is None:
        print("This Minecraft version is not supported by forge")
        sys.exit(0)
    # Checks if the version can be installed automatic
    if ask_yes_no(f"Do you want to install forge {forge_version}?"):
            callback = {
                "setStatus": lambda text: print(text)
            }
            minecraft_launcher_lib.forge.install_forge_version(forge_version, minecraft_directory, callback=callback)

    versions = minecraft_launcher_lib.utils.get_installed_versions(minecraft_directory)
    print(versions)
    version = versions[0]
    minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(version["id"], minecraft_directory, options)
    subprocess.run(minecraft_command)


if __name__ == "__main__":
    main()


import subprocess
import socket
import re
from datetime import datetime, timedelta

def get_ip_address():
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a remote server (doesn't have to be reachable)
        sock.connect(("8.8.8.8", 80))
        # Get the local IP address
        ip_address = sock.getsockname()[0]
    finally:
        # Close the socket to release resources
        sock.close()
    return ip_address

# Get and print the local IP address
local_ip = get_ip_address()

def check_service(service, command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

def host_services():
    service_checks = {
        "qbittorrent": "ps -ef | grep -E '([q]bittorrent)'",
        "minidlna": "ps -ef | grep -E '([m]inidlna)'",
        "Data Backup": "stat ~/.jbl-backup.log | grep ^Modify",
        "Expressvpn": "expressvpn status | grep -i connected | sed \"s/\\x1b\[[0-9;]*[mGK]//g\"",
        "Dropbox": "ps -ef | grep [d]ropbox",
        "KeepassXC": "ps -ef | grep -i '[b]in/keepassxc'",
        "Apache Nifi": "ps -ef | grep -i '[o]pt/nifi'",
        "Open WebUI": "curl localhost:3000 --silent |grep '<title>' | sed -e 's/^.*title>Open WebUI.*$/Open WebUI/'"
    }

    print("[- VDC Host Services (" + local_ip +") -]")

    for service, command in service_checks.items():
        output = check_service(service, command)

        if output:
            if service == "backup":
                backup_date_str = output.strip().split(' ')[1]  # Extract the date part
                backup_date = datetime.strptime(backup_date_str, '%Y-%m-%d')
                # print(f"[✅] Backup Status: {output.strip()}")
                if datetime.now() - backup_date > timedelta(days=7):
                    print(f"[❌] Backup Status: Last modified date {backup_date_str} is older than 7 days")
                else:
                    print(f"[✅] Backup Status: Last modified date {backup_date_str} is within 7 days")
            elif service == "expressvpn":
                if re.search("Connected", output.strip()):
                    print(f"[✅] ExpressVPN Status: {output.strip()}")
                else:
                    print(f"[❌] ExpressVPN Status: {output.strip()}")
            else:
                print(f"[✅] {service} is running")
        else:
            print(f"[❌] {service} is not running")


    print("")

# Call the function to execute
host_services()

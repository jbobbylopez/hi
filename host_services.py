import subprocess
import socket
import re
from datetime import datetime, timedelta

def get_ip_address():
    result = {
        "ip_address": None,
        "message": ""
    }
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        result["ip_address"] = sock.getsockname()[0]
        result["message"] = f"Local IP Address: {result['ip_address']}"
    except socket.error as e:
        result["message"] = f"Error occurred: {e}"
    finally:
        sock.close()
    return result


def get_hostname_address():
    result = {
        "hostname": None,
        "ip_address": None,
        "message": ""
    }
    try:
        result["hostname"] = socket.gethostname()
        result["ip_address"] = socket.gethostbyname(result["hostname"])
        result["message"] = f"Hostname: {result['hostname']}\nIP Address: {result['ip_address']}"
    except socket.error as e:
        result["message"] = f"Error occurred: {e}"
    return result

def check_process(process, command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

def process_checks():
    process_checks = {
        "qbittorrent": "ps -ef | grep -E '([q]bittorrent)'",
        "minidlna": "ps -ef | grep -E '([m]inidlna)'",
        "vi": "ps -ef |grep pts.*[v]i$",
        "Data Backup": "stat ~/.jbl-backup.log | grep ^Modify",
        "Expressvpn": "expressvpn status | grep -i connected | sed \"s/\\x1b\[[0-9;]*[mGK]//g\"",
        "Dropbox": "ps -ef | grep [d]ropbox",
        "KeepassXC": "ps -ef | grep -i '[b]in/keepassxc'",
        "Apache Nifi": "ps -ef | grep -i '[o]pt/nifi'",
        "Open WebUI": "curl localhost:3000 --silent |grep '<title>' | sed -e 's/^.*title>Open WebUI.*$/Open WebUI/'",
        "Galaxy S20": "mount| grep -i '/mnt/GalaxyS20'"
    }

    output_messages = []

    # Get and print the local IP address
    local_ip_result = get_ip_address()

    # Get and print the hostname and IP address
    hostname_result = get_hostname_address()

    # Host Information
    output_messages.append(f"[- Host Information: {hostname_result['hostname']} ({hostname_result['ip_address']}) {{{local_ip_result['ip_address']}}} -]")

    for process, command in process_checks.items():
        output = check_process(process, command)

        if output:
            if process == "Data Backup":
                backup_date_str = output.strip().split(' ')[1]  # Extract the date part
                backup_date = datetime.strptime(backup_date_str, '%Y-%m-%d')
                if datetime.now() - backup_date > timedelta(days=7):
                    output_messages.append(f"[❌] Backup Status: Last modified date {backup_date_str} is older than 7 days")
                else:
                    output_messages.append(f"[✅] Backup Status: Last modified date {backup_date_str} is within 7 days")
            elif process == "Expressvpn":
                if re.search("Connected", output.strip()):
                    output_messages.append(f"[✅] ExpressVPN Status: {output.strip()}")
                else:
                    output_messages.append(f"[❌] ExpressVPN Status: {output.strip()}")
            else:
                output_messages.append(f"[✅] {process} is running")
        else:
            output_messages.append(f"[❌] {process} is not running")

    # Print all output messages
    final_output = "\n".join(output_messages)
    print(final_output)
    print("\n")

# Call the function to execute
process_checks()

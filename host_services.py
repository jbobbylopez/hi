import subprocess

def check_service(service, command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

def host_services():
    service_checks = {
        "qbittorrent": "ps -ef | grep -E '([q]bittorrent)'",
        "minidlna": "ps -ef | grep -E '([m]inidlna)'",
        "backup": "stat ~/.jbl-backup.log | grep ^Modify",
        "expressvpn": "expressvpn status | grep -i connected"
    }

    print("[- VDC Host Services -]")

    for service, command in service_checks.items():
        output = check_service(service, command)

        if output:
            if service == "backup":
                print(f"[✅] Backup Status: {output.strip()}")
            else:
                print(f"[✅] {service} is running")
        else:
            print(f"[❌] {service} is not running")

    print("")

# Call the function to execute
host_services()

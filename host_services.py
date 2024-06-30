from rich.console import Console
from rich.table import Table
import subprocess
import socket
import re
from datetime import datetime, timedelta
import yaml

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

def get_checks_yaml(checks_yaml):
    with open(checks_yaml, 'r') as file:
        checks = yaml.safe_load(file)
    return checks

def compile_output_messages(process, output):
    output_messages = []

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
    return final_output

def check_engine_yaml(check_type):
    checks = get_checks_yaml("/home/jbl/scripts/jbl-host-information/checks.yml")
    checks = checks['checks']

    security_output = []
    data_output = []
    mount_output = []
    backup_output = []
    media_output = []
    tools_output = []
    group_output = []

    for process, attribs in checks.items():
        if attribs['group'] == check_type:
            output = check_process(process, attribs['command'])
            group_output.append(compile_output_messages(process, output))

    final_output = group_output
    return final_output

def display_checks():
    console = Console()
    security_checks = check_engine_yaml("Security")
    data_checks = check_engine_yaml("Data")
    mount_checks = check_engine_yaml("Mount")
    backup_checks = check_engine_yaml("Backup")
    media_checks = check_engine_yaml("Media")
    tools_checks = check_engine_yaml("Tools")

    # Get and print the local IP address
    local_ip_result = get_ip_address()

    # Get and print the hostname and IP address
    hostname_result = get_hostname_address()

    # Host Information
    print(f"[- Host Information: {hostname_result['hostname']} ({hostname_result['ip_address']}) {{{local_ip_result['ip_address']}}} -]")

    # Create a new table
    table1 = Table(show_header=True, header_style="bold magenta", expand=True)
    table2 = Table(show_header=True, header_style="bold magenta", expand=True)
    table3 = Table(show_header=True, header_style="bold magenta", expand=True)

    # Define columns
    table1.add_column("Security Checks", style="green3", justify="left", no_wrap=True, width=40)
    table1.add_column("Mount Checks", style="green3", justify="left", no_wrap=True, width=40)
    table2.add_column("Data Checks", style="green3", justify="left", no_wrap=True, width=40)
    table2.add_column("Media Checks", style="green3", justify="left", no_wrap=True, width=40)
    table3.add_column("Backup Checks", style="green3", justify="left", no_wrap=True, width=40)
    table3.add_column("Tools Checks", style="green3", justify="left", no_wrap=True, width=40)

    # Add rows to the table with cell borders
    for sec_check, mount_check, in zip(security_checks, mount_checks):
        table1.add_row(sec_check,mount_check)

    for data_check, media_check in zip(data_checks, media_checks):
        table2.add_row(data_check,media_check)

    for backup_check, tools_check in zip(backup_checks, tools_checks):
        table3.add_row(backup_check,tools_check)

    # Print the table with solid blue borders and solid green cell borders
    console.print(table1)
    console.print(table2)
    console.print(table3)

# Call the function to execute
display_checks()

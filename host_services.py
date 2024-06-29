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

def check_engine_yaml():
    checks = get_checks_yaml("/home/jbl/scripts/jbl-host-information/checks.yml")
    checks = checks['checks']

    output_messages = []

    for process, attribs in checks.items():
        output = check_process(process, attribs['command'])

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

def display_checks():
    console = Console()
    #process_checks = check_engine()
    process_checks = check_engine_yaml()
    checks = process_checks.split('\n')

    # Get and print the local IP address
    local_ip_result = get_ip_address()

    # Get and print the hostname and IP address
    hostname_result = get_hostname_address()

    # Host Information
    print(f"[- Host Information: {hostname_result['hostname']} ({hostname_result['ip_address']}) {{{local_ip_result['ip_address']}}} -]")

    # Create a new table
    table = Table(show_header=True, header_style="bold magenta", expand=True)

    # Define columns
    table.add_column("Process Checks", style="green3", justify="left", no_wrap=True, width=40)
    table.add_column("Mount Checks", style="green3", justify="center", no_wrap=True, width=40)

    # Example data
    col1_data = checks
    #col2_data = ["Data A", "Data B", "Data C", "Data D"]

    # Add rows to the table with cell borders
    for data1 in zip(col1_data):
        table.add_row(
            #f"[green3][blue]{data1[0]}[/blue][/green3]",
            f"{data1[0]}",
            #f"[blue]▌[/blue] [green3]{data2}[/green3]"
        )

    # Print the table with solid blue borders and solid green cell borders
    console.print(table)

# Call the function to execute
display_checks()

from rich.console import Console
from rich.table import Table
from rich.box import SIMPLE, MINIMAL
import subprocess
import socket
import re
import os
from datetime import datetime, timedelta
import yaml

def get_script_dir():
    ''' Returns the directory where the script is running from '''
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    return script_dir

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

def compile_output_messages(process, output, group):
    output_messages = []

    if output:
        if process == "Data Backup":
            backup_date_str = output.strip().split(' ')[1]  # Extract the date part
            backup_date = datetime.strptime(backup_date_str, '%Y-%m-%d')
            if datetime.now() - backup_date > timedelta(days=7):
                output_messages.append(f"[❌] Backup Status: Last modified date {backup_date_str} is older than 7 days")
            else:
                output_messages.append(f"[✅] Backup Status: Last modified date {backup_date_str} is within 7 days")
        elif process == "ExpressVPN":
            if re.search("Connected", output.strip()):
                output_messages.append(f"[✅] ExpressVPN Status: {output.strip()}")
            else:
                output_messages.append(f"[❌] ExpressVPN Status: {output.strip()}")
        elif group == "Tools":
            output_messages.append(f"[💡] {process} is running")
        elif group == "Mount":
            output_messages.append(f"[✅] {process} is mounted")
        else:
            output_messages.append(f"[✅] {process} is running")
    elif group == "Tools":
            output_messages.append(f"[⚫] {process} is not running")
    elif group == "Mount":
            output_messages.append(f"[❌] {process} is not mounted")
    else:
        output_messages.append(f"[❌] {process} is not running")

    # Print all output messages
    final_output = "\n".join(output_messages)
    return final_output

def check_engine_yaml(check_type):
    script_dir = get_script_dir()
    checks = get_checks_yaml(script_dir + "/config/checks.yml")
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
            group_output.append(compile_output_messages(process, output, check_type))

    final_output = group_output
    return final_output

def display_checks():
    """
    Display categorized checks in Rich tables, handling unequal lists gracefully.

    This function retrieves categorized checks from YAML configuration, processes each 
    category's checks, and displays them in separate Rich tables. It ensures all data is 
    displayed by iterating over the maximum length of all check lists and uses empty 
    strings for categories with fewer items. Tables are formatted with minimal borders 
    and styled headers.

    Key Steps:
    - Retrieves and categorizes checks (Security, Data, Mount, Backup, Media, Tools).
    - Creates three Rich tables with appropriate columns.
    - Iterates over lists, ensuring all data is displayed using zip() and handling 
      unequal lengths.
    - Prints tables with formatted headers and solid borders.

    Adjust widths, styles, and formatting as needed for specific display requirements.
    """
    console = Console()
    security_checks = check_engine_yaml("Security")
    data_checks = check_engine_yaml("Data")
    mount_checks = check_engine_yaml("Mount")
    backup_checks = check_engine_yaml("Backup")
    media_checks = check_engine_yaml("Media")
    tools_checks = check_engine_yaml("Tools")

    # Determine maximum length among all lists
    max_length = max(len(security_checks), len(data_checks), len(mount_checks),
                     len(backup_checks), len(media_checks), len(tools_checks))

    # Get and print the local IP address
    local_ip_result = get_ip_address()

    # Get and print the hostname and IP address
    hostname_result = get_hostname_address()

    # Host Information
    print(f"[- Host Information: {hostname_result['hostname']} ({hostname_result['ip_address']}) {{{local_ip_result['ip_address']}}} -]")

    # Create a new table
    table1 = Table(show_header=True, header_style="bold magenta", expand=True, box=MINIMAL)
    table2 = Table(show_header=True, header_style="bold magenta", expand=True, box=MINIMAL)
    table3 = Table(show_header=True, header_style="bold magenta", expand=True, box=MINIMAL)

    # Define columns
    table1.add_column("Security", style="green3", justify="left", no_wrap=True, width=40)
    table1.add_column("Volumes / File Services", style="green3", justify="left", no_wrap=True, width=40)
    table2.add_column("Data", style="green3", justify="left", no_wrap=True, width=40)
    table2.add_column("Media", style="green3", justify="left", no_wrap=True, width=40)
    table3.add_column("Backup", style="green3", justify="left", no_wrap=True, width=40)
    table3.add_column("Tools", style="green3", justify="left", no_wrap=True, width=40)


    for i in range(max_length):
        # Security and Mount checks
        if i < len(security_checks):
            sec_check = security_checks[i]
        else:
            sec_check = ""

        if i < len(mount_checks):
            mount_check = mount_checks[i]
        else:
            mount_check = ""

        table1.add_row(sec_check, mount_check)

        # Data and Media checks
        if i < len(data_checks):
            data_check = data_checks[i]
        else:
            data_check = ""

        if i < len(media_checks):
            media_check = media_checks[i]
        else:
            media_check = ""

        table2.add_row(data_check, media_check)

        # Backup and Tools checks
        if i < len(backup_checks):
            backup_check = backup_checks[i]
        else:
            backup_check = ""

        if i < len(tools_checks):
            tools_check = tools_checks[i]
        else:
            tools_check = ""

        table3.add_row(backup_check, tools_check)


    # Print the table with solid blue borders and solid green cell borders
    console.print(table1)
    console.print(table2)
    console.print(table3)

# Call the function to execute
display_checks()

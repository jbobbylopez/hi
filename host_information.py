import sys
from rich.console import Console
from rich.table import Table
from rich.box import MINIMAL
import subprocess
import socket
import re
import os
from datetime import datetime, timedelta
import yaml
import check_ubuntu_eol
import df_bargraph

def get_script_dir():
    ''' Returns the directory where the script is running from '''
    return os.path.dirname(os.path.abspath(__file__))

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
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return str(e)

def get_checks_yaml(checks_yaml):
    with open(checks_yaml, 'r') as file:
        checks = yaml.safe_load(file)
    return checks

def get_groups_yaml(groups_yaml):
    with open(groups_yaml, 'r') as file:
        groups = yaml.safe_load(file)
    return groups

def compile_output_messages(process, output, group, info=None):
    output_messages = []

    if output:
        if 'date_check' in process.lower():
            backup_date_str = output.strip().split(' ')[1]
            backup_date = datetime.strptime(backup_date_str, '%Y-%m-%d')
            threshold_days = 7  # Assuming 7 days threshold for date_check processes
            if datetime.now() - backup_date > timedelta(days=threshold_days):
                output_messages.append(f"[❌] {process}: Last modified date {backup_date_str} is older than {threshold_days} days")
            else:
                output_messages.append(f"[✅] {process}: Last modified date {backup_date_str} is within {threshold_days} days")
        elif 'expressvpn' in process.lower():
            if re.search("Connected", output.strip()):
                output_messages.append(f"[✅] {process} Status: {output.strip()}")
            else:
                output_messages.append(f"[❌] {process} Status: {output.strip()}")
        else:
            if group == "Tools":
                output_messages.append(f"[💡] {process} is running")
            elif group == "Mount":
                output_messages.append(f"[✅] {process} is mounted")
            else:
                output_messages.append(f"[✅] {process} is running")
    else:
        if group == "Tools":
            output_messages.append(f"[⚫] {process} is not running")
        elif group == "Mount":
            output_messages.append(f"[❌] {process} is not mounted")
        else:
            output_messages.append(f"[❌] {process} is not running")

    # Add info message if present
    if info:
        output_messages.append(f"  [🔹] {info}")

    final_output = "\n".join(output_messages)
    return final_output

def check_engine_yaml(check_type, verbose=False):
    script_dir = get_script_dir()
    checks = get_checks_yaml(os.path.join(script_dir, "config/checks.yml"))
    checks = checks['checks']

    group_output = []

    for process, attribs in checks.items():
        if attribs['group'] == check_type:
            output = check_process(process, attribs['command'])
            info = attribs.get('info') if verbose else None
            group_output.append(compile_output_messages(process, output, check_type, info))

    return group_output

def display_checks():
    """
    Display categorized checks in Rich tables, handling unequal lists gracefully.
    """
    console = Console()
    script_dir = get_script_dir()
    groups = get_groups_yaml(os.path.join(script_dir, "config/groups.yml"))['groups']

    print("arguments = " + str(sys.argv))
    verbose = '-verbose' in sys.argv
    print("verbose = " + str(verbose))

    # Get and print the local IP address
    local_ip_result = get_ip_address()

    # Get and print the hostname and IP address
    hostname_result = get_hostname_address()

    console.print(f"[- Host Information: {hostname_result['hostname']} ({hostname_result['ip_address']}) {{{local_ip_result['ip_address']}}} -]")

    group_statuses = {group: check_engine_yaml(group, verbose) for group in groups}

    # Loop over every two groups and create tables
    for i in range(0, len(groups), 2):
        table = Table(show_header=True, header_style="bold magenta", expand=True, box=MINIMAL)
        group1 = groups[i]
        table.add_column(group1, style="green3", justify="left", no_wrap=True, width=40)
        group2 = groups[i + 1] if i + 1 < len(groups) else None
        if group2:
            table.add_column(group2, style="green3", justify="left", no_wrap=True, width=40)

        max_length = max(len(group_statuses[group1]), len(group_statuses[group2]) if group2 else 0)

        for j in range(max_length):
            col1 = group_statuses[group1][j] if j < len(group_statuses[group1]) else ""
            col2 = group_statuses[group2][j] if group2 and j < len(group_statuses[group2]) else ""
            table.add_row(col1, col2)

        console.print(table)

# Call the function to execute
display_checks()
check_ubuntu_eol.main()
df_bargraph.display_bar_graph()

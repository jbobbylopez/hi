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

def compile_output_messages(check, cmd_output, group, info=None, indicators=None, sub_checks=None):
    status = ""
    check_indicators = None
    output_messages = []

    # The below 'if output:' statement means that the command completed
    # successfully, and 'output' contains any data returned by the executed
    # command.  'check' contains the name of the check in config/check.yml.
    if cmd_output:
        indicator = '✅'
        if indicators:
            if 'positive' in indicators and 'icon' in indicators['positive']:
                indicator = indicators['positive']['icon']
            if 'positive' in indicators and 'status' in indicators['positive']:
                output = indicators['positive']['status'] 

        if 'data backup' in check.lower():
            # This little bit of date calculation for the backup
            # notification likely needs to be moved or handled differently.
            # Separate function for sure.
            print("cmd_output: " + str(output))
            backup_date_str = cmd_output.strip().split(' ')[1]
            backup_date = datetime.strptime(backup_date_str, '%Y-%m-%d')
            threshold_days = 7  # Assuming 7 days threshold for date_check
            if datetime.now() - backup_date > timedelta(days=threshold_days):
                output_messages.append(f"[❌] {check}: Last modified date {backup_date_str} is older than {threshold_days} days")
            else:
                output_messages.append(f"[✅] {check}: Last modified date {backup_date_str} is within {threshold_days} days")
        elif 'expressvpn' in check.lower():
            if re.search("Connected", cmd_output.strip()):
                output_messages.append(f"[✅] {check} Status: {cmd_output.strip()}")
            else:
                output_messages.append(f"[❌] {check} Status: {cmd_output.strip()}")
        else:
            try:
                output = indicators['positive']['status']
                indicator = indicators['positive']['icon']
            except:
                output = " is running" 
            output_messages.append(f"[{indicator}] {check} {output}")

    else:
        indicator = '❌'
        output = "is stopped"
        if indicators:
            if 'negative' in indicators and 'icon' in indicators['negative']:
                indicator = indicators['negative']['icon']
            if 'negative' in indicators and 'status' in indicators['negative']:
                output = indicators['negative']['status'] 
        output_messages.append(f"[{indicator}] {check} {output}")

    # Append info: value if present
    if info:
        output_messages.append(f"  [🔹] {info}")

    # Append sub_checks if present
    # .. this will likely need to be turned into it's own function
    if sub_checks:
        for sub_check in sub_checks:
            indicator = '⚫'
            status = ""
            sub_check_indicators = None
            sub_check_command = sub_checks[sub_check]['command']
            sub_check_output = check_process(sub_check, sub_check_command).strip()

            if sub_check_output:
                if 'indicators' in sub_checks[sub_check]:
                    sub_check_indicators = sub_checks[sub_check]['indicators']
                    if 'positive' in sub_check_indicators and 'icon' in sub_check_indicators['positive']:
                        indicator = sub_check_indicators['positive']['icon']
                    if 'positive' in sub_check_indicators and 'status' in sub_check_indicators['positive']:
                        sub_check_output = sub_check_indicators['positive']['status'] 
                output_messages.append(f"  [{indicator}] {sub_check}: {sub_check_output}")

            else:
                if 'indicators' in sub_checks[sub_check]:
                    sub_check_indicators = sub_checks[sub_check]['indicators']
                    if 'negative' in sub_check_indicators and 'icon' in sub_check_indicators['negative']:
                        indicator = sub_check_indicators['negative']['icon']
                    if 'negative' in sub_check_indicators and 'status' in sub_check_indicators['negative']:
                        sub_check_output = sub_check_indicators['negative']['status'] 
                output_messages.append(f" [{indicator}] {sub_check}: {sub_check_output}")

    final_output = "\n".join(output_messages)
    return final_output

def check_engine_yaml(check_type, verbose=False):
    script_dir = get_script_dir()
    checks = get_checks_yaml(os.path.join(script_dir, "config/checks.yml"))
    checks = checks['checks']

    group_output = []
    sub_checks = None

    for check, attribs in checks.items():
        if attribs['group'] == check_type:
            output = check_process(check, attribs['command'])
            sub_checks = attribs.get('sub_checks') if verbose else None
            info = attribs.get('info') if verbose else None
            indicators = attribs.get('indicators')
            group_output.append(compile_output_messages(check, output, check_type, info, indicators, sub_checks))

    return group_output

def display_checks():
    """
    Display categorized checks in Rich tables, handling unequal lists gracefully.
    """
    console = Console()
    script_dir = get_script_dir()
    groups = get_groups_yaml(os.path.join(script_dir, "config/groups.yml"))['groups']
    verbose = 'info' in sys.argv

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

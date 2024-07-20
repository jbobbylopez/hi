import sys
import time
import subprocess
import socket
import re
import os
import yaml
import configparser
import check_ubuntu_eol
import df_bargraph
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.box import MINIMAL
from rich.align import Align
from rich.text import Text
import logging
import logging.handlers
import queue
import json


STATE_FILE_PATH = 'state.json'
STATE = {}
LOGGING_ENABLED = False

def get_script_dir():
    ''' Returns the directory where the script is running from '''
    return os.path.dirname(os.path.abspath(__file__))

# Read in 'config/config.ini'
script_dir = get_script_dir()
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(script_dir), 'config/config.ini'))

def center_text(text):
    """
    Center the given text based on the terminal width using Rich.
    """
    return Align.center(text)

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

def get_config_yaml(config_yaml):
    with open(config_yaml, 'r') as file:
        config = yaml.safe_load(file)
    return config

def check_record_handler(check, output, indicators):
    check_record = {}
    check_record['name'] = check
    check_record['result'] = 'SUCCESS'
    check_record['icon'] = '✅' # Default positive indicator
    check_record['stat_date_str'] = None
    threshold_days = 7  # Assuming 7 days threshold for date_check

    if 'data backup' in check.lower():
        check_record['stat_date_str'] = output.strip().split(' ')[1]
        check_record['stat_date'] = datetime.strptime(check_record['stat_date_str'], '%Y-%m-%d')
        if datetime.now() - check_record['stat_date'] > timedelta(days=threshold_days):
            check_record['result'] = 'FAIL'
            check_record['icon'] = '❌'
            check_record['status'] = f"Last modified date {check_record['stat_date_str']} is older than {threshold_days} days"
        else:
            check_record['status'] = f"Last modified date {check_record['stat_date_str']} is within {threshold_days} days"

    elif 'expressvpn' in check.lower():
        if re.search("Connected", output.strip()):
            check_record['status'] = f"{check} Status: {output.strip()}"
        else:
            check_record['result'] = 'FAIL'
            check_record['icon'] = '❌'
            check_record['status'] = f"{check} Status: {output.strip()}"

    else:
        if indicators:
            if 'positive' in indicators and 'icon' in indicators['positive']:
                check_record['icon'] = indicators['positive']['icon']
            if 'positive' in indicators and 'status' in indicators['positive']:
                check_record['status'] = indicators['positive']['status']
        try:
            # this is not expected to work if indicators is not set - only
            # to trigger an exception
            check_record['icon'] = indicators['positive']['icon']
            check_record['status'] = indicators['positive']['status'].strip()
        except:
            # Exception is caught and dealth with gracefully when
            # indicators are not configured correctly.
            check_record['status'] = "is running" 

    return check_record


def compile_output_messages(check, cmd_output, group, info=None, indicators=None, sub_checks=None):
    status = ""
    check_indicators = None
    system_checks = {}
    check_record = {}
    output_messages = []

    # The below 'if output:' statement means that the command completed
    # successfully, and 'output' contains any data returned by the executed
    # command.  'check' contains the name of the check in config/checks.yml.
    if cmd_output:
        check_record = check_record_handler(check, cmd_output, indicators)
        output_messages.append(f"[{check_record['icon']}] {check}: {check_record['status']}")

    else:
        indicator = '❌'
        output = "is stopped"

        if indicators:
            try:
                indicator = indicators.get('negative', {}).get('icon', indicator)
                if 'negative' in indicators and 'status' in indicators['negative']:
                    output = indicators['negative']['status'] 

            except Exception as e:
                print(f"* Warning: Potential checks file configuration error.")
                print(f" - Indicator configuration resulted in error.")
                print(f" - Make sure you have matching postive/negative indicators and indicator icons.")
                print(f" Using default indicators.")
                indicator = '❌'
                
        output_messages.append(f"[{indicator}] {check} {output}")
        check_record['name'] = check
        check_record['result'] = 'FAIL'
        check_record['icon'] = indicator
        check_record['status'] = output


    # Append info: value if present
    if info:
        output_messages.append(f"  [🔹] {info}")
        check_record['info'] = info

    # Append sub_checks if present
    # .. this will likely need to be turned into it's own function
    if sub_checks:
        check_record['sub_checks'] = {}
        for sub_check in sub_checks:
            check_record['sub_checks'][sub_check] = {}
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
                check_record['sub_checks'][sub_check]['icon'] = indicator
                check_record['sub_checks'][sub_check]['status'] = sub_check_output
                check_record['sub_checks'][sub_check]['command'] = sub_check_command

            else:
                if 'indicators' in sub_checks[sub_check]:
                    sub_check_indicators = sub_checks[sub_check]['indicators']
                    if 'negative' in sub_check_indicators and 'icon' in sub_check_indicators['negative']:
                        indicator = sub_check_indicators['negative']['icon']
                    if 'negative' in sub_check_indicators and 'status' in sub_check_indicators['negative']:
                        sub_check_output = sub_check_indicators['negative']['status'] 
                output_messages.append(f"  [{indicator}] {sub_check}: {sub_check_output}")

        check_record['sub_checks'][sub_check]['icon'] = indicator
        check_record['sub_checks'][sub_check]['status'] = sub_check_output
        check_record['sub_checks'][sub_check]['command'] = sub_check_command

    current_state = {check_record['name']:check_record['result'] }
    check_system_state(current_state, check_record)

    final_output = "\n".join(output_messages)
    return final_output


def check_argv_config_yaml_file():
    yml_file_path = None
    has_yml_file = None
    has_config = 'config' in sys.argv

    # Check each argument for a .yml file extension
    for arg in sys.argv:
        if arg.endswith('.yml'):
            yml_file_path = arg
            has_yml_file = 1
            break  # Stop at the first .yml file found

    if has_config and not has_yml_file:
        raise ValueError("No '*.yml' file path found in arguments.")
    
    if has_config and has_yml_file:
        return "config/" + yml_file_path


def check_engine_yaml(check_type, verbose=False):
    group_output = []
    sub_checks = None
    script_dir = get_script_dir()
    hi_dir     = os.path.dirname(script_dir)

    # read checks_file specified in config.ini
    # This is useful for quick testing other checks.yml files with
    # different names.
    # E.g.:  hi config config/my_custom_checks.yml
    ini_checks_file = config.get('Paths', 'checks_file')

    # read user-specified checks_file
    cli_checks_file = check_argv_config_yaml_file()

    if cli_checks_file:
        checks_yaml_file = cli_checks_file
    else:
        checks_yaml_file = ini_checks_file

    try:
        checks = get_config_yaml(os.path.join(hi_dir, checks_yaml_file))
        checks = checks['checks']
    except Exception as e:
        return str(e)

    for check, attribs in checks.items():
        if attribs['group'] == check_type:
            output = check_process(check, attribs['command'])
            sub_checks = attribs.get('sub_checks') if verbose else None
            info = attribs.get('info') if verbose else None
            indicators = attribs.get('indicators')
            group_output.append(compile_output_messages(check, output, check_type, info, indicators, sub_checks))

    return group_output


def enable_check_info():
    check_info = 0
    check_info = 1 in sys.argv or None
    return check_info

def display_checks():
    """
    Display categorized checks in Rich tables, handling unequal lists gracefully.
    """

    report_colors = {}
    table_colors = {}
    local_ip_result = get_ip_address()
    hostname_result = get_hostname_address()
    script_dir = get_script_dir()
    hi_dir     = os.path.dirname(script_dir)
    groups = get_config_yaml(os.path.join(hi_dir, "config/groups.yml"))['groups']

    if enable_check_info:
        info = 'info' in sys.argv
    else:
        info = None

    # Print hi tool display header
    report_colors['header_style'] = "" if config.get('Report', 'header_style') in [None, "None"] else config.get('Report', 'header_style')
    report_colors['hostname_style'] = "" if config.get('Report', 'hostname_style') in [None, "None"] else config.get('Report', 'hostname_style')
    report_colors['ip_style'] = "" if config.get('Report', 'ip_style') in [None, "None"] else config.get('Report', 'ip_style')
    console.print(f"⟪ HOST INFORMATION ⟫", end="", style=report_colors['header_style'])
    console.print(f" {hostname_result['hostname']}", end="", style=report_colors['hostname_style'])
    console.print(f" | {local_ip_result['ip_address']}", end="", style=report_colors['ip_style'])

    # Get all status messages for each target group in 'config/groups.yaml'
    group_statuses = {group: check_engine_yaml(group, info) for group in groups}

    # Rich table output
    # read number_of_columns per table specified in config.ini
    num_columns = int(config.get('Tables', 'number_of_columns'))
    table_colors['default_style'] = "" if config.get('Tables', 'default_style') in [None, "None"] else config.get('Tables', 'default_style')
    table_colors['header_style'] = "" if config.get('Tables', 'header_style') in [None, "None"] else config.get('Tables', 'header_style')
    table_colors['border_style'] = "" if config.get('Tables', 'border_style') in [None, "None"] else config.get('Tables', 'border_style')
    table_colors['column_style'] = "" if config.get('Tables', 'column_style') in [None, "None"] else config.get('Tables', 'column_style')
    table_colors['text_style'] = "" if config.get('Tables', 'text_style') in [None, "None"] else config.get('Tables', 'text_style')

    # Generate the tables
    for i in range(0, len(groups), num_columns):
        table = Table(
            show_header=True, 
            header_style=table_colors["header_style"],
            expand=True, 
            box=MINIMAL,
            border_style=table_colors["border_style"],
            style=table_colors["default_style"]
        )

        current_groups = groups[i:i + num_columns]
        for group in current_groups:
            table.add_column(group, style=table_colors["column_style"], justify="left", no_wrap=True, width=40)

        max_length = max(len(group_statuses[group]) for group in current_groups)

        for j in range(max_length):
            row = [
                Text(group_statuses[group][j], style=table_colors['text_style']) 
                if j < len(group_statuses[group]) 
                else ""
                for group in current_groups
            ]
            table.add_row(*row)

        console.print(table)

def display_hi_report():
    display_checks()  # Call the display_checks function to print the system checks
    check_ubuntu_eol.main()
    df_bargraph.display_bar_graph()


def display_hi_watch_report():
    print("\033[H", end='')  # ANSI escape code to move cursor to top-left
    display_hi_report()
    console.print(center_text("[🟢] watching.. (ctrl-c to quit)"), style="bold green")
    print("\033[J", end='')  # Clear the rest of the screen from the cursor position

def hide_cursor_clear_screen():
    print("\033[?25l", end='')  # Hide the cursor
    print("\033[H", end='')  # ANSI escape code to move cursor to top-left
    print("\033[J", end='')  # Clear the rest of the screen from the cursor position

def hi_watch(interval=2):
    """
    Continuously display the output of the display_checks function, updating every 'interval' seconds.
    """
    hide_cursor_clear_screen()
    display_hi_watch_report()
    if 'watch' in sys.argv:
        try:
            while True:
                time.sleep(interval)  # Wait for the specified interval before updating again
                display_hi_watch_report()
        except KeyboardInterrupt:
            console.clear()
            console.print("\n[hi: continuous monitoring stopped.]")
        finally:
            print("\033[?25h", end='')  # Ensure the cursor is shown when exiting

# Custom JSON formatter for log records
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "level": record.levelname,
            "message": record.getMessage(),
            "check_name": record.check_name,
            "previous_state": record.previous_state,
            "new_state": record.new_state
        }
        return json.dumps(log_record)

def configure_logging(log_file_path):
    log_queue = queue.Queue()

    # Queue handler to handle log records
    queue_handler = logging.handlers.QueueHandler(log_queue)
    
    # File handler to write log records to a file
    file_handler = logging.FileHandler(log_file_path, mode='a')  # 'a' for append mode
    file_handler.setFormatter(JsonFormatter())

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(queue_handler)

    # Listener to process log records from the queue
    listener = logging.handlers.QueueListener(log_queue, file_handler)
    listener.start()

def log_state_change(check_name, previous_state, new_state):
    logging.info(
        f'{check_name} state changed from {previous_state} to {new_state}',
        extra={
            'check_name': check_name,
            'previous_state': previous_state,
            'new_state': new_state
        }
    )

def read_initial_state():
    if not os.path.isfile(STATE_FILE_PATH):
        return {}
    with open(STATE_FILE_PATH, 'r') as f:
        return json.load(f)

def state(state):
    if state == {}:
        global STATE
        STATE = read_initial_state()
    return STATE

def write_state(state):
    with open(STATE_FILE_PATH, 'w') as f:
        json.dump(state, f, indent=4)

def check_system_state(current_state, check_record):
    # Dictionary to store the initial state
    last_known_state = state(STATE)

    # Compare current state with last known state
    for check_name, new_state in current_state.items():
        if check_name == check_record['name']:
            previous_state = last_known_state.get(check_name)
            if previous_state != new_state:
                last_known_state[check_name] = new_state

                # log state change
                if LOGGING_ENABLED:
                    log_state_change(check_name, previous_state, new_state)

                # Update the state file with the new state
                write_state(last_known_state)

# Configure logging at the start of your script

try:
    LOGGING_ENABLED = config.get('Logging', 'enable_logging')
    ini_log_file = config.get('Paths', 'log_file')
    if ini_log_file and LOGGING_ENABLED.lower() == "true":
        configure_logging(ini_log_file)
except Exception as e:
    print(f"Error: log_file not configured correctly in config.ini: {e}")


# Call the function to execute
console = Console()
if 'watch' in sys.argv:
    hi_watch()
else:
    display_hi_report()

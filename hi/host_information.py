"""
'hi' - Host Information: Main Program.
"""
import sys
import time
import subprocess
import daemon
import daemon.pidfile
import traceback
import socket
import re
import os
import psutil
import yaml
import configparser
import lockfile

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

# 'hi' internal dependencies
import check_os_eol
import df_bargraph

def get_script_dir():
    ''' Returns the directory where the script is running from '''
    return os.path.dirname(os.path.abspath(__file__))
script_dir = get_script_dir()


# Initial State Globals
STATE = {}
STATE_FILE_PATH = os.path.join(os.path.dirname(script_dir), 'state.json')
LOGGING_ENABLED = False



""" Utilities """
"""
Small / uncategorized tools and utilties that support the program functionality.
"""
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

def flush_loggers():
    """Flush all loggers to ensure all messages are written out."""
    for handler in logging.getLogger().handlers:
        handler.flush()



""" Modules """
"""
Modules to the main 'hi' program, which perform specific custom functions.
Modules are specific to various defined checks, like ExpressVPN, or Data Backups.
"""
def module_data_backup(check_record, output, fail_icon, fail_status):
    stat_threshold = config.get('Defaults', 'stat_threshold')
    check_record['stat_date_str'] = None
    threshold_days = int(stat_threshold)  # Assuming 7 days threshold for date_check
    check_record['stat_date_str'] = output.strip().split(' ')[1]
    check_record['stat_date'] = str(datetime.strptime(check_record['stat_date_str'], '%Y-%m-%d'))
    if datetime.now() - datetime.strptime(check_record['stat_date'], "%Y-%m-%d %H:%M:%S") > timedelta(days=threshold_days):
        check_record['result'] = fail_status
        check_record['icon'] = fail_icon
        check_record['status'] = f"Last modified date {check_record['stat_date_str']} is older than {threshold_days} days"
    else:
        check_record['status'] = f"Last modified date {check_record['stat_date_str']} is within {threshold_days} days"
    return check_record

def module_expressvpn(check_record, output):
    # Get INI defaults
    fail_icon = config.get('Defaults', 'fail_icon')
    fail_status = config.get('Defaults', 'fail_status')
    success_icon = config.get('Defaults', 'success_icon')
    success_status = config.get('Defaults', 'success_status')
    info_icon = config.get('Defaults', 'info_icon')

    if re.search("Connected", output.strip()):
        check_record['result'] = output.strip()
        check_record['status'] = f"Status: {output.strip()}"
        check_record['icon'] = success_icon
    else:
        check_record['result'] = fail_status
        check_record['icon'] = fail_icon
        check_record['status'] = f"Status: {output.strip()}"
    return check_record



""" Check Processors """
"""
Various filters and processors of checks defined.
"""
def check_record_handler(check, group, output, indicators):
    # Get INI defaults
    fail_icon = config.get('Defaults', 'fail_icon')
    fail_status = config.get('Defaults', 'fail_status')
    success_icon = config.get('Defaults', 'success_icon')
    success_status = config.get('Defaults', 'success_status')
    info_icon = config.get('Defaults', 'info_icon')

    check_record = {}
    check_record['name'] = check
    check_record['group'] = group
    check_record['result'] = success_status
    check_record['icon'] = success_icon # Default positive indicator

    if 'data backup' in check.lower():
        check_record = module_data_backup(check_record, output, fail_icon, fail_status)

    elif 'expressvpn' in check.lower():
        check_record = module_expressvpn(check_record, output)

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
            check_record['status'] = success_status

    return check_record

def core_module_subchecks(check_record, sub_checks, indicators):
    check_record['sub_checks'] = {}
    for sub_check in sub_checks:
        check_record['sub_checks'][sub_check] = {}
        indicator = '⚫'
        status = ""
        sub_check_indicators = None
        sub_check_command = sub_checks[sub_check]['command']
        sub_check_output = check_process(sub_check, sub_check_command).strip()

        if sub_check_output:
            sub_check_indicators = sub_checks[sub_check].get('indicators', {})
            positive_indicators = sub_check_indicators.get('positive', {})

            indicator = positive_indicators.get('icon')
            status = positive_indicators.get('status')

        else:
            sub_check_indicators = sub_checks[sub_check].get('indicators', {})
            negative_indicators = sub_check_indicators.get('negative', {})

            indicator = negative_indicators.get('icon')
            status = negative_indicators.get('status')

        check_record['sub_checks'][sub_check]['icon'] = indicator
        check_record['sub_checks'][sub_check]['status'] = status
        check_record['sub_checks'][sub_check]['output'] = sub_check_output
        check_record['sub_checks'][sub_check]['command'] = sub_check_command

    return check_record

def compile_check_results(check, cmd_output, group, info=None, indicators=None, sub_checks=None):
    status = ""
    check_indicators = None
    system_checks = {}
    check_record = {}
    output_messages = []

    # Get INI defaults
    fail_icon = config.get('Defaults', 'fail_icon')
    fail_status = config.get('Defaults', 'fail_status')
    success_icon = config.get('Defaults', 'success_icon')
    success_status = config.get('Defaults', 'success_status')
    info_icon = config.get('Defaults', 'info_icon')

    # The below 'if output:' statement means that the command completed
    # successfully, and 'output' contains any data returned by the executed
    # command.  'check' contains the name of the check in config/checks.yml.
    if cmd_output:
        check_record = check_record_handler(check, group, cmd_output, indicators)

    else:
        indicator = fail_icon
        output = fail_status

        if indicators:
            try:
                indicator = indicators.get('negative', {}).get('icon', indicator)
                if 'negative' in indicators and 'status' in indicators['negative']:
                    output = indicators.get('negative', {}).get('status', fail_status)

            except Exception as e:
                print(f"* Warning: Potential checks file configuration error.")
                print(f" - Indicator configuration resulted in error.")
                print(f" - Make sure you have matching postive/negative indicators and indicator icons.")
                print(f" Using default indicators.")
                indicator = fail_icon
                
        check_record['name'] = check
        check_record['group'] = group
        check_record['result'] = output
        check_record['icon'] = indicator
        check_record['status'] = fail_status

    check_record['info'] = info

    # Append sub_checks if present
    if sub_checks:
        check_record = core_module_subchecks(check_record, sub_checks, indicators)

    current_state = {check_record['name']:check_record['result']}
    update_system_state(current_state, check_record)

def get_check_results_data(groups, info):
    ''' This function aggregates all the check results into a dict, and
    returns that data for parsing and display output processing '''

    if 'daemon' in sys.argv:
        info = "info"
        for group in groups:
            check_engine_yaml(group, info)
    else:
        check_results_data = state()
        return check_results_data


""" YAML Processors """
"""
Various YAML file and check processors
"""
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
            output = check_process(check, attribs['command']) # The actual execution of commands
            sub_checks = attribs.get('sub_checks') if verbose else None
            info = attribs.get('info') if verbose else None
            indicators = attribs.get('indicators')
            compile_check_results(check, output, check_type, info, indicators, sub_checks)

def enable_check_info():
    check_info = None
    if 'info' in sys.argv:
        check_info = 1
    else:
        check_info = None
    return check_info



""" Daemon controls """
"""
Functions that support daemon initialization and functionality
"""
def read_pid_file(pidfile):
    try:
        with open(pidfile, 'r') as f:
            pid = int(f.read().strip())
        return pid
    except (IOError, ValueError):
        return None

def is_process_running(pid):
    try:
        return psutil.pid_exists(pid) and psutil.Process(pid).is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False

def hi_daemon():
    ''' Hi Daemon '''
    '''
    This function sets up the daemon context (server context) of the program.

    This allows the application to run headless (without the need for GUI or command-line).

    The application would run as a daemon in the background, and would publish state
    information that could be parsed by the hi command line client (client context).
    '''
    pidfile = '/tmp/hi_daemon.pid'
    pid = read_pid_file(pidfile)

    if pid and is_process_running(pid):
        print(f"hi_daemon() is already running (PID: {open(pidfile).read().strip()}).")
        sys.exit(1)
    elif pid: #PID file exists but process not running
        print(f"Removing stale PID file (PID: {pid}).")
        os.remove(pidfile)

    try:
        log_state_change("hi_daemon()", "offline", "starting..")
        console.print(f"hi_daemon() started.")
        with daemon.DaemonContext(
            working_directory='.',  # Ensure this is a valid directory for your process
            umask=0o022,
            pidfile=daemon.pidfile.PIDLockFile(pidfile),
            stderr=sys.stderr,  # Redirect stderr to catch daemon errors
            stdout=sys.stdout   # Redirect stdout to catch daemon logs
        ):
            pid = read_pid_file(pidfile)
            hi_daemon_process(pid,2)
    except PermissionError as e:
        console.print(f"\n[Permission error: {e}]")
        logging.debug(f"Permission error: {e}")
    except FileNotFoundError as e:
        console.print(f"\n[File not found: {e}]")
        logging.debug(f"File not found: {e}")
    except Exception as e:
        console.print(f"\n[An error occurred: {e}]")
        console.print(f"Exception in daemon context: %s", str(e))
        console.print(f"Traceback: %s", traceback.format_exc())
    finally:
        log_state_change("hi_daemon()", "running", "shutting down")
        if os.path.exists(pidfile):  # Cleanup the PID file
            os.remove(pidfile)
            log_state_change("hi_daemon()", f"pidfile ({pid})", "pid file removed")

def hi_daemon_process(pid,interval=2):
    """
    Main daemon process handler
    
    This function calls get_check_results_data() function which
    will either trigger a new call to check_engine_yaml() to generate
    a new list of check resutls (server context), or it call read_daemon_results() to
    read current state information (client context).

    This function accepts the 'interval' argument which controls the frequency
    of check execution and state update.
    """
    configure_logging(ini_log_file)
    console.print(f"hi_daemon_process() running (PID: {pid}).")
    log_state_change("hi_daemon_process()", "started", "running..")

    local_ip_result = get_ip_address()
    hostname_result = get_hostname_address()
    script_dir = get_script_dir()
    hi_dir     = os.path.dirname(script_dir)
    groups = get_config_yaml(os.path.join(hi_dir, "config/groups.yml"))['groups']
    check_results_data = None

    if enable_check_info():
        info = 'info' in sys.argv
    else:
        info = None

    while True:
        time.sleep(interval)  # Wait for the specified interval before updating again

        # Get all status messages for each target group in 'config/groups.yaml'
        check_results_data = get_check_results_data(groups, info)

def state(state = {}):
    if state == {}:
        try:
            state = read_initial_state()
        except Exception as e:
            console.print(f"Exception {e}")
    return state

def read_initial_state():
    if not os.path.isfile(STATE_FILE_PATH):
        return {}
    with open(STATE_FILE_PATH, 'r') as f:
        return json.load(f)

def write_state(state):
    try:
        with open(STATE_FILE_PATH, 'w') as f:
            json.dump(state, f, indent=4)
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")

def update_system_state(current_state, check_record):
    # Dictionary to store the initial state
    last_known_state = state(STATE)
    previous_state = None

    # Compare current state with last known state
    for check_name, new_state in current_state.items():
        if check_name == check_record['name']:
            try:
                previous_state = last_known_state.get(check_name)
                if previous_state:
                    if previous_state['result'] != new_state:
                        if LOGGING_ENABLED:
                            log_state_change(check_name, previous_state['result'], new_state)

                # Update the state file with the new state
                last_known_state[check_name] = check_record
                write_state(last_known_state)
            except Exception as e:
                console.print(f"\n[An error occurred: {e}]")
                console.print(f"Exception in daemon context: %s", str(e))
                console.print(f"Traceback: %s", traceback.format_exc())


""" Terminal Control and Command-line Interfaces """
"""
The following functions support curses terminal output and control, along with
processing of command-line arguments.
"""
def hide_cursor_clear_screen():
    print("\033[?25l", end='')  # Hide the cursor
    print("\033[H", end='')  # ANSI escape code to move cursor to top-left
    print("\033[J", end='')  # Clear the rest of the screen from the cursor position

def hi_watch(interval=2):
    """
    Continuously display the output of the checks(), updating every 'interval' seconds.
    """
    hide_cursor_clear_screen()
    hi_watch_report()
    if 'watch' in sys.argv:
        try:
            while True:
                time.sleep(interval)  # Wait for the specified interval before updating again
                hi_watch_report()
        except KeyboardInterrupt:
            console.clear()
            console.print('hi: continuous monitoring stopped.')
        finally:
            print("\033[?25h", end='')  # Ensure the cursor is shown when exiting

def hi_report():
    checks()  # Call the checks() print the system checks
    check_os_eol.main()
    df_bargraph.display_bar_graph()


def hi_watch_report():
    print("\033[H", end='')  # ANSI escape code to move cursor to top-left
    hi_report()
    console.print(center_text("[🟢] watching.. (ctrl-c to quit)"), style="bold green")
    print("\033[J", end='')  # Clear the rest of the screen from the cursor position



""" 'rich' terminal control and display """
"""
Various functions that support terminal output display control.
"""
def center_text(text):
    """
    Center the given text based on the terminal width using Rich.
    """
    return Align.center(text)

def generate_rich_tables(groups, check_results_data, table_colors, num_columns):
    info_icon = config.get('Defaults', 'info_icon')
    all_group_statuses = {group: [] for group in groups}

    # Organize data by groups
    for key, value in check_results_data.items():
        group = value.get('group', 'No group')
        status = f"{value['icon']} {value['name']} - {value['status']}"
        info = f"{value['info']}"

        sub_checks = None
        if 'sub_checks' in value:
            sub_checks = value['sub_checks']

        if group in groups:
            all_group_statuses[group].append(status)
            if enable_check_info() and value['info']:
                all_group_statuses[group].append(f"  [{info_icon}] {info}")
            if sub_checks:
                for sub_check in sub_checks:
                    all_group_statuses[group].append(f"    [{sub_checks[sub_check]['icon']}] {sub_check}: {sub_checks[sub_check]['status']} {sub_checks[sub_check]['output']}")

    # Create tables
    for i in range(0, len(groups), num_columns):
        console = Console()
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

        max_length = max(len(all_group_statuses[group]) for group in current_groups)

        for j in range(max_length):
            row = [
                #Text(f"hello! {max_length}/{j} - {len(all_group_statuses[group])}")
                Text(all_group_statuses[group][j], style=table_colors['text_style'])
                if j < len(all_group_statuses[group])
                else ""
                for group in current_groups
            ]
            table.add_row(*row)

        console.print(table)

def checks():
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

    # Get hi tool display header styles
    report_colors['header_style'] = "" if config.get('Report', 'header_style') in [None, "None"] else config.get('Report', 'header_style')
    report_colors['hostname_style'] = "" if config.get('Report', 'hostname_style') in [None, "None"] else config.get('Report', 'hostname_style')
    report_colors['ip_style'] = "" if config.get('Report', 'ip_style') in [None, "None"] else config.get('Report', 'ip_style')

    # construct the header
    header_text = Text()
    report_title = "⟪ HOST INFORMATION ⟫"
    hostname = hostname_result['hostname']
    local_ip = local_ip_result['ip_address']
    header_text = f"{report_title} | {hostname} | {local_ip}"

    # print the header
    console.print(f"{report_title}", end="", style=report_colors['header_style'])
    console.print(' | ', end="", style=report_colors['ip_style'])
    console.print(f"{hostname}", end="", style=report_colors['hostname_style'])
    console.print(' | ', end="", style=report_colors['ip_style'])
    console.print(f"{local_ip}", end="", style=report_colors['ip_style'])
    console.print(' ' * (console.width - len(header_text)), style=report_colors['ip_style'])

    # Get all status messages for each target group in 'config/groups.yaml'
    check_results_data = get_check_results_data(groups, info)

    # Rich table output
    # read number_of_columns per table specified in config.ini
    num_columns = int(config.get('Tables', 'number_of_columns'))
    table_colors['default_style'] = "" if config.get('Tables', 'default_style') in [None, "None"] else config.get('Tables', 'default_style')
    table_colors['header_style'] = "" if config.get('Tables', 'header_style') in [None, "None"] else config.get('Tables', 'header_style')
    table_colors['border_style'] = "" if config.get('Tables', 'border_style') in [None, "None"] else config.get('Tables', 'border_style')
    table_colors['column_style'] = "" if config.get('Tables', 'column_style') in [None, "None"] else config.get('Tables', 'column_style')
    table_colors['text_style'] = "" if config.get('Tables', 'text_style') in [None, "None"] else config.get('Tables', 'text_style')

    # Generate the tables
    generate_rich_tables(groups, check_results_data, table_colors, num_columns)



""" Logging and Log Management """
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



""" MAIN PROGRAM """
"""
'hi' program control flow starts here.
"""
# Read in 'config/config.ini'
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(script_dir), 'config/config.ini'))

# Configure logging if logging is enabled
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
elif 'daemon' in sys.argv:
    hi_daemon()
else:
    hi_report()

import subprocess
import yaml

def check_bash_command_syntax(command):
    try:
        # Use subprocess to run the bash command with syntax checking
        result = subprocess.run(['bash', '-n', '-c', command], capture_output=True, text=True)
        
        # Check the return code and prepare the message
        if result.returncode != 0:
            return f"Syntax error: {result.stderr.strip()}"
        else:
            return "Syntax is good! 😊"
    except Exception as e:
        return f"An error occurred: {e}"

def main():
    # Load the checks.yml file
    with open('checks.yml', 'r') as file:
        data = yaml.safe_load(file)
    
    # Loop through each command in the file
    checks = data.get('checks', {})
    for name, details in checks.items():
        command = details.get('command', '').strip()
        print(f"Checking {name} ({details.get('group', 'Unknown')}):")
        print(f"Command: {command}")
        status = check_bash_command_syntax(command)
        print(f"Status: {status}\n")
        print('-' * 40 + '\n')

if __name__ == "__main__":
    main()

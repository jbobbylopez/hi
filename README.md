![Screenshot of Hi](assets/hi-example-screenshot.png)

hi - Host Information
=====================

"hi" is a command-line tool designed to monitor and display the status of various services running on a host. The services and their respective checks are customizable via a YAML configuration file, allowing for flexibility to suit different monitoring needs. This tool leverages the Rich library to provide visually pleasing output that includes UTF8 status icons, so it should be run in a terminal that supports the UTF8 character-set.

Features
--------

*   Highly customizable checks that can report on any command-line executable status.
    
*   Verifies the running status of various services.
    
*   Checks the last modified date of backup logs to ensure up-to-date backups.
    
*   Monitors the connectivity status of ExpressVPN.
    
*   Displays the local IP address and hostname of the host.
    
*   Utilizes the Rich library for visually appealing console output with UTF8 status icons.
    

Getting Started
---------------

### Prerequisites

Ensure you have the following installed on your system:

*   Python 3.x (>= 3.6)
    
*   Required Python modules:
    
    *   subprocess
        
    *   socket
        
    *   re
        
    *   os
        
    *   pyyaml
        
    *   rich
        

Ensure that your terminal supports the UTF8 character set for proper display of status icons.

You can install the dependencies via pip:
`   pip install pyyaml rich   `

### Installation

1.  git clone https://github.com/jbobbylopez/hi.git
cd hi
    
2.  python3 --version
    
3.  pip install -r requirements.txt
    

### Configuration

Customize the services and checks in the config/checks.yml file located in the repository. This configuration file allows you to define any number of checks to monitor services or functionalities available via the command line.

Example configuration reference:
```
checks:
  qbittorrent:
    info: My bittorrent client
    group: Media
    command: |
      ps -ef | grep -E '([q]bittorrent)'
  ...
```

### Usage

1.  python3 host\_information.py
    
2.  **(Optional)** Set up a bash function and alias to run the script more easily.
    

Add an alias to your ~/.bashrc to call this script:
`alias hi="/path/to/hi/host_information.py $@"`

After adding these lines, save the ~/.bashrc file and apply the changes:
`source ~/.bashrc`

Now you can run the script using the command:
`hi`

#### Options and Arguments
Arguments:
-verbose - show check description from the 'info:' field in the checks.yml file.

#### Setting Up a Continuously Updating Monitor for 'hi'
To set up a continuosly updating view of the hi output, you can set up another bash function and alias.  Add the follwoing function to your ~/.bashrc file:
In this case, the watch command would monitor the output of 'hi' every 2 seconds.
```
host_information_watch() {
    clear
    watch -c -n 2 "python3 ~/path/to/hi/host_information.py"
}
```
Again, replace ~/path/to/hi/ with the actual path to where you cloned the repository.

Then, add an alias to call this function:
`alias hi_watch=host_information_watch`

After adding these lines, save the ~/.bashrc file and apply the changes:
`source ~/.bashrc`

Now you can run the continuously updating output from 'hi' using the command:
`hi_watch`

### Example Output ###

Here's an example of how the output will appear:
![Screenshot of Hi](assets/hi-example-screenshot.png)

### How It Works ###
*Configuration Loading:* The script starts by loading the YAML configuration file (config/checks.yml). This file specifies different services and checks categorized into groups such as Media, Tools, Security, Backup, Data, and Mount.
```
def get_checks_yaml(checks_yaml):
    with open(checks_yaml, 'r') as file:
        checks = yaml.safe_load(file)
    return checks
```
*Execution of Commands:* For each defined service, the corresponding command is executed using the subprocess.run method. The output of these commands determines the status of each service. The shell=True option allows the commands to be run in the shell, making it compatible with commands involving pipes and other shell features.
```
def check_process(process, command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout
```
### Customizing the Checks ###
The config/checks.yml file defines the checks that the tool will perform. Each entry in the file specifies a group and a command.
- group: The category of the service (e.g., Tools, Data, Backup, Media, Security, Mount).
- command: The shell command to check the status of the service.

You can add or modify checks to suit your needs. For example:
```
new_service:
  group: Tools
  command: ps -ef | grep -i '[n]ew_service'
```

### Contributing ###
1. Fork the repository.
2. Create your feature branch (git checkout -b feature/awesome-feature).
3. Commit your changes (git commit -m 'Add some awesome feature').
4. Push to the branch (git push origin feature/awesome-feature).
5. Open a Pull Request.

### Testing ###
Preliminary tests have been defined in 'test_host_information.py', many
more are expected to be added as the code for this tool increases in
complexity.  You can run the tests yourself as follows:
    pytest -v test_host_information.py

### License ###
This project is licensed under the MIT License. See the LICENSE file for details.

### Acknowledgements ###
Inspiration for this tool has come from various sources, including btop, glances, htop, and midnight commander.

### Contact ###
Want to talk about this tool? Feel free to reach me via github or linkedin.

### Note ###
This tool has so far only been tested on Ubuntu 22.04 LTS.

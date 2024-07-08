![Screenshot of Hi](assets/Screenshot_20240707_133302-hi-verbose-output.png)

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
        

You can check your version of python with the following command:
`   python3 --version   `

Ensure that your terminal supports the UTF8 character set for proper display of status icons.

You can install the dependencies via pip:
`   pip install pyyaml rich   `


### Installation

1.  `git clone https://github.com/jbobbylopez/hi.git`

`cd hi`
    
2.  `pip install -r requirements.txt`

3.  `python3 host_information.py`
    

### Configuration

Customize the services and checks in the `config/checks.yml` file located in the repository. This configuration file allows you to define any number of checks to monitor services or functionalities available via the command line.

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

Also be sure to read the article [Say "hi" to your Linux Host
Information](https://dev.to/jbobbylopez/saying-hi-to-your-linux-host-information-4fh6)
to learn about how to instrument more complex system checks.

### Usage

1.  `python3 host_information.py`
    
2.  **(Optional)** Set up a bash function and alias to run the script more easily.
    

Add an alias to your ~/.bashrc to call this script:

`alias hi="python3 /home/jbl/scripts/hi/host_information.py $@"`

After adding these lines, save the ~/.bashrc file and apply the changes:
`source ~/.bashrc`

Now you can run the script using the command:
`hi`

#### Options and Arguments
Arguments:

-  '-verbose': Show check description from the 'info:' field in the checks.yml file.


### Example Output ###

Here's an example of how the output will appear:
![hi tool output](assets/hi-example-screenshot.png)

An example of verbose output, showing the system check 'info:' field data:
![verbose output](assets/Screenshot_20240707_133302-hi-verbose-output.png)

### How It Works ###
The main section is a set of one or more two-column tables with group names
for their column headers.

Within each column, a list of system checks are displayed, showing either
disabled/enabled, or active/inactive, represented by [❌] and [✅]
respectively. Different indicators may be employed based on the groups
configured.  For example, the Tools group uses the [💡] and [⚫]
indicators.

After the system checks, two other pieces of system information is
displayed.  The Operating System End-of-Life date, and a filesystem
utilization summary.  This section looks like the following:

![OS EOL and Filesystem Output](assets/Screenshot_20240708_014437-filesystem-os-eol.jpeg)

### Behind The Scenes ###
To get an idea of how this all comes together, consider the following:

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
  command: ps -ef | grep -i "[n]ew_service"
```
You can review all the existing checks defined in `config/checks.yml` for more examples.

#### Setting Up a Continuously Updating Monitor for 'hi'
To set up a continuosly updating view of the hi output, you can set up another bash function and alias.  Add the following function to your ~/.bashrc file:
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

### Contributing ###
1. Fork the repository.
2. Create your feature branch (git checkout -b feature/awesome-feature).
3. Commit your changes (git commit -m 'Add some awesome feature').
4. Push to the branch (git push origin feature/awesome-feature).
5. Open a Pull Request.

### Testing ###
Preliminary tests have been defined in `test_host_information.py`, many
more are expected to be added as the code for this tool increases in
complexity.  You can run the tests yourself as follows:
    `pytest -v test_host_information.py`

### License ###
This project is licensed under the MIT License. See the LICENSE file for details.

### Acknowledgements ###
Inspiration for this tool has come from various sources, including btop, glances, htop, and midnight commander.

### Contact ###
Want to talk about this tool? Feel free to reach me via github or linkedin.

### Note ###

This tool has so far only been tested with the following system specifications:

------------------- 
- OS: Kubuntu 22.04.4 LTS x86_64 
- Kernel: 5.15.0-112-generic 
- Shell: bash 5.1.16 
- Python: 3.10.12.
- DE: Plasma 5.25.5 
- WM: KWin 
- Theme: Breeze Light [Plasma], Breeze [GTK3] 
- Icons: [Plasma], candy-icons [GTK2/3]

It is possible that your OS + Python version combination, or some aspect of
your OS or distro configuration may result in errors being thrown by this tool if
you attempt to use it.  

I of course take no responsibility for any harm this tool may cause to your
system.  You use this tool at your own risk.

I would however like to learn of any issues experienced using this tool.
If you happen to hit a bug or exception, or something doesn't look right,
kindly file a GitHub issue with the error details. Provide full error details,
along with your OS and system specifications. 

Please and thanks!

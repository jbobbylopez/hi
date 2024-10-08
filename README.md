![Screenshot of Hi](assets/Screenshot_20240707_133302-hi-verbose-output.png)

hi - Host Information
=====================

## Early Development Notice - 🚨
Please note that this tool is still in early development.  Things will change,
and there will likely be bugs along the way.

Star and watch the project to stay updated on development activities.

If you are looking for a more mature tool in this space that is quite
featureful and supports configuration of custom alerts in YAML, I highly
recommend taking a look at [glances](https://github.com/nicolargo/glances).


## Summary
"hi" is a command-line tool designed to monitor and display the status of various services running on a host. 
The services and their respective checks are customizable via a YAML configuration file, allowing for 
flexibility to suit different monitoring needs. This tool leverages the Rich library to provide visually
pleasing output that includes UTF8 status icons, so it should be run in a terminal that supports the UTF8
character-set.

You know the Linux '[watch](https://linuxhandbook.com/watch-command/)' command? The *hi* tool is just that, on steroids.

### Some History
What is the 'watch' command? It is a handy little tool that lets you execute a program periodically and watch the output
change in real-time. It is super useful for monitoring things like system performance or changes in directory contents.

The watch command traces its roots back to the early days of Unix-like systems. It was developed to help users keep an
eye on command output over time without having to manually re-run the command. 

*hi* takes this functionalty, and pairs it with highly customizable and
flexible monitoring and reporting dashboard with notification, alerting,
logging, and API integration capabilities.


## Target Audience

*hi* is a monitoring and reporting tool for Linux power users who tend to live on the command line.
These would be engineers, developers, researchers, systems administrators, and security experts who
are regularly hands-on with the systems they are building and maintaining. For folks such as these,
who appreciate the power of the command-line to get real work done, hi offers insightful monitoring
and reporting tools to elevate their efficiency and effectiveness. 
For those who rely on and benefit from the Linux and Open Source community to make sense of the world, this is for you.


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
    
You can check your version of python with the following command:
`   python3 --version   `

*   Required Python modules:
See ` requirements.txt `.        

Ensure that your terminal supports the UTF8 character set for proper display of status icons.


### Installation

Lets say your working directory is ~/tools/.  `cd ~/tools/` and do the
following:

1.  `git clone https://github.com/jbobbylopez/hi.git`

`cd hi`
    
2.  `pip install -r requirements.txt`

3.  Update ` config/config.ini ` and your custom ` checks.yml ` file
    accordingly.

4. Add an alias to your ~/.bashrc to call this script:

`alias hi="python3 /home/tools/hi/hi/host_information.py $@"`

After adding these lines, save the ~/.bashrc file and apply the changes:
`source ~/.bashrc`

Now you can run the tool using the commands:

To start the daemon:
`hi daemon` 

To run the cli client:
`hi`

or
`hi watch info`

#### Options and Arguments - the *hi* cli
You typically just want to run ` hi `, but there are a few options and
arguments to the tool you might want to be aware of.

Arguments:

-  'daemon': Run the 'hi' daemon.
-  'info': Show check description and sub-checks.
-  'watch': Native watch command for ongoing monitoring.
-  'config': Specify another status checks file that resides in 'config/'.
            E.g. `  hi config my-checks.yml  ` 


# Configuration
There are currently three (3) configuration files that 'hi' depends on.  They are as
follows:
- config/config.ini
- config/groups.yml

Depending on the groups you define in `groups.yml`, you will need a single .yml file defined for each group.  You will see by default the following configuration files are already in place:

- config/Security.yml
- config/Data.yml
- config/Tools.yml
- config/Media.yml
- .. and so on.

## config/config.ini ####
This file is the main configuration file that tells 'hi' what files it needs and options it should enable.

You can configure table output options to customize how your reports
displayed.

##### config.ini example #####
```
[Defaults]
fail_icon = 🔴
fail_status = stopped
success_icon = ✅
success_status = running
info_icon = 📘
stat_threshold = 7

[Paths]
log_file = hi_log.json

[Report]
header_style = bold dark_blue on cyan
hostname_style = bright_blue on black
ip_style = bold bright_green on black

[Tables]
number_of_columns = 3 
default_style = green
header_style = bright_green on black
border_style = bright_white 
column_style = bright_blue
text_style = None

[OS Bar]
os_text_style = black on green

[Logging]
enable_logging = true

```

## config/<checks_group>.yml ##
This is where the magic happens.  The `  config/<checks_group>.yml  ` file is where
your system status checks are defined. The naming convention of this file must follow the group names identified you config/groups.yml.

This configuration file allows you to define any number of system status checks to monitor services or functionalities available via the command line.

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

Several examples of various system status checks are available for review
or reuse in the ` config/example.yml ` files that comes with this tool.


### sub-checks
You can now define multiple sub-checks using the same check declaration pattern.

Here's an example of how sub-checks are configured.  We will use the
'Thunderbird' check which comes pre-defined in config/checks.yml.

In the following check defined for Thunderbird, you can see that not only is the
main check for the running process in place, but there are also two
sub-checks defined for checking Thunderbird's 'Memory Usage' and 'Version'
information.

```
  Thunderbird:  
    info: My favorite mail client
    group: Communications            
    indicators:                                                                   
      positive:                     
        status:    
        icon: 📧
      negative:                         
        status:
        icon: 📧
    command: | 
      ps -ef | grep -E "[t]hunderbird"
    sub_checks:              
      Memory Usage:                     
        command: |
          ps --no-headers -o rss -C thunderbird | awk '{sum+=$1} END {printf "%.2f MB (%.2f GB)\n", sum/1024, sum/1048576}'                                         
        indicators:  
          positive:
              icon: 💾                                                            
          negative:
              icon: 💾    
      Version:    
        command: |                                                                                                                                                  
          thunderbird --version
```
### Custom Indicators

In the above Thunderbird check configuration example, you can also see the
custom indicators which can be defined within the config/checks.yml file.

These custom indicators, when defined, will override the default check
'hi' check indicators (in most cases).

You can see that custom indicators have been defined not just for
Thunderbird, but also for it's 'Memory Usage' sub-check.  The 'Version'
sub-check does not have any indicators defined, and so that sub-check will
use the default indicators.

An example of what the output looks like when `  hi info  ` is run:
![Sub-checks and Indicators](assets/Screenshot_20240709_034009-subchecks-indicators-output.png)

As you can see, the check description (info field), along with the
sub-checks are indented slightly from the main checks so that they are
nicely grouped together.

## The 'hi' daemon ##
'hi' is now implemented as a client/server application that requires the
monitoring component to be run as a daemon.  This is done with the
following command:

`hi daemon`

Once the daemon is running, you can use the 'hi' tool as usual using any
of the following commands:

`hi'
'hi info'
'hi watch'
'hi watch info'

#### Colors and Styles ####
Colors and styles can be applied to various parts of the *hi* display
output.  The ` config.ini ` file that comes with this tool provides some
examples.

Read more about the styles and colors that are available for use in ` colors.md `.


### Paths ###

##### checks_file #####
The 'checks_file' setting tells *hi* where YOUR custom 'checks.yml' file is located.  The checks file can be named anything,
as long as it is a properly formatted YAML file.  It should look something like the checks.yml or example.yml files that comes
with this tool.

##### log_file #####
The `log_file` is the location where 'hi' writes it's logging information.
The logs are in JSONL (JSON Lines) format, and so this file would
ideally be named with a .json extension.

You can create a sub-directory to store your logs within the 'hi' tool
directory, for example 'logs/', and have 'hi' write it's logs there.

For example
```
[Paths]
checks_file = config/checks.yml
log_file = logs/hi_log.json
```

The JSONL logging format was selected because it is easily parsable by 
upstream log analysis and monitoring tools, such as Logstash, Graylog, 
Zabbix, Splunk, and others.


### Report ###
##### header_style #####
The style of the hi tool report header ("HOST INFORMATION").

##### hostname_style #####
The style of the hi tool report hostname.

##### ip_style #####
The style of the hi tool report ip.


### Tables ###
##### number_of_columns #####
The 'number_of_columns' setting (default = 2) allows you to configure the
number of columns you would like rendered per table.  It is possible set
this to 7 or higher for extra-wide terminals. However I would suggested anywhere
between 2 and 5 for the best results.

##### default_style #####
Default style of the table background, which would be applied to everything
if no other styles below are defined.

##### header_style #####
Style of table headers.

##### border_style #####
Style of table borders.

##### column_style #####
Style of the column within a table.

##### text_style #####
Style of the text for status messages (within a column).


### OS Bar ###
##### os_text_style #####
Style of the text for the Operating System and End of Life bar.
This feature currently on supports Ubuntu operating systems at the moment.


### Logging ###
##### enable_logging #####
Set ` enable_logging = true ` if you want to enable logging.  This is set
to 'false' by default.  If you enable logging, be sure to configure the `log_file` variable under [Paths] as well.

#### config/groups.yml ####
*hi* "status groups" typically referred to simply as "groups" can be customized in the `  config/groups.yml  ` file, and only those system checks
configured with those specific groups defined will be reported.

The following is how the groups.yml file should be configured.  You can
either keep these same group names, or modify and rename them to whatever
you like.

` config/groups.yml ` example:
```
groups:
  - Security
  - Mount
  - Data
  - Communications
  - Media
  - Backup
  - Virtualization
  - Tools
```



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

After the system checks, two other pieces of system information are 
displayed.  The Operating System End-of-Life date, and a filesystem
utilization summary.  This section looks like the following:

![OS EOL and Filesystem Output](assets/Screenshot_20240708_014437-filesystem-os-eol.jpeg)

Groups can be customized in the config/groups.yml file, and only those system checks
configured with the groups defined will be reported.

Example of the groups.yml and checks.yml configuration files:
![Groups and Checks configuration](assets/Screenshot_20240707_133537-groups-and-checks-config.png)



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

For an example of a more complex check, take a look at the one defined for ExpressVPN:
```
   ExpressVPN:
     info: For general privacy and security.
     group: Security
     command: |
       expressvpn status | grep -i connected | sed "s/\\x1b\\[[0-9;]*[mGK]//g"
```
In the case of ExpressVPN, I'm not just interested in checking if the process is running, I'm also
interested in capturing a portion of the command output to be included in the reporting output of 'hi'.

In order to leverage that output, there is a custom handler defined in `host_information.py`:
```
         elif 'expressvpn' in process.lower():    
             if re.search("Connected", output.strip()):    
                 output_messages.append(f"[✅] {process} Status: {output.strip()}")    
             else:    
                 output_messages.append(f"[❌] {process} Status: {output.strip()}")
```

You can review all the existing checks defined in `config/checks.yml` for more examples.


#### hi watch
'hi' no longer uses the linux 'watch' command for continuous monitoring.
Instead a new, native watch command is available that retains the correct
output formatting in the terminal. 

To use the watch command, all you have to do now is run one of the
following commands:

`  hi watch   `
`  hi watch info  `

The command would monitor the output of 'hi' every 2 seconds, and update
your terminal output accordingly.


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
